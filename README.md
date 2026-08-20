# Legacy → Angular Spec Extraction Kit (GitHub Copilot)

Prompt files for reverse-engineering feature specifications out of a legacy Struts/JSP/Spring Boot
application, so specs — not legacy code — become the input to your AI workbench.

## Install

Copy `.github/` into the root of the **legacy** repository. In VS Code, open Copilot Chat, switch to
**Agent mode**, and the prompts appear as slash commands. (Visual Studio uses `#prompt:<name>`
instead of `/<name>`.)

Pick a reasoning-capable model in the model picker. This is analysis work, not completion — the fast
cheap models summarize where you need them to enumerate.

## Workflow

Recon runs **once per application**. Extraction runs **once per feature**.

```
/recon-1-inventory          → docs/APP-PROFILE.md §1-2   stack, request lifecycle
/recon-2-layers             → docs/APP-PROFILE.md §3-4   layers, where logic lives
/recon-3-data               → docs/APP-PROFILE.md §5-7   SQL, session, integrations
/recon-4-features           → docs/APP-PROFILE.md §8-10  feature index, glossary, risks
                                                          + interview questions

        ── HUMAN GATE ──  review the profile, answer the questions, edit the file

/recon-5-generate-extractor → rewrites extract-feature-spec.prompt.md with your app's real
                              paths, conventions, lifecycle diagram, and glossary

        ── then, per feature ──

/extract-feature-spec       → docs/specs/<feature>/TRACE.md  then  SPEC.md

        ── HUMAN GATE ──  resolve open questions, sign off parity decisions

        → hand SPEC.md to the Angular build session
```

## The two gates

Both exist because errors compound.

**Gate 1, after recon.** A wrong fact in the profile propagates into every feature spec you
generate afterward. Read it. Fix it by hand where needed. Then paste the condensed conventions and
glossary into `.github/copilot-instructions.md` so every later session inherits them.

**Gate 2, after each spec.** If section 20 (Open Questions) is non-empty, the spec doesn't go to
implementation. Section 17 (Parity Decisions) needs a business SME who remembers *why* the dropdown
is sorted that way — that's the one part the agent genuinely cannot do.

## Why it's split into phases

A large legacy repo will not fit in one Copilot session. Each phase writes its output to disk and
the next reads it back, so quality doesn't degrade as context fills. Same reason extraction runs in
two passes: `TRACE.md` (raw, complete, ugly) then `SPEC.md` (structured, from the trace).

If a phase still runs out of room, scope it to a module and run it twice.

## Keep the code-gen session separate

Never let one session read legacy code *and* emit Angular. The spec is the review checkpoint, and
mixing the two skips it — you also get Struts idioms smuggled into the new app. The build session
should see `SPEC.md` and your project constitution, nothing else.

## Tuning it

The first feature is a calibration run. Do it manually alongside the agent, then diff. Whatever the
agent missed, add as an explicit step — it will keep missing the same class of thing otherwise.

Also supplement static extraction with a runtime pass: walk the feature with devtools open, save the
HAR, enable SQL logging, and force every error path you can. Behavior that only appears at runtime
is invisible to any amount of code reading.
