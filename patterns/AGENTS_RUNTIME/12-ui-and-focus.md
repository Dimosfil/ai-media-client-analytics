## UI And Focus

- Launch applications in the background so focus does not jump away from the
  user's current window.
- For web applications, assume the user will inspect the UI manually. Do not
  open, browse, screenshot, or visually inspect the UI automatically unless the
  user explicitly asks for that.
- After implementing a frontend, backend, API, or full-stack feature, restart
  the affected dev server or backend process when local run instructions provide
  a restart command or when hot reload is uncertain. Then refresh the browser,
  client, or API caller before verification so checks do not use stale HTML,
  JavaScript, routes, schemas, or cached responses.
