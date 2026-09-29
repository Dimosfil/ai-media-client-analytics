## Project Memory And RAG Operations

- Apply the project-local `config_service.enabled` toggle from
  `08-config-service.md` to every operation below. Query or write
  config-service only when integration is effectively enabled. When disabled,
  ordinary local operations use documented project-local runtime config;
  config-service-specific operations stop with the disabled-state blocker and
  point to `gi config on`.
- Treat `gi sql`, `gi sqlite`, `ги sql`, `ги sqlite`, `gi vector`,
  `gi вектор`, and `ги вектор` as requests to inspect project-memory retrieval
  readiness and current metrics. For SQL, read `tools/project-memory/rag-system.json`
  when present, run the local index stats command when available, count
  reviewable project-memory/spec files, compare the numbers with the configured
  or default SQLite activation limits, and report whether SQLite/FTS is absent,
  current, stale, or recommended. For vector, read vector and embedding metadata,
  check semantic corpus size and chunk count, run the vector adapter status
  command when available, compare the numbers with vector activation limits, and
  report collection, record count, index path, freshness caveats, and readiness.
  These are inspection commands by default; do not create external services,
  install heavy dependencies, upload data, or index private sources unless the
  user explicitly asks and project-local rules allow it.
- Treat `gi tools rebuild`, `gi rag rebuild`, `ги тулс ребилд`,
  `ги раг ребилд`, and equivalent full GI/RAG rebuild wording as requests to
  rebuild the current project's entire configured GI/RAG project-memory
  retrieval system from approved sources: source manifest, SQLite/FTS or
  structured memory indexes, chunk exports, vector indexes, adapter metadata,
  and retrieval eval/status checks. This is a heavy command and requires an
  explicit user confirmation immediately before running the full rebuild, even
  if the user requested the command by name. Before asking for confirmation,
  read `tools/project-memory/rag-system.json`, list the configured rebuild
  nodes, generated paths that may be replaced, expected local scripts or
  adapters, and privacy exclusions. Do not include secrets, private runtime
  data, ignored telemetry, or sources outside the current project root. After a
  successful rebuild, run the configured stats/status/eval checks, update local
  rebuild state such as `last_full_rebuild_migration` or per-node markers when
  present, and report changed generated artifacts without committing
  rebuildable indexes.
- Treat `gi tools rebuild sql`, `gi rag rebuild sql`,
  `gi tools rebuild vector`, `gi rag rebuild vector`,
  `gi tools rebuild chunks`, `gi rag rebuild chunks`,
  `gi tools rebuild manifest`, `gi rag rebuild manifest`,
  `gi tools rebuild evals`, `gi rag rebuild evals`, and Russian equivalents
  such as `ги тулс ребилд sql`, `ги раг ребилд sql`,
  `ги тулс ребилд вектор`, `ги раг ребилд вектор`,
  `ги тулс ребилд чанки`, `ги раг ребилд чанки`,
  `ги тулс ребилд манифест`, `ги раг ребилд манифест`,
  `ги тулс ребилд тесты`, and `ги раг ребилд тесты` as requests to rebuild only
  the named GI/RAG node. Read `rag-system.json`, run only the documented node
  command or local helper, then verify that node's status. Ask one short
  clarification question if the node is not configured instead of guessing a
  command. For an `evals` node, prefer machine-checkable retrieval checks that
  verify index health, count consistency, and expected source paths in top
  keyword, semantic, or hybrid results; do not treat an answer's wording as the
  primary eval target.
- During `gi обновить`, inspect each newly applied migration. If a migration
  changes RAG source rules, chunking, embedding metadata, SQLite/vector schemas,
  retrieval adapters, or project-memory index scripts, check the project's
  `rag-system.json` rebuild state. If the project has not rebuilt the affected
  RAG nodes for that migration, tell the user exactly which nodes are stale and
  ask for confirmation before running the full `gi tools rebuild`; for narrow
  migrations, run or offer the smallest documented node rebuild that satisfies
  the migration. Do not mark RAG rebuild state current until the rebuild and
  readback/status checks succeed.
