# CLAUDE.md — bot-bb Project Guidelines

## Code Style

- **Minimalistic**: Write the least code possible to solve the problem.
- **DRY**: Never duplicate logic. If it exists, reuse it. If it doesn't, make it reusable. Don't ever hardcode things unless it is just for testing !
- **No over-engineering**: Don't add abstractions, error handling, or features that aren't needed right now. Focus to do what is asked.
- **No decorative comments** unless the logic is genuinely non-obvious, there needs to be only one comment with "#" for one line max !

## Structure & Modularity

- `src/bots/` — Individual bot scripts (one per target site/system)
- `src/classes/` — Shared logic: drivers, file handling, data extraction, scheduling
- `src/classes/methods/` — Reusable method modules (cancel, parallel, auto-exec, pdf)
- `src/classes/file/` — File I/O, conversion, and path management
- `src/view/` — GUI screens (gui1–gui7) and reusable UI modules
- `src/view/modules/` — Shared UI components (buttons, loading indicators)
- `src/config/` — Environment and configuration files
- `src/config/systems_registry.py` — configuration file for all bots the appear in the gui. New bots have to be added here to appear in the app.

## Rules

1. **Reuse before creating** — Check `src/classes/` and `src/view/modules/` for existing utilities before writing new ones !!!
    1.5 **Use the same architecture for consistency** - Always check the existing architecture before making new bots so they follow the same general flow and idea.
2. **One responsibility per file** — Each module does one thing well.
3. **Keep functions small** — If a function does more than one thing, split it.
4. **Flat over nested** — Prefer early returns and guard clauses over deep indentation.
5. **Consistent naming** — `snake_case` for everything (files, functions, variables).
6. **No unused code** — Delete dead code, don't comment it out.
7. **No use of emojis** - Do not use emojis whatsoever !
