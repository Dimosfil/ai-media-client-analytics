import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import call, patch

import analyticsctl as ctl


class ComposePolicyTests(unittest.TestCase):
    def test_up_requests_only_missing_locked_images_without_build(self):
        with patch.object(ctl, "check") as verify, patch.object(ctl, "run") as run:
            ctl.up(None)
        verify.assert_called_once_with(None)
        self.assertEqual(run.call_args_list[0],
                         call(*(ctl.COMPOSE_LOCKED + ["up", "-d", "--no-build", "--pull", "missing"])))

    def test_lock_images_selects_digest_from_matching_repository(self):
        raw = {"services": {"db": {"image": "postgres:15", "ports": [{}]},
                            "proxy": {"image": "caddy:2", "ports": [{"published": "80"}]}}}
        secured = {"services": {"db": {"image": "postgres:15"}, "proxy": {"image": "caddy:2"}}}

        def fake_run(*args, **kwargs):
            if args[:3] == ("docker", "image", "inspect"):
                reference = args[3]
                digest = ctl.canonical_repository(reference) + "@sha256:" + hashlib.sha256(reference.encode()).hexdigest()
                return json.dumps([{"RepoDigests": ["docker.io/library/unrelated@sha256:" + "f" * 64, digest]}])
            if args[:2] == ("docker", "pull"):
                return 0
            raise AssertionError(args)

        with tempfile.TemporaryDirectory() as directory:
            with (patch.object(ctl, "ROOT", Path(directory)), patch.object(ctl, "validate_env"),
                  patch.object(ctl, "require_command"), patch.object(ctl, "verify_upstream_files"),
                  patch.object(ctl, "compose_config", side_effect=[raw, secured]),
                  patch.object(ctl, "run", side_effect=fake_run), patch.object(ctl, "check")):
                ctl.lock_images(None)
            manifest = json.loads((Path(directory) / "image-lock.json").read_text())
            self.assertEqual(manifest["service_digests"]["db"],
                             "docker.io/library/postgres@sha256:" + hashlib.sha256(b"postgres:15").hexdigest())

    def test_real_compose_parser_with_synthetic_digest_overlay(self):
        standalone = ctl.ROOT / ".local-tools/docker-compose.exe"
        command = [str(standalone)] if standalone.is_file() else (["docker", "compose"] if shutil.which("docker") else None)
        if command is None or not (ctl.ROOT / ".env.services").is_file() or not (ctl.ROOT / "posthog/products").is_dir():
            self.skipTest("Compose parser or prepared upstream checkout unavailable")

        def config(*files):
            result = subprocess.run(command + ["--env-file", ".env.example", *[arg for file in files for arg in ("-f", str(file))],
                                               "config", "--format", "json"], cwd=ctl.ROOT, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)

        raw = config("docker-compose.yml")
        self.assertEqual((ctl.ROOT / "docker-compose.security.yml").read_text(encoding="utf-8"), ctl.security_overlay(raw))
        secured = config("docker-compose.yml", "docker-compose.security.yml")
        source_images = {name: service["image"] for name, service in secured["services"].items()}
        digests = {name: ctl.canonical_repository(image) + "@sha256:" + hashlib.sha256(image.encode()).hexdigest()
                   for name, image in source_images.items()}
        overlay = {"services": {name: {"image": digest, "pull_policy": "never"} for name, digest in digests.items()}}
        with tempfile.NamedTemporaryFile("w", suffix=".json", dir=ctl.ROOT, encoding="utf-8", delete=False) as output:
            json.dump(overlay, output)
            overlay_path = Path(output.name)
        try:
            locked = config("docker-compose.yml", "docker-compose.security.yml", overlay_path)
            ctl.validate_config(locked, {"source_images": source_images, "service_digests": digests}, "analytics.example.com")
            self.assertEqual(len(locked["services"]), 38)
        finally:
            overlay_path.unlink()

    def test_repository_normalization(self):
        self.assertEqual(ctl.canonical_repository("postgres:15-alpine"), "docker.io/library/postgres")
        self.assertEqual(ctl.canonical_repository("docker.io/posthog/posthog@sha256:" + "a" * 64),
                         "docker.io/posthog/posthog")

    def test_overlay_resets_builds_and_ports_and_repairs_db_mounts(self):
        raw = {"services": {"proxy": {}, "db": {"ports": [{}]}, "capture": {"build": {"context": "."}}}}
        overlay = ctl.security_overlay(raw)
        self.assertIn("ports: !reset []", overlay)
        self.assertIn("build: !reset null", overlay)
        self.assertIn("./posthog/docker/postgres-init-scripts:/docker-entrypoint-initdb.d:ro", overlay)

    def test_config_rejects_internal_port_and_mutable_image(self):
        digest = "docker.io/library/postgres@sha256:" + "a" * 64
        manifest = {"source_images": {"db": "postgres:15", "proxy": "caddy:2"},
                    "service_digests": {"db": digest, "proxy": "docker.io/library/caddy@sha256:" + "b" * 64}}
        config = {"services": {
            "db": {"image": digest, "pull_policy": "never", "ports": [], "volumes": [
                {"target": "/docker-entrypoint-initdb.d", "source": str(ctl.ROOT / "posthog/docker/postgres-init-scripts")},
                {"target": "/products", "source": str(ctl.ROOT / "posthog/products")}],
                   },
            "proxy": {"image": manifest["service_digests"]["proxy"], "pull_policy": "never",
                      "environment": {"CADDY_HOST": "analytics.invalid"},
                      "ports": [{"published": "80", "target": 80, "protocol": "tcp"},
                                {"published": "443", "target": 443, "protocol": "tcp"}]}}}
        with patch.object(Path, "is_dir", return_value=True):
            ctl.validate_config(config, manifest, "analytics.invalid")
            config["services"]["db"]["ports"] = [{"published": "5432", "target": 5432}]
            with self.assertRaisesRegex(RuntimeError, "Unexpected published host port"):
                ctl.validate_config(config, manifest, "analytics.invalid")
            config["services"]["db"]["ports"] = []
            config["services"]["db"]["pull_policy"] = "always"
            with self.assertRaisesRegex(RuntimeError, "Pull policy"):
                ctl.validate_config(config, manifest, "analytics.invalid")


class RestoreSafetyTests(unittest.TestCase):
    def test_existing_volume_blocks_restore_before_file_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            backup = root / "backup"
            config = backup / "config"
            config.mkdir(parents=True)
            names = ctl.CONFIG_FILES + ["POSTHOG_VERSION"]
            for name in names:
                (config / name).write_text("test", encoding="utf-8")
            volume = "ai-media-analytics_postgres-data"
            archive = backup / f"{volume}.tar"
            archive.write_bytes(b"synthetic")
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            manifest = {"posthog_commit": ctl.VERSION,
                        "config_sha256": {name: digest(config / name) for name in names},
                        "volumes": {volume: {"filename": archive.name, "sha256": digest(archive)}}}
            (backup / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

            def fake_run(*args, **_kwargs):
                if args[:2] == ("docker", "ps"):
                    return ""
                if args[:3] == ("docker", "volume", "ls"):
                    return volume + "\n"
                raise AssertionError(args)

            with (patch.object(ctl, "ROOT", root), patch.object(ctl, "run", side_effect=fake_run),
                  patch.object(ctl.sys, "platform", "linux"), patch.object(ctl.os, "geteuid", return_value=0, create=True)):
                with self.assertRaisesRegex(RuntimeError, "fresh Docker volumes"):
                    ctl.restore(SimpleNamespace(directory=str(backup)))
            self.assertFalse((root / ".env").exists())


if __name__ == "__main__":
    unittest.main()
