# Query And Prompt Normalization Boundaries

Search, retrieval, ranking, classification, and model-facing UI features often
need an interpretation/translation layer: intent extraction, language
translation, synonyms, stemming, prompt expansion, language routing,
model-specific templates, score thresholds, and fallbacks. Treat that behavior
as a dedicated capability and adapter policy, not as scattered hard-code.

## Rule

- Do not embed ad hoc translation maps, synonym dictionaries, stemming rules,
  prompt expansions, model compatibility hacks, intent-interpretation rules, or
  scoring thresholds directly in request handlers, UI glue, command handlers, or
  one-off feature code.
- Keep query/prompt behavior in a dedicated interpretation/translation module,
  documented config, resource files, curated data assets, locale packs, model
  adapter modules, provider-swappable LLM adapters, or search/ranking pipeline
  components with tests.
- The interpretation/translation module may be implemented by deterministic
  rules, curated dictionaries, local algorithms, retrieval, a local or remote
  service, or any interchangeable LLM provider. Keep the provider behind an
  interface so changing providers does not rewrite product/UI logic.
- If a model works better with another language, prompt shape, or query style,
  express that in the model adapter or retrieval pipeline contract. Do not mix
  raw user text with model-specific expansions unless the contract and tests say
  that blend is intended.
- Keep user intent separate from model-facing text. Store or pass the original
  query for display, audit, and debugging, then derive normalized model input
  through a named pipeline step.
- Version or document curated normalization resources when they affect user
  results, especially for multilingual search, domain vocabulary, safety
  filters, or ranking.
- Avoid single-example fixes that only add the current failing word. Add a
  general extension point and a focused fixture showing how new vocabulary is
  added without editing core application logic.

## Architecture

- Use a small pipeline such as `parse -> detect language -> normalize -> expand
  -> adapt for model -> rank -> explain`.
- Put user-intent interpretation and translation behind a stable interface such
  as `interpret(user_query, context) -> interpreted_intent + model_queries`.
- Put model-specific behavior behind an adapter, for example an image-text
  embedding query adapter, lexical-search adapter, or hybrid retriever.
- Keep domain dictionaries outside the adapter when they are reusable across
  models. Keep model prompt templates inside or beside the adapter when they are
  specific to one model family.
- If an LLM implements interpretation or translation, configure the provider,
  model, prompt template, timeout, budget, fallback, and privacy policy outside
  product/UI code.
- Validate resource shape at startup or load time. Fail clearly when a required
  locale, synonym set, prompt template, or threshold is missing or malformed.

## Audit Checklist

Search changed paths for:

- inline dictionaries of user words, translations, synonyms, stems, or aliases;
- inline intent parsers or translation heuristics in UI/request code;
- prompt strings added directly inside request handlers or UI callbacks;
- special cases for one failing query;
- provider-specific LLM calls embedded in product/UI logic;
- model names coupled to product/UI logic;
- score thresholds or ranking weights without config or tests;
- tests that only assert one demo word rather than the normalization contract.

Move findings into resources, config, adapters, or fixtures. If a full cleanup
is too large, record the debt in project memory with the affected paths and the
expected resource/adaptor shape.

## Verification

- Test at least one original user-language query, the interpreted intent, and
  the expected model-facing query.
- Test that adding a new synonym or translation does not require editing core
  request/UI logic.
- Test that changing the interpretation implementation, including replacing a
  deterministic module with an LLM adapter or changing LLM providers, does not
  require rewriting product/UI logic.
- Test that raw user text is preserved for display/debugging while model-facing
  text uses the adapter pipeline.
- Inspect search/ranking results with a small fixture or smoke check for the
  failing query class.
