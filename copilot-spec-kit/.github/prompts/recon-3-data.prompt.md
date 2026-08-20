---
description: 'Legacy app recon phase 3 — data access, cross-cutting concerns, integration points. Writes docs/APP-PROFILE.md sections 5-7.'
mode: agent
tools: ['codebase', 'search', 'editFiles']
---

# Recon Phase 3 — Data, Cross-Cutting Concerns, Integrations

Read `#file:docs/APP-PROFILE.md` first. Same ground rules as Phase 1.

## Task

### 5. Data access

- Mechanism(s): raw JDBC, `JdbcTemplate`, iBATIS/MyBatis, Hibernate, stored procedure calls —
  and whether more than one is in use
- **Where SQL text lives:** inline string literals, XML mapper files, `.sql` files, or entirely in
  the database. Give the search pattern that finds SQL in this codebase.
- Stored procedure convention: naming, invocation style, parameter conventions, and whether source
  is available in the workspace. If not, record it as a Phase 4 risk.
- Connection pooling and transaction management style (declarative vs programmatic), isolation levels
- Schema conventions: table/column naming, primary key strategy, soft deletes, audit columns,
  optimistic locking, and how timestamps and timezones are handled
- Any multi-database, cross-schema, or read-replica access

### 6. Cross-cutting concerns

For each, describe the mechanism and cite one concrete example:

| Concern | Mechanism | Example |
|---|---|---|
| Authentication | | |
| Authorization / entitlements | | |
| Session management — what actually lives in session | | |
| Transaction demarcation | | |
| Exception handling & error pages | | |
| Message resolution / i18n | | |
| Logging & audit | | |
| Caching | | |
| File upload / download | | |
| CSRF / token handling | | |
| Date & timezone convention | | |

For session management, produce a full inventory: search every `session.setAttribute` call in the
codebase and list the distinct keys, the writer, and the readers. This inventory drives the hardest
part of the SPA migration.

### 7. Integration points

Every boundary the app talks across — REST/SOAP clients, MQ and Kafka topics, batch jobs and
schedulers, file drops, mainframe calls, shared databases. For each: direction, protocol, payload
shape, error/retry behavior, and which features depend on it.

## Output

Update `docs/APP-PROFILE.md` with `## 5. Data Access`, `## 6. Cross-Cutting Concerns`, and
`## 7. Integration Points`.

End with sampling method, `OPEN QUESTION:` items, and anything Phase 4 needs.
