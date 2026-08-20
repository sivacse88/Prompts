---
description: 'Legacy app recon phase 5 — generate the app-specific feature extraction prompt from the reviewed profile. Rewrites .github/prompts/extract-feature-spec.prompt.md.'
mode: agent
tools: ['codebase', 'search', 'editFiles']
---

# Recon Phase 5 — Generate the Feature Extraction Prompt

**Precondition:** `docs/APP-PROFILE.md` has been reviewed by a human and the Phase 4 interview
questions have been answered. If the profile still contains unresolved `UNKNOWN` entries in the
glossary or unanswered interview questions, say so and ask before proceeding.

Read `#file:docs/APP-PROFILE.md` in full.

## Task

Rewrite `#file:.github/prompts/extract-feature-spec.prompt.md`, replacing every `{{placeholder}}`
in its **Application Context** block with established facts from the profile.

The generated prompt must be usable by an agent session that has **never seen** this
reconnaissance. That means inlining, not referencing:

- Real file paths for Struts config, validation config, and message bundles
- Real package patterns, base classes, and naming conventions per layer
- The real data access mechanism and the search pattern that finds SQL in this codebase
- The stored procedure convention and whether source is available
- The session management convention and the session key inventory
- The security and transaction mechanisms
- The full request-lifecycle Mermaid sequence diagram from Phase 1
- The complete domain glossary table from Phase 4
- A one-paragraph summary of the top migration risks from Phase 4

Anything you leave generic will be guessed at during extraction.

## Rules

- **Change only the Application Context block and the glossary.** The procedure, output structure,
  rules, and completeness checklist in that file are deliberate — do not shorten, reorder, or
  "improve" them.
- Keep the YAML front matter intact, including the `${input:...}` variables.
- If the glossary is longer than roughly 60 rows, move it to `docs/GLOSSARY.md` and reference it as
  `#file:docs/GLOSSARY.md` instead of inlining, so the prompt stays within context.
- If the profile is thin in an area the extraction depends on, do not paper over it. Add an
  explicit instruction in the generated prompt telling the extraction agent to verify that area
  from source rather than trusting the profile.

## Output

The rewritten `extract-feature-spec.prompt.md`, plus a short chat summary of which placeholders you
filled, which you could not, and what a human should verify before the first extraction run.
