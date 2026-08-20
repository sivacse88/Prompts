---
description: 'Legacy app recon phase 2 — module map, layer conventions, and where business logic actually lives. Writes docs/APP-PROFILE.md sections 3-4.'
mode: agent
tools: ['codebase', 'search', 'editFiles']
---

# Recon Phase 2 — Layers & Logic Distribution

Continue the reconnaissance. Read `#file:docs/APP-PROFILE.md` first for established context.

Apply the ground rules from Phase 1: evidence with `file:line` citations, confidence labels,
strategic sampling, hunt for exceptions, never guess.

## Task

### 3. Module & package map

Map the source tree to logical layers. For each, establish the package pattern, naming convention,
and the base class or interface everything extends.

| Layer | Package pattern | Naming convention | Base type | Example (`file:line`) |
|---|---|---|---|---|
| Action | | | | |
| Form / DTO | | | | |
| Service | | | | |
| DAO / repository | | | | |
| Domain model | | | | |
| View | | | | |
| Utility / helper | | | | |

Then search for classes that break each convention and list them.

### 4. Where the business logic actually lives

This is the most important section in the whole profile. Establish, with evidence, the real
distribution of business logic across:

- Action classes
- Service classes
- DAOs
- SQL and stored procedures
- **JSP scriptlets and tag logic**
- JavaScript
- Database constraints and triggers
- Configuration and property files

Give an approximate percentage split and cite two examples of each location where logic was found.

Search specifically for `<%` scriptlets in the JSP tree and report what business rules live there.
Those are the rules that get silently lost in a migration — call them out loudly.

Also find and list: every hardcoded constant, magic number, and status code that appears to carry
business meaning, with its location. You will not be able to decode all of them; mark the rest
`UNKNOWN — needs SME`.

## Output

Update `docs/APP-PROFILE.md` with `## 3. Module & Package Map` and
`## 4. Business Logic Distribution`. Leave other sections untouched.

End with your sampling method, `OPEN QUESTION:` items, and a note on anything Phase 3 must verify.
