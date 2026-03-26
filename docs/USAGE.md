# Desloppify Usage

This repository contains the active Rust implementation of `desloppify`.

Use the checkout-local launcher when you want to guarantee that you are running
this repo's Rust CLI instead of an older binary or the archived Python fork:

```bash
/Users/xyra/Documents/desloppify/scripts/desloppify-local --help
```

That launcher works from any current working directory. It always executes the
Rust workspace in this checkout.

## Which Entry Point To Use

Use one of these two entry points:

```bash
/Users/xyra/Documents/desloppify/scripts/desloppify-local ...
```

```bash
cargo install --path /Users/xyra/Documents/desloppify/crates/deslop-cli --force
desloppify ...
```

Avoid these paths unless you intentionally want legacy behavior:

- Do not use `archive/forked-desloppify-python/`.
- Do not `pip install desloppify`.
- Do not assume a preexisting bare `desloppify` on your machine points at this checkout.

## What Desloppify Writes

Desloppify writes project state under the target repo's `.desloppify/` folder.

- `.desloppify/state.json`: latest scan state and finding history
- `.desloppify/config.json`: persisted config such as excludes
- `.desloppify/`: review packets and related workflow artifacts

If you scan the same project repeatedly, keep that directory. It is how the tool
tracks fixed findings, reopeners, and plan state over time.

## Safe First Pass On A New Codebase

Run the tool in this order:

```bash
DESLOP=/Users/xyra/Documents/desloppify/scripts/desloppify-local
TARGET=/absolute/path/to/codebase

$DESLOP scan --path "$TARGET"
$DESLOP status --path "$TARGET"
$DESLOP queue --path "$TARGET"
$DESLOP plan show --path "$TARGET"
$DESLOP next --path "$TARGET"
```

What each command is for:

- `scan`: collect findings and refresh `.desloppify/state.json`
- `status`: see overall scores and project summary
- `queue`: inspect prioritized work items
- `plan show`: inspect the current living plan
- `next`: ask the tool for the next recommended action

`plan` and actionable `review` commands require an existing completed scan.
Start with `scan`, not `review`.

## Excluding Noise Before You Scan

Persist exclusions for vendored, generated, build, archive, or migration trees:

```bash
DESLOP=/Users/xyra/Documents/desloppify/scripts/desloppify-local
TARGET=/absolute/path/to/codebase

$DESLOP exclude add --path "$TARGET" node_modules
$DESLOP exclude add --path "$TARGET" dist
$DESLOP exclude add --path "$TARGET" build
$DESLOP exclude add --path "$TARGET" vendor
$DESLOP exclude add --path "$TARGET" archive
$DESLOP exclude list --path "$TARGET"
```

You can also pass one-off exclusions during a scan:

```bash
$DESLOP scan --path "$TARGET" --exclude node_modules --exclude dist
```

Prefer persisted excludes for real codebases so later scans and LLM review use
the same scope.

## Common Investigation Commands

Inspect findings:

```bash
$DESLOP show --path "$TARGET"
$DESLOP show --path "$TARGET" --tier 1
$DESLOP show --path "$TARGET" --detector long_function
$DESLOP show --path "$TARGET" --file src/
```

Resolve a finding after you intentionally fixed or dismissed it:

```bash
$DESLOP resolve --path "$TARGET" --status fixed finding_id_here
$DESLOP resolve --path "$TARGET" --status wontfix finding_id_here --note "Intentional tradeoff"
```

Run a single detector when debugging tool behavior:

```bash
$DESLOP detect --path "$TARGET" long_function
```

Generate artifacts for inspection:

```bash
$DESLOP tree --path "$TARGET"
$DESLOP viz --path "$TARGET" --output "$TARGET/desloppify-report.html"
```

Check current language support:

```bash
$DESLOP langs
```

## Mutating Commands

Treat these as opt-in:

```bash
$DESLOP fix --path "$TARGET" --dry-run
$DESLOP move --path "$TARGET" --dry-run src/old.rs src/new.rs
```

Only run the non-dry-run form after you inspect the proposed changes.

## LLM Review Workflow

Use review only after a fresh scan:

```bash
$DESLOP review --prepare --path "$TARGET"
$DESLOP review --run-batches --backend codex --mode findings_only --path "$TARGET"
```

Important review constraints:

- `review --run-batches` currently supports the in-process Codex backend only.
- Non-Codex reviewers should go through `review --external-start --runner ...`.
- `--mode findings_only` is the safest default.
- `--mode trusted` applies subjective assessments into the persisted score surface.
- `--force-review-rerun` is only for intentionally stale contexts.

If you want to hand review to another tool instead of the built-in Codex path:

```bash
$DESLOP review --external-start --runner claude --path "$TARGET"
```

Follow the generated instructions to submit the result back with
`review --external-submit ... --import`.

## Polyglot Repositories

Auto-detect is convenient, but mixed-language monorepos often need explicit
scoping.

Use one of these patterns:

```bash
$DESLOP scan --path "$TARGET" --lang rust
```

```bash
$DESLOP scan --path "$TARGET/services/api" --lang rust
$DESLOP scan --path "$TARGET/web" --lang typescript
```

If a repo has multiple independent language roots, scan each root separately
instead of assuming one top-level auto-detect pass captures everything well.

## What Not To Do

- Do not start with `review`.
- Do not use `--mode trusted` casually.
- Do not scan vendored or archived trees unless you mean to.
- Do not assume `fix` or `move` are safe without `--dry-run`.
- Do not use the archived Python fork as the default execution path.

## LLM Handoff

If another LLM will operate this tool for you, hand it
`docs/LLM_RUNBOOK.md` from this repo. That file contains a copy-paste prompt
and an explicit execution policy for safe first use on another codebase.
