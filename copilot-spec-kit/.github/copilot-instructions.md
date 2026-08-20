# Copilot Instructions — Legacy Modernization

This repository is a legacy Struts/JSP/Spring Boot application being migrated feature by feature to
an Angular SPA with REST APIs, using a strangler fig approach.

## What Copilot is being used for here

Primarily **analysis and specification**, not code generation against the legacy tree. Unless
explicitly asked, do not modify legacy application code.

## Standing rules

- Cite `path/to/File.java:LINE` for any non-obvious claim about how the application behaves.
- Never invent behavior. If the code is ambiguous, write `OPEN QUESTION:` with the file and line
  that prompted it. Honest gaps are more useful than confident guesses.
- Quote constants, thresholds, and SQL exactly as written. Never paraphrase a query.
- Keep description separate from recommendation. State what the code does today before offering an
  opinion on what it should do.
- Use the domain glossary in `docs/APP-PROFILE.md` — do not invent synonyms for established terms.

## Key artifacts

| File | What it is |
|---|---|
| `docs/APP-PROFILE.md` | Reconnaissance profile: stack, layer conventions, data access, session inventory, feature index, glossary, risk register |
| `docs/specs/<feature>/TRACE.md` | Raw extraction findings for one feature |
| `docs/specs/<feature>/SPEC.md` | The reviewed specification handed to implementation |
| `.github/prompts/` | The recon and extraction prompt files |

<!--
After the recon phases complete and a human has reviewed docs/APP-PROFILE.md, paste the
condensed conventions and glossary below so every Copilot session inherits them without
re-reading the profile.
-->

## Application conventions

_To be filled from docs/APP-PROFILE.md after recon._
