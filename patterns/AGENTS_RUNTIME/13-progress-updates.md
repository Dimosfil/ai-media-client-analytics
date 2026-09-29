## Progress Updates

- Keep progress updates phase-level, not command-level. Do not narrate after
  every command batch, report counters such as "ran 4 commands", or live-blog
  each intermediate hypothesis.
- Do not duplicate tool-run counters that the chat UI may show automatically;
  system UI counters are not agent progress updates.
- Send an update when the phase changes, a meaningful finding changes the next
  step, a blocker appears, or work has been quiet for long enough that the user
  needs reassurance.
- Batch routine observations internally and summarize only the current
  conclusion, next action, and blockers. Keep command names and detailed logs
  for final summaries or failure diagnosis.
