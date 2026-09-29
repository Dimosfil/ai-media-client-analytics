#!/usr/bin/env python3
"""Provider-neutral bridge from GI project memory to code-intelligence MCP tools."""

from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = Path("tools/project-memory/rag-system.json")
DEFAULT_PROTOCOL_VERSION = "2025-06-18"


class ConfigurationError(RuntimeError):
    """Raised when the project-local adapter contract is invalid."""


class McpError(RuntimeError):
    """Raised when an MCP subprocess cannot complete a request safely."""


def repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    try:
        output = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=current,
            stderr=subprocess.DEVNULL,
        )
        return Path(output.decode("utf-8", errors="replace").strip()).resolve()
    except (FileNotFoundError, subprocess.CalledProcessError):
        for path in [current, *current.parents]:
            if (path / ".git").exists():
                return path
        return current


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Missing configuration: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigurationError(f"Configuration root must be an object: {path}")
    return value


def resolve_config(root: Path, configured: str) -> Path:
    path = Path(configured)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def code_config(config: dict[str, Any]) -> dict[str, Any]:
    value = config.get("code_intelligence") or {}
    if not isinstance(value, dict):
        raise ConfigurationError("code_intelligence must be an object")
    return value


def validate_config(section: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not section:
        return ["code_intelligence section is missing"]
    if not isinstance(section.get("enabled", False), bool):
        errors.append("code_intelligence.enabled must be boolean")
    if not section.get("enabled", False):
        return errors
    if not str(section.get("provider") or "").strip():
        errors.append("code_intelligence.provider is required when enabled")
    transport = section.get("transport") or {}
    if not isinstance(transport, dict):
        errors.append("code_intelligence.transport must be an object")
        return errors
    if transport.get("kind") != "mcp-stdio":
        errors.append("only transport.kind=mcp-stdio is supported")
    if not str(transport.get("command") or "").strip():
        errors.append("code_intelligence.transport.command is required when enabled")
    if not isinstance(transport.get("args", []), list):
        errors.append("code_intelligence.transport.args must be an array")
    if not isinstance(transport.get("environment_variables", []), list):
        errors.append("transport.environment_variables must be an array of names")
    if "env" in transport or "environment" in transport:
        errors.append("inline environment values are forbidden; use environment_variables names")
    allowed = section.get("allowed_tools") or []
    if not isinstance(allowed, list) or not allowed:
        errors.append("code_intelligence.allowed_tools must be a non-empty array")
    capabilities = section.get("capabilities") or {}
    if not isinstance(capabilities, dict):
        errors.append("code_intelligence.capabilities must be an object")
    elif any(not isinstance(value, dict) for value in capabilities.values()):
        errors.append("every code_intelligence capability must be an object")
    return errors


def resolve_project_path(root: Path, section: dict[str, Any]) -> Path:
    raw = str(section.get("project_path") or ".")
    path = Path(raw)
    resolved = path.resolve() if path.is_absolute() else (root / path).resolve()
    if not section.get("allow_external_project_path", False):
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ConfigurationError(
                "code_intelligence.project_path leaves the repository; "
                "set allow_external_project_path only in explicit local test configuration"
            ) from exc
    return resolved


def render_args(values: list[Any], project_path: Path) -> list[str]:
    return [str(value).replace("{project_path}", str(project_path)) for value in values]


def git_state(project_path: Path) -> dict[str, Any]:
    state: dict[str, Any] = {"head": "", "dirty": None}
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=project_path, stderr=subprocess.DEVNULL
        )
        state["head"] = head.decode("utf-8", errors="replace").strip()
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=project_path, stderr=subprocess.DEVNULL
        )
        state["dirty"] = bool(status.strip())
    except (FileNotFoundError, subprocess.CalledProcessError):
        state["warning"] = "project_path is not a readable Git worktree"
    return state


def assess_freshness(
    section: dict[str, Any], provider_meta: dict[str, Any], local_state: dict[str, Any]
) -> dict[str, Any]:
    policy = section.get("freshness") or {}
    indexed = str(provider_meta.get("indexed_commit") or "")
    provider_head = str(provider_meta.get("live_head") or "")
    local_head = str(local_state.get("head") or "")
    stale_warning = str(provider_meta.get("stale_warning") or "").strip()
    warnings: list[str] = []
    stale = False
    comparable_head = local_head or provider_head
    commits_match = bool(
        indexed
        and comparable_head
        and (indexed.startswith(comparable_head) or comparable_head.startswith(indexed))
    )
    if indexed and comparable_head and not commits_match:
        stale = True
        warnings.append("provider index commit differs from the current Git HEAD")
    if stale_warning:
        stale = True
        warnings.append(stale_warning)
    if policy.get("require_indexed_commit", False) and not indexed:
        stale = True
        warnings.append("provider did not report indexed_commit")
    if policy.get("warn_on_dirty_worktree", True) and local_state.get("dirty") is True:
        warnings.append("worktree has uncommitted changes that may be absent from the provider index")
    return {
        "indexed_commit": indexed,
        "provider_live_head": provider_head,
        "local_head": local_head,
        "dirty_worktree": local_state.get("dirty"),
        "stale": stale,
        "warnings": warnings,
    }


def extract_provider_meta(result: dict[str, Any]) -> dict[str, Any]:
    meta = result.get("_meta")
    if isinstance(meta, dict):
        return meta
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        if isinstance(structured.get("_meta"), dict):
            return structured["_meta"]
        nested = structured.get("result")
        if isinstance(nested, dict) and isinstance(nested.get("_meta"), dict):
            return nested["_meta"]
    return {}


class McpStdioClient:
    def __init__(self, command: list[str], cwd: Path, env: dict[str, str], timeout: float) -> None:
        self.command = command
        self.cwd = cwd
        self.timeout = timeout
        self._next_id = 1
        self._messages: queue.Queue[dict[str, Any]] = queue.Queue()
        self._stderr: list[str] = []
        try:
            self.process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except (FileNotFoundError, OSError) as exc:
            raise McpError(f"Could not start provider command {command[0]!r}: {exc}") from exc
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()

    def _read_stdout(self) -> None:
        assert self.process.stdout is not None
        for line in self.process.stdout:
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(message, dict):
                self._messages.put(message)

    def _read_stderr(self) -> None:
        assert self.process.stderr is not None
        for line in self.process.stderr:
            self._stderr.append(line.rstrip())
            if len(self._stderr) > 40:
                del self._stderr[:10]

    def _send(self, message: dict[str, Any]) -> None:
        if self.process.poll() is not None:
            detail = self._stderr[-1] if self._stderr else f"exit={self.process.returncode}"
            raise McpError(f"Provider process exited before request: {detail}")
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
        self.process.stdin.flush()

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        self._send(
            {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}
        )
        deadline = time.monotonic() + self.timeout
        deferred: list[dict[str, Any]] = []
        try:
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    detail = self._stderr[-1] if self._stderr else "no provider error output"
                    raise McpError(f"Timed out waiting for {method}: {detail}")
                try:
                    response = self._messages.get(timeout=min(remaining, 0.25))
                except queue.Empty:
                    if self.process.poll() is not None:
                        detail = self._stderr[-1] if self._stderr else f"exit={self.process.returncode}"
                        raise McpError(f"Provider exited while waiting for {method}: {detail}")
                    continue
                if response.get("id") != request_id:
                    deferred.append(response)
                    continue
                if "error" in response:
                    raise McpError(f"MCP {method} failed: {response['error']}")
                result = response.get("result")
                return result if isinstance(result, dict) else {"value": result}
        finally:
            for item in deferred:
                self._messages.put(item)

    def initialize(self, protocol_version: str) -> dict[str, Any]:
        result = self.request(
            "initialize",
            {
                "protocolVersion": protocol_version,
                "capabilities": {},
                "clientInfo": {"name": "gi-code-intelligence", "version": "1"},
            },
        )
        self.notify("notifications/initialized")
        return result

    def close(self) -> None:
        if self.process.poll() is not None:
            return
        if self.process.stdin:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)

    def __enter__(self) -> "McpStdioClient":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


def create_client(root: Path, section: dict[str, Any]) -> tuple[McpStdioClient, Path]:
    project_path = resolve_project_path(root, section)
    transport = section.get("transport") or {}
    command_name = str(transport.get("command") or "")
    args = render_args(transport.get("args") or [], project_path)
    forwarded = transport.get("environment_variables") or []
    system_names = {
        "PATH",
        "PATHEXT",
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "TEMP",
        "TMP",
        "TMPDIR",
        "HOME",
        "USERPROFILE",
        "LOCALAPPDATA",
        "APPDATA",
        "LANG",
        "LC_ALL",
    }
    env = {key: value for key, value in os.environ.items() if key.upper() in system_names}
    for name in forwarded:
        key = str(name)
        if key not in os.environ:
            raise ConfigurationError(f"Required environment variable is not set: {key}")
        env[key] = os.environ[key]
    timeout = float((section.get("timeouts") or {}).get("request_seconds") or 30)
    return McpStdioClient([command_name, *args], project_path, env, timeout), project_path


def configured_route(section: dict[str, Any], query: str) -> dict[str, Any]:
    routing = section.get("routing") or {}
    routes = routing.get("routes") or []
    lowered = query.casefold()
    scores: dict[str, int] = {}
    sources: dict[str, list[str]] = {}
    for route in routes:
        if not isinstance(route, dict):
            continue
        route_id = str(route.get("id") or "").strip()
        if not route_id:
            continue
        terms = [str(term).casefold() for term in route.get("terms") or []]
        extensions = [str(item).casefold() for item in route.get("path_extensions") or []]
        score = sum(1 for term in terms if term and term in lowered)
        score += sum(2 for extension in extensions if extension and extension in lowered)
        scores[route_id] = score
        sources[route_id] = [str(item) for item in route.get("sources") or []]
    matched = [route_id for route_id, score in scores.items() if score > 0]
    if len(matched) > 1:
        decision = str(routing.get("combined_route") or "federated")
        selected_sources = sorted({source for route_id in matched for source in sources[route_id]})
    elif matched:
        decision = matched[0]
        selected_sources = sources[decision]
    else:
        decision = str(routing.get("default_route") or "project_memory")
        selected_sources = sources.get(decision, ["project_memory"])
    fallback = False
    reason = "configured routing indicators"
    if not section.get("enabled", False) and "code_intelligence" in selected_sources:
        fallback = True
        selected_sources = [str(item) for item in routing.get("fallback_sources") or ["project_memory"]]
        decision = "project_memory" if selected_sources == ["project_memory"] else "fallback"
        reason = "code intelligence is disabled; using configured fallback sources"
    return {
        "route": decision,
        "sources": selected_sources,
        "scores": scores,
        "fallback": fallback,
        "reason": reason,
    }


def provider_session(root: Path, section: dict[str, Any]) -> tuple[McpStdioClient, Path, dict[str, Any]]:
    client, project_path = create_client(root, section)
    try:
        initialized = client.initialize(
            str((section.get("transport") or {}).get("protocol_version") or DEFAULT_PROTOCOL_VERSION)
        )
    except Exception:
        client.close()
        raise
    return client, project_path, initialized


def run_status(args: argparse.Namespace) -> int:
    root = repo_root()
    config = load_json(resolve_config(root, args.config))
    section = code_config(config)
    errors = validate_config(section)
    if errors:
        print_json({"ok": False, "enabled": bool(section.get("enabled")), "errors": errors})
        return 1
    if not section.get("enabled", False):
        print_json({"ok": True, "enabled": False, "provider": section.get("provider", "")})
        return 0
    client, project_path, initialized = provider_session(root, section)
    try:
        listing = client.request("tools/list")
    finally:
        client.close()
    available = sorted(
        str(tool.get("name"))
        for tool in listing.get("tools", [])
        if isinstance(tool, dict) and tool.get("name")
    )
    allowed = sorted(str(item) for item in section.get("allowed_tools") or [])
    missing = sorted(set(allowed) - set(available))
    output = {
        "ok": not missing,
        "enabled": True,
        "provider": section.get("provider"),
        "project_path": str(project_path),
        "server": initialized.get("serverInfo") or {},
        "allowed_tools": allowed,
        "available_tools": available,
        "missing_allowed_tools": missing,
        "git": git_state(project_path),
    }
    print_json(output)
    return 0 if output["ok"] else 1


def run_route(args: argparse.Namespace) -> int:
    root = repo_root()
    config = load_json(resolve_config(root, args.config))
    print_json(configured_route(code_config(config), args.query))
    return 0


def run_call(args: argparse.Namespace) -> int:
    root = repo_root()
    config = load_json(resolve_config(root, args.config))
    section = code_config(config)
    errors = validate_config(section)
    if errors:
        raise ConfigurationError("; ".join(errors))
    if not section.get("enabled", False):
        raise ConfigurationError("code intelligence is disabled")
    allowed = {str(item) for item in section.get("allowed_tools") or []}
    if args.tool not in allowed:
        raise ConfigurationError(f"Tool is not allowlisted: {args.tool}")
    try:
        arguments = json.loads(args.arguments)
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"--arguments must be a JSON object: {exc}") from exc
    if not isinstance(arguments, dict):
        raise ConfigurationError("--arguments must be a JSON object")
    client, project_path, _initialized = provider_session(root, section)
    try:
        result = client.request("tools/call", {"name": args.tool, "arguments": arguments})
    finally:
        client.close()
    freshness = assess_freshness(section, extract_provider_meta(result), git_state(project_path))
    rejected = bool(freshness["stale"] and (section.get("freshness") or {}).get("reject_stale", False))
    envelope = {
        "ok": not rejected and not bool(result.get("isError")),
        "provider": section.get("provider"),
        "tool": args.tool,
        "freshness": freshness,
        "result": result,
    }
    print_json(envelope)
    return 0 if envelope["ok"] else 2


def run_invoke(args: argparse.Namespace) -> int:
    root = repo_root()
    config = load_json(resolve_config(root, args.config))
    section = code_config(config)
    capability = (section.get("capabilities") or {}).get(args.capability)
    if not isinstance(capability, dict):
        raise ConfigurationError(f"Unknown capability: {args.capability}")
    tool = str(capability.get("tool") or "")
    argument = str(capability.get("argument") or "target")
    value: Any = args.value
    if capability.get("argument_type") == "array":
        value = [args.value]
    forwarded = argparse.Namespace(config=args.config, tool=tool, arguments=json.dumps({argument: value}))
    return run_call(forwarded)


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="Path to rag-system.json")
    sub = parser.add_subparsers(dest="command")
    status = sub.add_parser("status", help="Validate config and list provider tools")
    status.set_defaults(func=run_status)
    route = sub.add_parser("route", help="Route a question using configured indicators")
    route.add_argument("query")
    route.set_defaults(func=run_route)
    call = sub.add_parser("call", help="Call one allowlisted MCP tool")
    call.add_argument("tool")
    call.add_argument("--arguments", default="{}")
    call.set_defaults(func=run_call)
    invoke = sub.add_parser("invoke", help="Invoke a configured provider-neutral capability")
    invoke.add_argument("capability")
    invoke.add_argument("value")
    invoke.set_defaults(func=run_invoke)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    try:
        return int(args.func(args))
    except (ConfigurationError, McpError) as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
