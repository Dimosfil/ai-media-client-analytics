"""Execute production SQL against synthetic events, translating HogQL primitives.

This verifies relationships and arithmetic, not live HogQL resolver compatibility.
No second implementation of the report algorithms lives here.
"""
import json
import re
import sqlite3
from datetime import datetime


class ConditionalCount:
    def __init__(self): self.n=0
    def step(self,value): self.n+=int(bool(value))
    def finalize(self): return self.n


class ConditionalSum:
    def __init__(self): self.n=0
    def step(self,value,condition):
        if condition and value is not None: self.n+=value
    def finalize(self): return self.n


class Unique:
    def __init__(self): self.values=set()
    def step(self,value):
        if value is not None: self.values.add(value)
    def finalize(self): return len(self.values)


class ConditionalUnique(Unique):
    def step(self,value,condition):
        if condition: super().step(value)


class ArgMin:
    def __init__(self): self.key=None; self.value=None
    def step(self,value,key):
        if value is not None and key is not None and (self.key is None or key<self.key): self.key,self.value=key,value
    def finalize(self): return self.value


class AnyValue:
    def __init__(self): self.value=None
    def step(self,value):
        if self.value is None: self.value=value
    def finalize(self): return self.value


class ConditionalMin:
    def __init__(self): self.value=None
    def step(self,value,condition):
        if condition and value is not None and (self.value is None or value<self.value): self.value=value
    def finalize(self): return self.value


def to_float(value):
    try: return float(value)
    except (ValueError,TypeError): return None


def property_value(raw,path):
    if raw is None: return None
    value=json.loads(raw)
    for key in path.split('.'):
        if not isinstance(value,dict): return None
        value=value.get(key)
    if isinstance(value,(dict,list)): return json.dumps(value,sort_keys=True)
    return value


def json_value(raw,keys):
    if raw is None: return None
    value=json.loads(raw)
    for key in keys:
        if not isinstance(value,dict): return None
        value=value.get(key)
    return value


def translate(sql):
    sql=re.sub(r'length\(arrayFilter\(k -> NOT k IN \(([^)]*)\),JSONExtractKeys\(payload\)\)\)',
        lambda m:f"unknownKeys(payload,{json.dumps(m[1])})",sql)
    sql=re.sub(r'(?:(\w+)\.)?(properties|clicked_properties)((?:\.[A-Za-z_$][A-Za-z0-9_$]*)+)',
        lambda m:f"propertyValue({m[1]+'.' if m[1] else ''}{m[2]},'{m[3][1:]}')",sql)
    sql=re.sub(r"toString\((propertyValue\([^)]*,'selection_made'\))\)",r'booleanString(\1)',sql)
    # SQLite integer division differs from ClickHouse division.
    sql=sql.replace('/nullIf(', '*1.0/nullIf(')
    return sql


class SyntheticPostHog:
    def __init__(self,events=()):
        self.connection=sqlite3.connect(':memory:',check_same_thread=False)
        self.connection.row_factory=sqlite3.Row
        self.connection.execute('CREATE TABLE events(uuid TEXT,event TEXT,timestamp TEXT,distinct_id TEXT,properties TEXT)')
        for event in events:
            self.connection.execute('INSERT INTO events VALUES(?,?,?,?,?)',
                (event['uuid'],event['event'],event['timestamp'],event['distinct_id'],json.dumps(event['properties'])))
        for name,n,aggregate in [('countIf',1,ConditionalCount),('sumIf',2,ConditionalSum),('uniqExact',1,Unique),
                                 ('uniqExactIf',2,ConditionalUnique),('argMin',2,ArgMin),('any',1,AnyValue),('minIf',2,ConditionalMin)]:
            self.connection.create_aggregate(name,n,aggregate)
        for name,n,function in [('propertyValue',2,property_value),('toString',1,lambda v:None if v is None else str(v)),
            ('booleanString',1,lambda v:None if v is None else 'true' if v else 'false'),('toFloat',1,to_float),
            ('toDateTime',2,lambda v,z:v),('startsWith',2,lambda v,p:bool(v and v.startswith(p))),
            ('match',2,lambda v,p:bool(v is not None and re.search(p,str(v)))),
            ('dateDiff',3,lambda u,a,b:None if a is None or b is None else int((datetime.fromisoformat(b)-datetime.fromisoformat(a)).total_seconds()))]:
            self.connection.create_function(name,n,function)
        self.connection.create_function('JSONType',-1,lambda raw,*keys:
            'String' if isinstance(json_value(raw,keys),str) else 'Other')
        self.connection.create_function('JSONExtractString',-1,lambda raw,*keys:
            json_value(raw,keys) if isinstance(json_value(raw,keys),str) else '')
        self.connection.create_function('JSONExtractRaw',-1,lambda raw,*keys:
            '' if json_value(raw,keys) is None else json.dumps(json_value(raw,keys),separators=(',',':')))
        self.connection.create_function('unknownKeys',2,lambda raw,allowed:
            len(set(json.loads(raw))-set(re.findall(r"'([^']*)'",allowed))))
        self.timeout=45

    def query(self,sql):
        return [dict(row) for row in self.connection.execute(translate(sql)).fetchall()]

    def __del__(self):
        if hasattr(self,'connection'):
            self.connection.close()
