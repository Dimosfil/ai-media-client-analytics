#!/usr/bin/env python3
"""Pinned, operator-run PostHog hobby deployment helpers (Python 3.12+)."""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VERSION = (ROOT / "POSTHOG_VERSION").read_text(encoding="utf-8").strip()
CONFIG_FILES = [".env", "docker-compose.security.yml", "docker-compose.images.json",
                "docker-compose.poc.yml", "image-lock.json"]
UPSTREAM_FILES = (("docker-compose.base.yml", "docker-compose.base.yml"),
                  ("docker-compose.hobby.yml", "docker-compose.yml"),
                  (".env.services", ".env.services"))
COMPOSE_BASE = ["docker", "compose", "-f", "docker-compose.yml", "-f", "docker-compose.security.yml"]
COMPOSE_LOCKED = COMPOSE_BASE + ["-f", "docker-compose.images.json"]
COMPOSE_POC = COMPOSE_LOCKED + ["-f", "docker-compose.poc.yml"]
POC_SERVICES = ["proxy", "capture", "ingestion-general", "plugins", "feature-flags"]


def fail(message):
    raise RuntimeError(message)


def run(*args, capture=False, check=True):
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.PIPE if capture else None, check=False)
    if check and result.returncode:
        detail = (result.stderr or "").strip() if capture else ""
        fail(f"Command failed: {args[0]} {args[1] if len(args) > 1 else ''} {detail}")
    return result.stdout if capture else result.returncode


def require_command(name):
    if shutil.which(name) is None:
        fail(f"Required command missing: {name}")


def git_in_checkout(*args, capture=False, check=True):
    # A root-run backup must still be able to verify a checkout owned by the deploy user.
    return run("git", "-c", f"safe.directory={ROOT / 'posthog'}", "-C", "posthog", *args,
               capture=capture, check=check)


def upstream_file_bytes(source):
    result = subprocess.run(["git", "-c", f"safe.directory={ROOT / 'posthog'}", "-C", "posthog",
                             "show", f"{VERSION}:{source}"], cwd=ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode:
        fail(f"Cannot read {source} from pinned upstream commit: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def env_values():
    path = ROOT / ".env"
    if not path.exists():
        fail("Missing .env. Run init or restore first.")
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key] = value
    return values


def validate_env():
    if not re.fullmatch(r"[0-9a-f]{40}", VERSION):
        fail("POSTHOG_VERSION must contain an exact 40-character commit SHA")
    values = env_values()
    if values.get("POSTHOG_APP_TAG") != VERSION:
        fail("POSTHOG_APP_TAG must match POSTHOG_VERSION")
    if values.get("COMPOSE_PROJECT_NAME") != "ai-media-analytics":
        fail("COMPOSE_PROJECT_NAME must be ai-media-analytics")
    domain = values.get("DOMAIN", "")
    if not re.fullmatch(r"(?=.{4,253}$)[a-z0-9-]+(?:\.[a-z0-9-]+)+", domain) or "example.com" in domain:
        fail("Set DOMAIN to your real DNS name")
    if values.get("CADDY_HOST") != domain:
        fail("CADDY_HOST must match DOMAIN for upstream Caddyfile interpolation")
    for key in ("POSTHOG_SECRET", "ENCRYPTION_SALT_KEYS", "BROWSERLESS_SECRET"):
        if len(values.get(key, "")) < 32 or "GENERATED" in values.get(key, ""):
            fail(f"Missing generated value: {key}")
    return values


def init(args):
    if (ROOT / ".env").exists():
        fail(".env already exists; secrets are never regenerated automatically")
    domain = args.domain.lower().strip()
    if not re.fullmatch(r"(?=.{4,253}$)[a-z0-9-]+(?:\.[a-z0-9-]+)+", domain) or "example.com" in domain:
        fail("Provide a real DNS domain, e.g. analytics.your-domain.net")
    values = {
        "COMPOSE_PROJECT_NAME": "ai-media-analytics", "DOMAIN": domain, "CADDY_HOST": domain,
        "REGISTRY_URL": "posthog/posthog", "POSTHOG_APP_TAG": VERSION,
        "TLS_BLOCK": "",
        "POSTHOG_SECRET": secrets.token_hex(32),
        "ENCRYPTION_SALT_KEYS": secrets.token_hex(16),
        "BROWSERLESS_SECRET": secrets.token_hex(32),
        "OPT_OUT_CAPTURE": "true",
    }
    path = ROOT / ".env"
    with path.open("x", encoding="utf-8") as stream:
        for key, value in values.items():
            stream.write(f"{key}={value}\n")
    path.chmod(0o600)
    print("Created .env with generated secrets. Keep it private and back it up securely.")


def ensure_checkout():
    require_command("git")
    target = ROOT / "posthog"
    created = not target.exists()
    if created:
        run("git", "clone", "--filter=blob:none", "--no-checkout", "https://github.com/PostHog/posthog.git", "posthog")
    if not (target / ".git").is_dir():
        fail("posthog/ exists but is not a Git checkout")
    if created:
        # --no-checkout still leaves HEAD at the remote default branch.
        git_in_checkout("fetch", "origin", VERSION)
        git_in_checkout("checkout", "--detach", VERSION)
    actual = git_in_checkout("rev-parse", "HEAD", capture=True, check=False).strip()
    if not actual:
        git_in_checkout("fetch", "origin", VERSION)
        git_in_checkout("checkout", "--detach", VERSION)
        actual = git_in_checkout("rev-parse", "HEAD", capture=True).strip()
    if actual != VERSION:
        fail(f"Upstream checkout is {actual}; expected {VERSION}. Review and prepare in a clean directory.")
    if git_in_checkout("status", "--porcelain", capture=True).strip():
        fail("Upstream checkout contains local changes")


def verify_upstream_files():
    ensure_checkout()
    for source, destination in UPSTREAM_FILES:
        source_path = ROOT / "posthog" / source
        dest_path = ROOT / destination
        if not source_path.is_file():
            fail(f"Missing pinned upstream file: {source}")
        if dest_path.exists() and dest_path.read_bytes() != upstream_file_bytes(source):
            fail(f"{destination} differs from pinned upstream; stop and review")


def download_geoip():
    share = ROOT / "share"
    share.mkdir(exist_ok=True)
    target = share / "GeoLite2-City.mmdb"
    if target.exists() and target.stat().st_size:
        return
    require_command("curl")
    require_command("brotli")
    temp = target.with_suffix(".tmp")
    with temp.open("wb") as output:
        curl = subprocess.Popen(["curl", "-fsSL", "--http1.1", "https://mmdbcdn.posthog.net/"], stdout=subprocess.PIPE)
        brotli = subprocess.run(["brotli", "--decompress"], stdin=curl.stdout, stdout=output, check=False)
        curl.stdout.close()
        curl_result = curl.wait()
    if curl_result or brotli.returncode or not temp.stat().st_size:
        temp.unlink(missing_ok=True)
        fail("GeoIP download/decompression failed")
    temp.replace(target)
    (share / "GeoLite2-City.json").write_text(json.dumps({"date": dt.date.today().isoformat()}), encoding="utf-8")


def prepare(_args):
    validate_env()
    verify_upstream_files()
    for source, destination in UPSTREAM_FILES:
        dest_path = ROOT / destination
        dest_path.write_bytes(upstream_file_bytes(source))
    compose = ROOT / "compose"
    compose.mkdir(exist_ok=True)
    (compose / "start").write_text("#!/bin/sh\n/compose/wait\n./bin/migrate\n./bin/docker-server\n", encoding="utf-8")
    (compose / "temporal-django-worker").write_text("#!/bin/sh\n./bin/temporal-django-worker\n", encoding="utf-8")
    (compose / "wait").write_text(
        "#!/usr/bin/env python3\nimport socket,time\n"
        "while True:\n"
        "    try:\n"
        "        for host,port in [('clickhouse',9000),('db',5432)]:\n"
        "            with socket.create_connection((host,port),timeout=5): pass\n"
        "        break\n"
        "    except OSError: time.sleep(5)\n", encoding="utf-8")
    for path in compose.iterdir():
        path.chmod(0o755)
    download_geoip()
    print(f"Prepared upstream PostHog at {VERSION}. No containers were started.")


def compose_config(files):
    return json.loads(run(*(files + ["config", "--format", "json"]), capture=True))


def canonical_repository(reference):
    repository = reference.split("@", 1)[0]
    if ":" in repository.rsplit("/", 1)[-1]:
        repository = repository.rsplit(":", 1)[0]
    parts = repository.split("/")
    if "." not in parts[0] and ":" not in parts[0] and parts[0] != "localhost":
        repository = "docker.io/" + repository
    if repository.startswith("docker.io/") and repository.count("/") == 1:
        repository = repository.replace("docker.io/", "docker.io/library/", 1)
    return repository


def validate_config(config, manifest, domain):
    services = config["services"]
    if set(services) != set(manifest["source_images"]) or set(services) != set(manifest["service_digests"]):
        fail("Image lock service set differs from Compose")
    for name, service in services.items():
        if name != "proxy" and service.get("ports"):
            fail(f"Unexpected published host port on {name}")
        if service.get("build"):
            fail(f"Build remains enabled on {name}")
        digest = manifest["service_digests"][name]
        if service.get("image") != digest or not re.fullmatch(r"[^@]+@sha256:[0-9a-f]{64}", digest):
            fail(f"Missing or mismatched image digest for {name}")
        if canonical_repository(digest) != canonical_repository(manifest["source_images"][name]):
            fail(f"Digest repository differs from source image on {name}")
        if service.get("pull_policy") != "never":
            fail(f"Pull policy is not never on {name}")
        if any(mount.get("type") == "volume" and not mount.get("source") for mount in service.get("volumes", [])):
            fail(f"Anonymous volume remains on {name}")
    proxy_ports = services["proxy"].get("ports", [])
    if len(proxy_ports) != 2 or {(str(p.get("published")), int(p.get("target")), p.get("protocol", "tcp")) for p in proxy_ports} != {
            ("80", 80, "tcp"), ("443", 443, "tcp")} or any(p.get("host_ip") not in (None, "0.0.0.0", "::") for p in proxy_ports):
        fail(f"Unexpected proxy port mapping: {proxy_ports}")
    if services["proxy"].get("environment", {}).get("CADDY_HOST") != domain:
        fail("Caddy host must be the exact DOMAIN")
    db_mounts = {v["target"]: v["source"] for v in services["db"].get("volumes", [])}
    for target, path in (("/docker-entrypoint-initdb.d", ROOT / "posthog/docker/postgres-init-scripts"),
                         ("/products", ROOT / "posthog/products")):
        if Path(db_mounts.get(target, "")).resolve() != path.resolve() or not path.is_dir():
            fail(f"Missing pinned bind mount for db: {target}")


def security_overlay(raw):
    lines = ["# Generated for the pinned PostHog Compose. Do not edit upstream snapshots.",
             "services:", "  proxy:", "    environment:", "      CADDY_HOST: ${DOMAIN}",
             "      CADDY_EXTRA_CONFIG: ${CADDY_EXTRA_CONFIG:-}",
             "    volumes:", "      - caddy-legacy-data:/root/.caddy"]
    for name, service in sorted(raw["services"].items()):
        if name == "proxy":
            continue
        changes = []
        if service.get("ports"):
            changes.append("    ports: !reset []")
        if service.get("build"):
            changes.append("    build: !reset null")
        if name == "web":
            changes.extend(["    environment:", "      OIDC_RSA_PRIVATE_KEY: ${OIDC_RSA_PRIVATE_KEY:-}"])
        if name == "db":
            changes.extend(["    volumes:",
                            "      - ./posthog/docker/postgres-init-scripts:/docker-entrypoint-initdb.d:ro",
                            "      - ./posthog/products:/products:ro"])
        if name == "elasticsearch":
            changes.extend(["    volumes:", "      - elasticsearch-data:/var/lib/elasticsearch/data"])
        if changes:
            lines.extend([f"  {name}:", *changes])
    lines.extend(["volumes:", "  caddy-legacy-data:", "  elasticsearch-data:"])
    return "\n".join(lines) + "\n"


def lock_images(_args):
    validate_env()
    require_command("docker")
    verify_upstream_files()
    if (ROOT / "image-lock.json").exists() or (ROOT / "docker-compose.images.json").exists():
        fail("Image lock already exists; do not refresh it implicitly")
    raw = compose_config(["docker", "compose", "-f", "docker-compose.yml"])
    security_text = security_overlay(raw)
    security_path = ROOT / "docker-compose.security.yml"
    if security_path.exists() and security_path.read_text(encoding="utf-8") != security_text:
        fail("Existing security overlay differs from pinned Compose; review it before locking")
    security_path.write_text(security_text, encoding="utf-8")
    secured = compose_config(COMPOSE_BASE)
    images = {}
    for name, service in sorted(secured["services"].items()):
        reference = service.get("image")
        if not reference:
            fail(f"Service {name} has no image; review this upstream version")
        images[name] = reference
    digests = {}
    for reference in sorted(set(images.values())):
        print(f"Pulling and locking {reference}", flush=True)
        run("docker", "pull", reference)
        inspected = json.loads(run("docker", "image", "inspect", reference, capture=True))[0]
        repo_digests = inspected.get("RepoDigests") or []
        matching = [digest for digest in repo_digests if canonical_repository(digest) == canonical_repository(reference)]
        if len(matching) != 1:
            fail(f"Expected one registry digest for {reference}, found {len(matching)}")
        digests[reference] = matching[0]
    service_digests = {name: digests[reference] for name, reference in images.items()}
    overlay = {"services": {name: {"image": digest, "pull_policy": "never"} for name, digest in service_digests.items()}}
    (ROOT / "docker-compose.images.json").write_text(json.dumps(overlay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {"posthog_commit": VERSION, "source_images": images, "service_digests": service_digests}
    (ROOT / "image-lock.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    check(None)
    print("Images locked by registry digest. Commit both generated lock files in your new repository.")


def check(_args):
    values = validate_env()
    verify_upstream_files()
    for filename in ("docker-compose.security.yml", "docker-compose.images.json", "image-lock.json"):
        if not (ROOT / filename).is_file():
            fail(f"Missing {filename}; run lock-images on the Linux Docker host")
    manifest = json.loads((ROOT / "image-lock.json").read_text(encoding="utf-8"))
    if manifest.get("posthog_commit") != VERSION:
        fail("Image lock version does not match POSTHOG_VERSION")
    raw = compose_config(["docker", "compose", "-f", "docker-compose.yml"])
    if (ROOT / "docker-compose.security.yml").read_text(encoding="utf-8") != security_overlay(raw):
        fail("Security overlay differs from generated pinned policy")
    source_config = compose_config(COMPOSE_BASE)
    for name, service in source_config["services"].items():
        if service.get("image") != manifest["source_images"].get(name):
            fail(f"Source image changed after lock on {name}")
    config = compose_config(COMPOSE_LOCKED)
    validate_config(config, manifest, values["DOMAIN"])
    print(f"Configuration OK: {len(config['services'])} digest-locked services; only proxy publishes 80/443.")


def up(_args):
    check(None)
    # A fresh restore host needs the pinned digests; missing pulls cannot advance a tag.
    run(*(COMPOSE_LOCKED + ["up", "-d", "--no-build", "--pull", "missing"]))
    run(*(COMPOSE_LOCKED + ["ps"]))


def check_poc(_args):
    check(None)
    values = validate_env()
    manifest = json.loads((ROOT / "image-lock.json").read_text(encoding="utf-8"))
    config = compose_config(COMPOSE_POC)
    validate_config(config, manifest, values["DOMAIN"])
    if config["services"]["web"].get("environment", {}).get("GRANIAN_WORKERS") != "1":
        fail("POC web must run one Granian worker")
    command = config["services"]["kafka"].get("command", [])
    if not {"--smp 1", "--memory 1G", "--reserve-memory 256M"} <= set(command):
        fail("POC Redpanda limits differ from the tested configuration")
    print("POC configuration OK: digest-locked images, one web worker, only proxy publishes 80/443.")


def up_poc(_args):
    check_poc(None)
    allowed = poc_service_names(compose_config(COMPOSE_POC))
    running = set(run(*(COMPOSE_LOCKED + ["ps", "--status", "running", "--services"]),
                      capture=True).splitlines())
    extra = sorted(running - allowed)
    if extra:
        run(*(COMPOSE_LOCKED + ["stop", "--timeout", "30", *extra]))
    run(*(COMPOSE_POC + ["up", "-d", "--no-build", "--pull", "never", *POC_SERVICES]))
    run(*(COMPOSE_POC + ["ps"]))


def smoke(_args):
    values = validate_env()
    project_key = os.environ.get("POSTHOG_PROJECT_KEY", "")
    if not project_key:
        fail("Set POSTHOG_PROJECT_KEY in the current shell; never store it in .env")
    event_id = str(uuid.uuid4())
    distinct_id = f"smoke:{event_id}"
    payload = json.dumps({
        "api_key": project_key, "event": "analytics_smoke", "distinct_id": distinct_id,
        "uuid": event_id, "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
        "properties": {"source": "ai-media-analytics-bundle", "schema_version": 1},
    }).encode("utf-8")
    request = urllib.request.Request(f"https://{values['DOMAIN']}/capture/", data=payload,
                                     headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 201, 202):
            fail(f"Capture returned HTTP {response.status}")
    print(f"Capture accepted. event_id={event_id}; waiting for ClickHouse...", flush=True)
    query = f"SELECT count() FROM posthog.events WHERE event = 'analytics_smoke' AND distinct_id = '{distinct_id}'"
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        result = run(*(COMPOSE_LOCKED + ["exec", "-T", "clickhouse", "clickhouse-client", "--query", query]), capture=True, check=False)
        if result.strip().isdigit() and int(result.strip()) >= 1:
            print(f"ClickHouse confirmed {event_id}. Confirm it in PostHog Live events too.")
            return
        time.sleep(5)
    fail(f"Event {event_id} did not appear in ClickHouse within 180 seconds; inspect ingestion containers")


def volume_names():
    result = run("docker", "volume", "ls", "--filter", "label=com.docker.compose.project=ai-media-analytics",
                 "--format", "{{.Name}}", capture=True)
    return sorted(name for name in result.splitlines() if name)


def all_volume_names():
    result = run("docker", "volume", "ls", "--format", "{{.Name}}", capture=True)
    return set(result.splitlines())


def poc_service_names(config):
    selected = set(POC_SERVICES)
    pending = list(selected)
    while pending:
        name = pending.pop()
        for dependency in config["services"][name].get("depends_on", {}):
            if dependency not in selected:
                selected.add(dependency)
                pending.append(dependency)
    return selected


def expected_volume_names(poc=False):
    config = compose_config(COMPOSE_POC if poc else COMPOSE_LOCKED)
    if any(mount.get("type") == "volume" and not mount.get("source")
           for service in config["services"].values() for mount in service.get("volumes", [])):
        fail("Anonymous volume cannot be backed up safely")
    selected = poc_service_names(config) if poc else set(config["services"])
    names = {config["volumes"][mount["source"]]["name"] for name in selected
             for mount in config["services"][name].get("volumes", []) if mount.get("type") == "volume"}
    return names


def volume_path(name):
    value = json.loads(run("docker", "volume", "inspect", name, capture=True))[0]
    path = Path(value["Mountpoint"])
    if not path.is_dir():
        fail(f"Volume mountpoint unavailable: {name}")
    return path


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def backup(args):
    poc = args.poc
    check_poc(None) if poc else check(None)
    compose = COMPOSE_POC if poc else COMPOSE_LOCKED
    start = compose + ["up", "-d", "--no-build", "--pull", "never"] + (POC_SERVICES if poc else [])
    if sys.platform != "linux" or os.geteuid() != 0:
        fail("Cold volume backup requires root on the Linux Docker host")
    destination = Path(args.directory).resolve()
    if destination.exists():
        fail("Backup destination already exists")
    volumes = volume_names()
    if any(not name.startswith("ai-media-analytics_") for name in volumes):
        fail("Project-labelled anonymous or foreign volume found; inspect it before backup")
    missing = expected_volume_names(poc) - set(volumes)
    if not volumes or missing:
        fail(f"Compose volumes missing before backup: {sorted(missing)}")
    running = set(run(*(compose + ["ps", "--status", "running", "--services"]), capture=True).splitlines())
    if not {"web", "proxy", "db", "clickhouse"} <= running:
        fail("Core services are not running; refusing cold backup of an uncertain stack state")
    destination.mkdir(parents=True, mode=0o700)
    destination.chmod(0o700)
    (destination / "INCOMPLETE").write_text("Backup has not completed and must not be restored.\n", encoding="utf-8")
    backup_error = None
    try:
        run(*(COMPOSE_LOCKED + ["stop", "--timeout", "120"]))
        config = destination / "config"
        config.mkdir(mode=0o700)
        for filename in CONFIG_FILES + ["POSTHOG_VERSION"]:
            shutil.copy2(ROOT / filename, config / filename)
        volume_metadata = {}
        for name in volumes:
            target = destination / f"{name}.tar"
            with tarfile.open(target, "w") as archive:
                archive.add(volume_path(name), arcname=".")
            target.chmod(0o600)
            volume_metadata[name] = {"filename": target.name, "sha256": sha256(target)}
        manifest = {"posthog_commit": VERSION, "deployment_mode": "poc" if poc else "full",
                    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "volumes": volume_metadata,
                    "config_sha256": {name: sha256(config / name) for name in CONFIG_FILES + ["POSTHOG_VERSION"]}}
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (destination / "INCOMPLETE").unlink()
    except Exception as error:
        backup_error = error
    finally:
        restart_code = run(*start, check=False)
    if restart_code:
        fail(f"Stack restart failed after backup (exit {restart_code}); inspect containers immediately. Backup: {destination}")
    if backup_error:
        raise backup_error
    print(f"Cold backup complete: {destination}. Encrypt and move it off-host; rehearse restore.")


def restore(args):
    if sys.platform != "linux" or os.geteuid() != 0:
        fail("Volume restore requires root on the Linux Docker host to preserve ownership")
    source = Path(args.directory).resolve()
    if (source / "INCOMPLETE").exists():
        fail("Backup is marked incomplete")
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    mode = manifest.get("deployment_mode", "full")
    if mode not in ("full", "poc"):
        fail("Unknown backup deployment mode")
    if manifest.get("posthog_commit") != VERSION:
        fail("Backup version differs from this bundle")
    if not manifest.get("volumes"):
        fail("Backup manifest contains no volumes")
    if set(manifest.get("config_sha256", {})) != set(CONFIG_FILES + ["POSTHOG_VERSION"]):
        fail("Backup configuration file set is incomplete or unexpected")
    for name, expected in manifest["config_sha256"].items():
        if sha256(source / "config" / name) != expected:
            fail(f"Configuration checksum mismatch: {name}")
    for name, item in manifest["volumes"].items():
        filename = item["filename"]
        if (not re.fullmatch(r"ai-media-analytics_[a-zA-Z0-9_.-]+", name)
                or filename != f"{name}.tar" or sha256(source / filename) != item["sha256"]):
            fail(f"Volume checksum/name invalid: {name}")
    existing = run("docker", "ps", "-a", "--filter", "label=com.docker.compose.project=ai-media-analytics",
                   "--format", "{{.ID}}", capture=True)
    if existing.strip():
        fail("Restore requires a fresh project with no containers; no data was overwritten")
    existing_volumes = all_volume_names() & set(manifest["volumes"])
    if existing_volumes:
        fail(f"Restore requires fresh Docker volumes; existing: {sorted(existing_volumes)}")
    for name in CONFIG_FILES:
        target = ROOT / name
        if target.exists() and sha256(target) != manifest["config_sha256"][name]:
            fail(f"Existing {name} differs from backup; use a fresh bundle directory")
    for name in CONFIG_FILES:
        target = ROOT / name
        if not target.exists():
            shutil.copy2(source / "config" / name, target)
    prepare(None)
    check_poc(None) if mode == "poc" else check(None)
    missing = expected_volume_names(mode == "poc") - set(manifest["volumes"])
    if missing:
        fail(f"Backup is missing required Compose volumes: {sorted(missing)}")
    for name, item in manifest["volumes"].items():
        short_name = name.removeprefix("ai-media-analytics_")
        run("docker", "volume", "create", "--label", "com.docker.compose.project=ai-media-analytics",
            "--label", f"com.docker.compose.volume={short_name}", name)
        destination = volume_path(name)
        if any(destination.iterdir()):
            fail(f"Volume {name} is not empty; refusing extraction")
        with tarfile.open(source / item["filename"], "r") as archive:
            for member in archive.getmembers():
                relative = Path(member.name)
                if relative.is_absolute() or ".." in relative.parts or member.isdev() or member.isfifo():
                    fail(f"Unsafe archive member in {name}")
            archive.extractall(destination, filter="tar")
    start_command = "up-poc" if mode == "poc" else "up"
    print(f"Restore extracted to fresh volumes. Run check, {start_command}, then verify old and new events in UI/ClickHouse.")


def main():
    if sys.version_info < (3, 12):
        fail("Python 3.12 or newer is required for safe archive extraction")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init_parser = sub.add_parser("init")
    init_parser.add_argument("--domain", required=True)
    for name in ("prepare", "lock-images", "check", "up", "check-poc", "up-poc", "smoke"):
        sub.add_parser(name)
    backup_parser = sub.add_parser("backup")
    backup_parser.add_argument("directory")
    backup_parser.add_argument("--poc", action="store_true")
    sub.add_parser("restore").add_argument("directory")
    args = parser.parse_args()
    functions = {"init": init, "prepare": prepare, "lock-images": lock_images, "check": check,
                 "up": up, "check-poc": check_poc, "up-poc": up_poc,
                 "smoke": smoke, "backup": backup, "restore": restore}
    try:
        functions[args.command](args)
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
