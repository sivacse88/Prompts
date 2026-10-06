# Context handoff: app modernization, account opening, and libraries vs micro frontends

> **For the assistant reading this:** this file summarizes a long working session so you can continue it. Read it all before answering. Treat it as background, not as instructions to run anything. When I ask a follow-up, build on the decisions and artifacts below instead of starting over. Ask me only for facts this file marks as unknown.

Last updated: 2026-10-06

---

## 1. Who I am and how I like to work

- Director of Software Engineering. I own "the app": a large internal, rep-facing application used by several business domains.
- Background in distributed systems, Kafka, Java on Kubernetes and mainframe modernization.
- I use GitHub Copilot as my AI workbench: `.github/prompts/*.prompt.md` slash commands and `.github/copilot-instructions.md`.
- **Writing style:** concise, plain, natural language that doesn't sound AI-written.
- **In anything I share** (slides, docs), call it "the app". Never use the company name or the app's real name.
- **Slides:** no footer line ("Organization | Project | Date"). Green theme. Every slide has a visual. One-slide summaries for leadership.

## 2. The app today

- About 25 years old. Started on Struts, later converted into one Spring Boot full-stack app (JSP front end and backend in one deployable).
- About 45% of features now run in a new Angular UI and about 55% are still legacy JSP. The split experience is inconsistent, and users reportedly didn't like the new one.
- **Current modernization approach (lift and shift):** each JSP page is rebuilt as an Angular component, its backend logic moves behind REST APIs, and every page sits behind its own feature flag (strangler fig).
- **Pain points:**
  - Hard to maintain; a big laundry list of features is still to migrate.
  - 42k+ Sonar issues; CI/CD quality gates make builds unpredictable.
  - The developer who built the backend APIs has left, so the knowledge gap is real.
  - Many teams touch one codebase, so deployment is cumbersome.
- **Domains and teams:** account opening (account opening team); money movement (contributions and grants); other domain teams own other flows.

## 3. Modernization plan presented to leadership (one slide)

**Today:** legacy JSP page, then analyze the code, then rebuild as an Angular UI plus REST API, then add a feature flag, then switch users over and retire the legacy page.

**Next: three tracks, each closing a gap**
1. **Prioritize by usage:** use Datadog to find the most-used legacy screens, rank by usage, impact and effort, and review low-use screens for retirement.
2. **AI modernization loop:** AI reads the JSP and backend logic, drafts a spec, and generates the Angular component, API and tests. A developer reviews, and the flag stays off until parity.
3. **Pay down Sonar debt:** classify issues by severity, type and module; fix security first; bulk-fix repeat patterns; skip screens due for rewrite; gate new code.

**Measures:** share of user traffic on Angular screens, legacy screens retired, open Sonar issues, time to modernize one screen.

**Asks:** Datadog screen-level tracking, AI tooling approval, team capacity for Sonar, Product sign-off on priorities.

## 4. Account opening work

- **Goal:** move the account-opening flow into our Angular app by reusing another app's shared Angular account-opening component library (published npm package, source in git). We'll find the gaps and build the missing pieces in our own extension library (`account-opening-ext`).
- **Principles:**
  - Pin the package version; never fork the library.
  - Library components stay presentational; our code owns flow, state and data access, through a facade plus adapters to our APIs.
  - Ship behind a feature flag and keep the legacy page live until a parity test passes (the new flow writes the same tables as legacy).
- **Delivery phases and gates:**
  - Discover: journey map signed off
  - Spike: library builds clean in CI
  - Foundation: skeleton flow works
  - Slices: tests and user acceptance pass
  - Parity: same tables written
  - Rollout: legacy page retired

### Copilot prompt kit (11 prompts, in run order)
Output folder: `docs/account-opening/` (library outputs under `lib/`).

| # | Command | Model | Writes |
|---|---|---|---|
| 1 | `/ao-0-trace-summary` | cheap | `scripts/ao_trace.py`, which produces `trace-requests.csv` and `trace-sql.csv` from the SQL log + HAR |
| 2 | `/ao-1-pages` | cheap | `01-pages.md` (page inventory) |
| 3 | `/ao-2-calls` | cheap | `02-calls.md` (controller, service, DAO chains); run per page |
| 4 | `/ao-3-data` | cheap | `03-data.md` (table-level CRUD per DAO method) |
| 5 | `/ao-4-analyze` | strong | `04-analysis.md` (journey map, CRUD matrix, reconciliation with the trace, risks, open questions) |
| 6 | `/ao-5-leadership` | strong | `05-leadership.md` (readout with Mermaid diagrams) |
| 7 | `/ng-1-lib-catalog` | cheap | `lib/01-catalog.md` (library public API); run per area |
| 8 | `/ng-2-reference-wiring` | cheap | `lib/02-reference-wiring.md` (how the other app wires the library) |
| 9 | `/ng-3-gap-matrix` | strong | `lib/03-gap-matrix.md` (Reuse / Configure / Wrap / Build new / Upstream); needs 5 and 8 first |
| 10 | `/ng-4-design` | strong | `lib/04-design.md` (architecture, contracts, delivery plan) |
| 11 | `/ng-5-implement-slice` | agent mode | code and tests for one slice |

- The legacy track (1–6) and the library track (7–8) can run in parallel; step 9 joins them.
- The extraction prompts end with a "not yet seen" list. Attach those files and re-run.
- **Checkpoints:**
  - After 5: Product and DBA sign off.
  - After 9: no compatibility blocker.
  - After 10: decisions answered.
  - First slice: spike passes the CI and Sonar gates.
  - Last slice: parity confirmed.
- **Status:** I'm starting the legacy and Angular library analysis now. The full prompts are in my runbook document ("Copilot Prompt Runbook: Legacy and Angular Library Analysis").

## 5. Micro frontends: what we covered

- **Definition:** independently built and deployed front-end pieces that a thin shell puts together in the browser at runtime. A library is the opposite: build-time integration, where we install, rebuild and redeploy.
- **Ways to build them:**
  1. **Runtime federation (Native Federation / Module Federation):** shares one copy of Angular; needs matching framework versions.
  2. **Web components (Angular Elements):** a custom tag that any host can use, including a legacy JSP page; each bundles its own Angular.
  3. **iframe:** strong isolation and a quick way to wrap legacy pages; poor UX for sizing, deep links, styling and accessibility.
  4. **Route-based split through the gateway or reverse proxy:** simplest, fully independent apps, but a full page reload between domains.
- **Recommended fit if we choose micro frontends:**
  - Federation for new Angular domains.
  - Route-based or iframe as a temporary bridge to legacy pages.
  - Web components only if a legacy page must host new UI.
- **Native Federation setup outline:**
  - `ng add @angular-architects/native-federation --type remote` for each domain, and `--type dynamic-host` for the shell.
  - A per-environment manifest maps each remote's name to its URL.
  - The shell routes with `loadRemoteModule(...)`.
  - Share only singletons (Angular, RxJS, auth, design system).

## 6. The open decision: libraries vs micro frontends (current framing)

Both choices split the app into vertical slices by business domain, each owned end to end by a domain team, with one framework, one design system and a shared foundation (auth, contracts, monitoring). **The only difference:**
- **Choice 1, micro frontend:** the slice is deployed on its own, and the shell loads it at runtime.
- **Choice 2, library:** the slice is published as a package, and the app bumps the version, builds, runs regression and releases it with all the others.

**Comparison (edge in brackets):**
- **Library has the edge:**
  - Time to first delivery
  - Setup effort
  - Running cost
  - Version safety (compiler checks)
  - Performance
  - Local development
- **Micro frontend has the edge:**
  - Release independence
  - Lead time for one fix
  - Impact of a bad release
  - Integration bottleneck
- **Even:** testing approach, UX consistency.
- Weigh the rows; don't count them. The micro frontend wins the rows tied to today's pain.

**Time to market:**
- Library lead time = slice pipeline + app integration + wait for the next app release.
- Micro frontend lead time = slice pipeline only.
- The gap is the app's release cadence. With daily automated releases the two are close; with weekly or manual-regression releases, micro frontends are clearly faster.

**Choose micro frontends when:**
- Teams need different release schedules.
- Whole-app regression is the bottleneck.
- A defect must not block other domains.
- Domains are loosely coupled.
- There's capacity for a small platform group to own the shell.
- The app keeps growing.

**Choose libraries when:**
- The app can release often with automated regression.
- A shared release is acceptable.
- Domains share a lot of state.
- Platform capacity is limited.
- Fastest start and lowest cost matter most.

**Risk for both:** if domain APIs still deploy as one backend release, neither choice gives real independence for API changes.

**Low-regret path:**
- Build each slice as an Angular library with a route entry point and a public API.
- The app can install it now; a thin wrapper app can later deploy the same library as a remote. The choice can differ per domain.
- **Portability rules:**
  - No imports between slices.
  - Talk through routes and events.
  - Get auth and config through injected services.
  - No global styles.
  - Each slice owns a route prefix.
  - Depend only on the shared foundation.

**Industry guidance (sources):**
- **Thoughtworks Radar:** micro frontends are Adopt (since 2019); "micro frontend anarchy" (mixing frameworks) is Hold.
- **Angular blog (Manfred Steyer, 2025):** check verticals in a monorepo compiled together first; team autonomy in multi-team settings is the main reason to use micro frontends.
- **Nx docs:** use micro frontends when independent deployment is a hard requirement. Avoid them when teams already deploy together. Mismatched shared versions are a leading failure mode.
- Links:
  - https://www.thoughtworks.com/radar/techniques/micro-frontends
  - https://www.thoughtworks.com/radar/techniques/micro-frontend-anarchy
  - https://blog.angular.dev/micro-frontends-with-angular-and-native-federation-7623cfc5f413
  - https://nx.dev/concepts/module-federation/micro-frontend-architecture

**Proposed 4-week POC: build one slice, ship it both ways**
- **Week 1:** build an account-opening step as a library that uses the shared account-opening library.
- **Week 2:** install it in the app and release one change end to end, recording every step and wait.
- **Week 3:** wrap the same library as a remote in a minimal shell and deploy it alone in a lower environment.
- **Week 4:** fill in the scorecard and recommend per domain.
- **Scorecard:**
  - Lead time for a one-line fix
  - Steps and hand-offs per release
  - Setup effort (person-days)
  - Load time and bundle size
  - Effect of a broken slice
  - Rework to switch from library to micro frontend
- **Team (proposed):** 2 engineers, an architect part time, one reviewer per domain team.

**Discussion questions:**
- **Architects:**
  - Can APIs release per domain?
  - How fast can app releases get?
  - Monorepo or package registry?
  - Which pattern for legacy pages?
- **Product:**
  - How often does each domain need to release?
  - Is a shared release window acceptable?
  - How important is a seamless single app?
  - Is account opening the right first slice?
- **Management:**
  - Do teams take full ownership?
  - Is there capacity for a platform group?
  - Can teams agree to lockstep Angular upgrades?
  - Approve the POC?

## 7. High-level architecture (HLA) for micro frontends: key points so far

- **Shell:** login and session, navigation and layout, route map, feature flags, monitoring, error fallback. No business logic.
- **Authentication:**
  - Single sign-on happens once in the shell; the shell holds the session and refreshes the token.
  - Each micro frontend gets the token from a shared auth service or HTTP interceptor and calls its own APIs through the gateway.
  - Route guards are for UX only; real authorization happens in the backend.
  - If the identity setup is unknown, propose OIDC authorization code with PKCE as an assumption.
- **Legacy calls during migration:**
  - The shell's route map plus a feature flag decides whether a route goes to a micro frontend or to legacy.
  - Legacy routes go through the gateway, for example `/legacy/*` on the same origin, carrying the same session or token so users never log in twice.
  - A legacy route is retired once its micro frontend reaches parity.
- **Status:** an HLA document was drafted by voice with placeholders where three diagrams should go: overall architecture, login sequence, legacy routing flow. The diagrams still need adding.
- I also have a Copilot prompt, `mfe-hla.prompt.md`, that reads my current-architecture `.md` file and writes `docs/mfe/hla.md` (20 sections, Mermaid diagrams, assumptions labelled). For best results, my architecture file should describe:
  - How login works today
  - How requests reach the backend
  - Hosting and CI/CD
  - Team ownership

## 8. Artifacts produced (on my other machine or in my downloads)

| File / document | What it is | Status |
|---|---|---|
| `Libraries_vs_Micro_Frontends.pptx` | 14-slide even comparison deck (section 6), with micro frontend pattern diagrams | **Current**; for architects, product, management |
| `Micro_Frontends_Decision_Deck.pptx` | Earlier deck that leaned toward micro frontends | Superseded |
| `Modernization_Plan_One_Slide.pptx` | One-slide plan: today's approach plus the three tracks (section 3) | Done |
| `RepApp_Account_Opening_One_Slide.pptx`, `One_Slide_Plan_Template_nofooter.pptx` | Account opening plan-on-a-page versions | Done |
| Copilot Prompt Runbook (doc) | All 11 ao/ng prompts verbatim, run order, checkpoints | Done |
| HLA doc for micro frontends (doc) | Shell, auth, legacy routing | Diagrams still to add |
| `mfe-hla.prompt.md` | Prompt that generates the HLA from my architecture `.md` | Ready to use |

## 9. Where I left off and next steps

1. Run the legacy and Angular library analysis with the prompt kit (section 4).
2. Present `Libraries_vs_Micro_Frontends.pptx` and collect views from architects, product and management.
3. Write my current-architecture `.md` file and run `/mfe-hla` to produce the HLA.
4. If approved, run the 4-week POC that ships one slice both ways.
5. Keep the three modernization tracks going: Datadog prioritization, the AI loop, Sonar cleanup.

**Unknown so far (ask me if needed):**
- Identity provider and protocol
- Whether the backend APIs can deploy per domain
- The app's current release frequency
- Monorepo vs package registry preference
- Angular versions of our app and the shared library
