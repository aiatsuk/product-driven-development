---
name: product-driven-development
description: "Maintain product-level memory as Markdown above repositories, tickets, and AI chats. Use when selecting a product, recovering prior context, browsing active work, recording durable results or decisions, or verifying missing, conflicting, or exact details against a named native Codex, Claude, or Grok session."
---

# Product-Driven Development

Treat product knowledge as a small, human-readable document workspace above code repositories and
external tools. Read the relevant documents before work, record important results at natural
checkpoints, and use those documents in later tasks.

No lifecycle hook, database, daemon, background index, or automatic session binding is required.
The skill is the operating contract; Markdown files are the memory. A bundled read-only helper is
used only for exact native-session evidence fallback.

## User interaction

The portable explicit entry point is `$product-driven-development`. Natural-language requests work
too. Some hosts pass text such as `/product list` through to the agent; interpret it as the same
semantic request when it reaches you, but do not claim that the plugin registers a native slash
command. Hosts that reserve top-level slash commands may reject `/product` before the agent can
see it; use the explicit skill invocation there.

Interpret these user intents whether they arrive through the skill invocation or natural language:

- list products - list products from the workspace root;
- use or select `<product>` - select logical product context for this conversation and load its
  `product.md` plus `memory.md`;
- show status for `[project-or-ticket]` - read its documents and refresh external status only when
  the user asks for current data;
- show `<id>` - show the matching product, project, ticket, note, decision, or knowledge
  document;
- search for `<text>` - search product Markdown first, then linked sources when needed;
- note `<result>` - capture one important milestone using the artifact template;
- remember `<fact>` - add a reviewed reusable fact to the narrowest suitable document;
  use `memory.md` only for cross-project knowledge.

Examples: `$product-driven-development list my products`, `Use the storefront product`, or `Show
active projects for checkout`. If the host passes it through, `/product list` has the same meaning
as the first example.

## Workspace

Use `${PRODUCT_MEMORY_HOME}` when set, otherwise:

```text
~/.local/share/product-driven-development/products/
```

Each direct child is one product. Prefer this layout for new documents:

```text
<product>/
  product.md                         stable product map, owners, paths, authoritative links
  memory.md                          compact durable knowledge used in most product tasks
  projects/<id>/
    project.md                       outcome, scope, links, related repositories and tickets
    status.md                        current local status, blockers, next action
    notes/YYYY-MM-DD-HHMM-<slug>.md  discoveries, results, discussions, handoffs
  tickets/<id>/
    ticket.md
    status.md
    notes/YYYY-MM-DD-HHMM-<slug>.md
  knowledge/<slug>.md                reusable product facts and runbooks
  decisions/<slug>.md                explicit proposed or accepted decisions
  sessions/<host>-<session-id>.md    explicit binding plus optional curated session summary
```

Existing JSON, SQLite indexes, or imported raw transcripts are legacy evidence. Do not use them as
an automatic fallback, and do not rewrite or delete them unless the user explicitly asks for a
migration. The original host-managed session remains the preferred source evidence.

Read [references/artifacts.md](references/artifacts.md) before creating a new product, project,
ticket, note, decision, or session summary.

## Start work

1. List product directories and their `product.md` files.
2. Use the product explicitly named by the user. If none is named and several are plausible, show
   the short list and ask which one to use. Never infer from a globally latest chat.
3. Read `product.md` and `memory.md`, then the relevant Project/Ticket documents and newest notes.
4. Search with `rg` before claiming that context, a key, link, decision, or earlier result is absent.
5. Refresh volatile facts from their owning system when the user asks for current status. Issue
   trackers, documentation and design systems, repositories, CI, and dashboards remain authoritative.
6. If a mandatory evidence-fallback condition remains after curated search, follow the native
   session procedure below.

Product selection is logical context for the current conversation; it does not change the shell
working directory and does not require a persistent host-session binding.

## Native session evidence fallback

Use curated knowledge first. Native fallback is mandatory only when:

- the user names an exact session or asks for exact wording/provenance;
- the required detail is absent;
- the relevant record is marked candidate, unverified, stale, or partial;
- curated sources conflict; or
- a session summary may not cover the current native source.

Do not read native files when a confirmed/accepted curated answer is sufficient, has no
stale/conflict marker, and exact sourcing was not requested. A transcript describes historical
discussion; current issue, PR/CI, documentation, design, code, config, and rollout state must still be
checked in their owning systems.

Before native access, read [references/session-evidence.md](references/session-evidence.md). Both
helper commands require the selected product root and exact `host + session_id`. Use a linked
`sessions/<host>-<session-id>.md` binding. Use `--allow-unbound` only for a one-time check when the
user explicitly supplied that exact session in the selected-product context; it cannot override a
revoked or malformed binding.

```text
python3 <skill-root>/scripts/session_evidence.py inspect \
  --host <codex|claude|grok> --session-id <uuid> --product-root <product-root>

python3 <skill-root>/scripts/session_evidence.py search \
  --host <codex|claude|grok> --session-id <uuid> --product-root <product-root> \
  --query <literal>
```

Use `--scope messages-and-tools` only when the requested fact is likely to exist in visible tool
results rather than messages. Never search tool arguments, system/developer prompts, reasoning, or
unknown fields. The helper performs fixed-limit literal search and returns bounded sanitized JSON;
it never copies or modifies a transcript.

Report the evidence outcome, independent source state and coverage state, exact host/session and
line or event coordinates, observation time, and limitations. Say that the local original was
checked only when native access actually succeeded. If content is unavailable, ambiguous,
truncated, partial, or redacted, say so instead of filling the gap from inference.

The complete transcript stays in native host storage. Use targeted bounded searches rather than
placing a whole long transcript into one model context or Product Workspace.

## Record important moments

At the next natural checkpoint, create or update the smallest useful Markdown artifact when work
produces something a later task should know:

- an accepted or rejected decision;
- a durable product fact, architecture boundary, or constraint;
- a completed result or verification outcome;
- a blocker, risk, open question, or next action;
- a reusable repository path, PR, ticket, design document, config, experiment, dashboard,
  command, or runbook;
- a handoff, pause, compaction, or end-of-task summary.

Use the narrowest owner:

- Project note for project-wide work;
- Ticket note for ticket-specific work;
- `knowledge/` for reusable facts across work items;
- `decisions/` only for an explicit decision, keeping it `proposed` until the user accepts it;
- `sessions/<host>-<session-id>.md` for an explicitly linked session and its curated navigation
  summary;
- `memory.md` only for compact facts useful in many future product tasks.

Batch one coherent milestone into one note. Link to AI Factory, spec-driven, code, PR, issue tracker,
design, or session-binding artifacts instead of copying them. Record reviewed paraphrases and
provenance, not raw logs or a chat dump. Never store secrets, credentials, private key material, or
sensitive payloads.

If the user requested read-only work or prohibited writes, do not create a note. Present the exact
result in chat and say what would normally be captured.

## Finish and resume

Before ending writable product work, make sure the owning `status.md` or latest note states:

- what was requested;
- what changed or was learned;
- decisions, clearly separated into accepted and proposed;
- evidence and reusable links;
- verification performed;
- blockers or open questions;
- one concrete next action.

To resume, read the product map, owning Project/Ticket, its status, and newest notes. Do not redo a
finished investigation merely because the original chat is unavailable.

## Integration with delivery frameworks

AI Factory and spec-driven remain responsible for their own detailed artifacts and gates. Product
memory only links them to the owning Product/Project/Ticket and records the durable outcome, current
status, and next action. A product note never grants approval to implement, commit, push, publish,
deploy, merge, or modify an external system.
