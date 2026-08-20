---
description: 'Legacy app recon phase 4 — feature index, domain glossary, migration risk register, and interview questions. Writes docs/APP-PROFILE.md sections 8-10.'
mode: agent
tools: ['codebase', 'search', 'editFiles']
---

# Recon Phase 4 — Feature Index, Glossary, Risks

Read `#file:docs/APP-PROFILE.md` first. Same ground rules as Phase 1.

## Task

### 8. Feature index

From every Struts config file identified in Phase 1, build the catalog that lets a human point at
a feature by name.

| Feature ID | Feature name | Entry action path(s) | Form bean | Primary JSP(s) | Service(s) | Tables / procs touched | Complexity |
|---|---|---|---|---|---|---|---|
| `F-001` | | | | | | | S / M / L |

Rules:
- **Group related actions into one feature.** A five-step wizard is one feature, not five. State
  your grouping logic.
- Flag any action path that appears orphaned or unreachable, with the evidence.
- Complexity is a rough estimate of extraction effort: S = single action, one table;
  M = multi-action or multi-table; L = wizard, heavy session use, or stored-procedure-driven logic.

### 9. Domain glossary

Every domain term, abbreviation, status code, and business constant encountered so far, with its
meaning and where it's defined. Include the magic values surfaced in Phase 2.

| Term | Meaning | Defined at | Confidence |
|---|---|---|---|

Mark undecodable entries `UNKNOWN — needs SME`. This glossary gets injected into every feature
extraction, so precision here compounds.

### 10. Migration risk register

Ranked by expected pain:

| Rank | Risk | Evidence | Features affected | Mitigation |
|---|---|---|---|---|

Consider at minimum: heavy session dependence, business logic in JSP scriptlets, stored procedures
with no available source, shared mutable state, framework behavior with no modern equivalent,
features with no test coverage, code that may or may not be dead, and undocumented integrations.

### 11. Interview the human

Finally, list the questions you could not answer from the code, **ranked by how much the answer
would change the resulting feature specs**. For each: the question, the file/line that prompted it,
and what you'll assume if it goes unanswered.

Do not ask questions the repository already answers. Aim for the ten that matter most.

## Output

Update `docs/APP-PROFILE.md` with `## 8. Feature Index`, `## 9. Domain Glossary`, and
`## 10. Migration Risk Register`.

Put the interview questions in your chat response, not in the file — they are for the human,
and their answers get folded back in before Phase 5 runs.

**Stop here.** Do not proceed to generating the extraction prompt until a human has reviewed this
profile and answered the questions. An error in the profile propagates into every feature spec.
