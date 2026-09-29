# PostHog deployment contract

## Scope

This repository provisions a dedicated self-hosted PostHog instance for product
analytics. It does not instrument AI Media Client or collect its technical logs.
`POSTHOG_VERSION` is the upstream source commit. The two checked-in Compose
snapshots must match that commit byte for byte; `.env.services` is regenerated
from the same checkout.

## Invariants

- `init` creates `.env` once with generated secrets. No operation regenerates or
  commits the secrets.
- `prepare` checks the exact upstream commit and clean checkout before it uses
  upstream files. The security overlay is derived from that Compose model.
- `lock-images` is explicit and one-time. Every runtime service uses an image
  repository and SHA-256 registry digest from the same source repository as its
  upstream image. `check` rejects a changed service set, tag, digest, build,
  pull policy, or published internal port. `up` never builds or pulls tags; it
  may fetch missing immutable digests on a fresh restore host.
- Only Caddy publishes TCP 80 and 443. Storage and worker services are private
  to Docker networks. Every persistent Docker volume is named, including Caddy
  and Elasticsearch volumes that are anonymous upstream.
- `backup` is a cold, root-run Linux operation: verify the required volumes and
  running core services, stop the stack, archive every project-labelled volume
  with ownership metadata, copy config and checksums, and restart. A partial
  archive carries `INCOMPLETE`; restart failure is reported as failure.
- `restore` runs on a separate clean Docker daemon. It verifies checksums and
  refuses existing target containers and volumes before extracting. The same
  project name and original domain are retained. Restored volumes keep Compose
  labels, and archive ownership is restored by root. Restorability requires
  runtime and historical-event verification.
- `smoke` sends only `analytics_smoke` with a unique synthetic distinct ID.
  Capture acceptance alone is insufficient: the event must appear in
  ClickHouse and be confirmed in PostHog UI.

## Current verification boundary

On 2026-09-29, byte identity with upstream commit
`812820220b9e8b514053612e5aa9a9fb80f5cec6` and Docker Compose v2.39.4
configuration parsing were checked locally. The resulting unbuilt model has 38
services, only Caddy publishes ports, and all 14 persistent volumes are named.
No target Linux Docker daemon was available; image pulls, runtime health, HTTPS,
UI smoke, cold backup, and isolated restore remain unverified.

Implementation: `analyticsctl.py`, checked-in Compose snapshots, generated
security overlay; operator workflow: `README.md`.
