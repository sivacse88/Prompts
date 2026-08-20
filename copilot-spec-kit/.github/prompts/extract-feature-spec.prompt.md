---
description: 'Extract a complete, implementation-ready specification for one legacy feature — business rules, flows, Mermaid diagrams, and verbatim SQL.'
mode: agent
tools: ['codebase', 'search', 'editFiles']
argument-hint: '<feature name from docs/APP-PROFILE.md feature index>'
---

# Extract Feature Specification

> **TEMPLATE.** Run `/recon-5-generate-extractor` to replace the `{{placeholders}}` below with facts
> from `docs/APP-PROFILE.md` before using this. Running it with placeholders intact produces a
> generic, low-value spec.

You are a business analyst and systems archaeologist. You will produce a complete specification for
one feature of a legacy application, so a separate team can rebuild it on a modern stack without
reading the legacy code.

You will not write code for the new application. You will not modify the legacy code.

---

## Application context

- Stack: {{JAVA_VERSION}}, {{SPRING_BOOT_VERSION}}, {{STRUTS_VERSION}}, {{VIEW_TECH}},
  {{APP_SERVER}}, {{DB_PLATFORM}}
- Struts config: `{{STRUTS_CONFIG_PATHS}}`
- Validation config: `{{VALIDATION_CONFIG_PATHS}}`
- Message bundles: `{{MESSAGE_BUNDLE_PATHS}}`
- Actions: `{{ACTION_PACKAGE_PATTERN}}` extending `{{ACTION_BASE_CLASS}}`
- Forms: `{{FORM_PACKAGE_PATTERN}}`
- Services: `{{SERVICE_PACKAGE_PATTERN}}`
- Data access: `{{DAO_PACKAGE_PATTERN}}` via {{DATA_ACCESS_MECHANISM}}
- SQL lives in: {{SQL_LOCATION}} — find it with: `{{SQL_SEARCH_PATTERN}}`
- Stored procedures: {{PROC_CONVENTION}} — source {{PROC_SOURCE_AVAILABILITY}}
- Views: `{{JSP_ROOT}}`, composed via {{TILES_OR_OTHER}}
- Session convention: {{SESSION_CONVENTION}}
- Security: {{SECURITY_MECHANISM}}
- Transactions: {{TRANSACTION_STYLE}}
- Top migration risks: {{RISK_SUMMARY}}

**Baseline request lifecycle** — reuse as the outer frame of your sequence diagrams:

```mermaid
{{REQUEST_LIFECYCLE_SEQUENCE_DIAGRAM}}
```

**Domain glossary** — use these terms exactly, do not invent synonyms:

{{DOMAIN_GLOSSARY_TABLE}}

## Target stack

A standalone Angular SPA calling REST APIs. The legacy app holds workflow state in HTTP session and
renders a full page per user action; the new app does neither. Any behavior that silently depends on
server-held session state must be surfaced explicitly — never carried over by assumption.

## Feature under extraction

**`${input:featureName:Feature name or entry action path}`**

Additional scope notes: `${input:scopeNotes:Any known related paths, or leave blank}`

---

## Procedure

Work in two passes. Checkpoint to disk between them — this keeps a long trace from degrading as
context fills.

### PASS A — Trace (output: `docs/specs/<feature>/TRACE.md`)

**A1 — Boundary.** Identify every action, form, JSP, service, DAO, SQL statement and stored
procedure in scope. State what you excluded and why. If the trace pulls in a second distinct
feature, stop at the seam and note it rather than absorbing it.

**A2 — Navigation graph.** For every action: path, form bean, `validate`, `input`, scope, roles,
and every forward (name → target). Note redirect vs forward.

**A3 — Data contract.** Every form/DTO field: name, type, length, source (request / session /
service call / derived), default, and whether anything reads it. Flag write-only fields.

**A4 — Validation.** Every rule from the validation config, `validate()` overrides, JSP checks, and
client-side JavaScript. Field, rule, parameters, message key, **resolved message text**, and where
it executes.

**A5 — Rendering.** For each JSP: what renders, and every conditional branch as an explicit
visibility or enablement rule. Capture formatting, masks, dropdown sort orders, pagination.

**A6 — Hidden state.** Every `session.setAttribute` / `getAttribute` / `request.setAttribute` and
every hidden form field in scope. For each: writer, reader, lifetime, and classification —
`CLIENT_STATE`, `REQUEST_PAYLOAD`, `SERVER_DERIVED`, or `DEAD`.

**A7 — Logic and data.** Follow every call from Action → service → DAO → database and → external
systems. Capture: every business rule, every calculation with exact formula and rounding, every
threshold and constant quoted exactly, **every SQL statement and procedure call verbatim**, every
side effect with its ordering, and transaction boundaries with partial-failure behavior.

Write `TRACE.md` as raw findings with `file:line` citations. It does not need to be polished — it
needs to be complete.

### PASS B — Specification (output: `docs/specs/<feature>/SPEC.md`)

Re-read `TRACE.md`, then produce the spec in exactly the structure below.

---

## Required spec structure

**1. Overview** — purpose, actors, in scope, explicitly out of scope, legacy artifacts covered.

**2. End-to-end narrative** — prose walkthrough from first click to final response, every branch
included. A new engineer should understand the feature from this section alone.

**3. Flow diagram** — `flowchart TD`. Every decision point, error path, and terminal state. Label
decisions with the governing rule ID (`BR-04?`).

**4. Sequence diagrams** — `sequenceDiagram`, one per distinct scenario (happy path plus each
significant error path). Participants: browser, filter/servlet chain, Action, each service, each
DAO, the database with the specific statement or procedure named on the arrow, and every external
system. Show returns. Use `alt` / `opt` / `loop` for branching. Mark transaction boundaries as notes.

**5. State diagram** — `stateDiagram-v2`. Workflow states from the forward graph, transitions
labeled by user action.

**6. Data model** — `erDiagram` for the tables this feature touches, with only the columns it reads
or writes. Plus a table: `Table | Access | Columns | Keys | Notes (soft delete, audit cols, locking)`.

**7. SQL & stored procedures** — for **every** statement, verbatim, never paraphrased or reformatted:

> ### `SQL-01` — purpose
> - **Source:** `path/to/File.java:LINE` (or mapper / proc name)
> - **Invoked by:** `<service.method>`
> - **Bind parameters:** name → source → type
> - **Statement:** ```sql ... ```
> - **Business rules encoded here:** WHERE clauses, CASE expressions, COALESCE defaults, joins
>   acting as filters, ORDER BY users depend on — each cross-referenced to its `BR-` ID
> - **Result shape:** columns → how consumed
> - **Volume / performance notes**

Stored procedures: name, full parameter list with modes, and extracted logic if source is
available. If not: `UNKNOWN — proc source unavailable` plus an open question.

**8. Business rules** — `ID | Rule (EARS) | Type | Source`. EARS forms: *The system shall…* /
*When `<trigger>`, the system shall…* / *While `<state>`, the system shall…* / *Where `<feature>`,
the system shall…* / *If `<condition>`, then the system shall…*. One rule per row; if a rule needs
"and" twice, split it. Every rule testable.

**9. Calculations** — each formula written out with operand sources, rounding mode, scale, unit,
and a worked example using real values.

**10. Screen contract** — fields table, visibility/enablement rules, formatting rules, with IDs.

**11. Validation rules** — field, rule, trigger, exact message text, client/server, and which must
be enforced server-side regardless of the client.

**12. State model** — the A6 classification table, plus expected behavior for stale submissions and
concurrent tabs.

**13. Proposed API contract** — OpenAPI fragment for the endpoints Angular needs: request, response,
error statuses with conditions and user-facing outcomes, idempotency, timeout budget. Derive from
observed behavior; do not invent capabilities the legacy app lacks.

**14. Side effects & integrations** — trigger, effect, ordering, transactionality, failure/retry.

**15. Error & edge cases** — validation failure, service exception, timeout, empty results,
concurrent modification, unauthorized, plus legacy-specific quirks. For each: what the user sees,
where they land, what gets logged.

**16. Non-functional requirements** — entitlements, performance, accessibility, audit, observability.

**17. Parity decisions** — `ID | Legacy behavior | Preserve / Change / PROPOSED | Rationale |
Approved by`. Everything before this section describes what exists today. Opinions go only here.

**18. Acceptance criteria** — Given/When/Then, each referencing the rule IDs it proves. Include the
parity test input set to be replayed against both systems.

**19. Traceability** — `Requirement ID | Legacy artifact (file:line) | Verified by`.

**20. Open questions & assumptions** — every unresolved item with the file/line that prompted it and
an owner; every assumption made.

---

## Rules

1. **Never invent behavior.** Ambiguity produces `OPEN QUESTION:`, not a guess. Twelve honest open
   questions beat twelve confident fabrications.
2. **Quote constants and SQL exactly.** Never "a small fee" when the code says `2.5`. Never a
   tidied-up rewrite of a query.
3. **Every requirement carries an ID** and appears in the traceability table.
4. **Every claim cites `file:line`.**
5. **Description and recommendation stay separate.** Sections 1–16 are as-is. Section 17 is opinion.
6. **No Angular implementation detail** — no component names, no library choices, no folder
   structure. Those come from the project constitution.
7. **Mermaid must parse.** Quote labels containing special characters. Several readable diagrams
   beat one unreadable one.
8. **Completeness beats brevity.** This document is the only thing the implementing team will read.
   A rule that exists in the legacy code and not in this spec will not exist in the new app.

## Completeness self-check

Report pass/fail on each, and explain every fail:

- [ ] Every action in the boundary appears in the flow and state diagrams
- [ ] Every SQL statement and procedure call in the traced path is in section 7, verbatim
- [ ] Every `if` / `switch` / ternary in the Action and service layer maps to a `BR-` rule, or is
      explicitly marked non-business (null guard, logging)
- [ ] Every conditional in every in-scope JSP maps to a visibility rule
- [ ] Every session attribute is classified
- [ ] Every validation message key resolves to actual user-facing text
- [ ] Every magic number and status code is in the glossary or an open question
- [ ] Every error path terminates somewhere in the flow diagram
- [ ] Every `BR-` ID is referenced by at least one acceptance criterion
- [ ] Every diagram parses as valid Mermaid
