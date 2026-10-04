# Product Driven Development

Product Driven Development is a self-contained skill and plugin for maintaining curated product knowledge above repositories, tickets, and AI sessions. Product context stays in small human-readable Markdown files and exact native-session evidence is queried only through a bounded read-only helper.

## Included

- a portable product, project, ticket, note, decision, and knowledge workspace contract;
- explicit product selection with no implicit latest-session binding;
- curated-first recall and conflict handling;
- bounded read-only evidence lookup for named Codex, Claude, and Grok sessions;
- Codex and Claude plugin manifests;
- unit tests for the plugin bundle and evidence helper.

## Use

Install this repository with your host's normal plugin workflow. The root contains a Codex manifest in `.codex-plugin/plugin.json` and a Claude-compatible manifest and marketplace entry in `.claude-plugin/`.

Invoke `$product-driven-development`, or ask naturally to list products, select one, inspect current work, record a milestone, or verify an exact fact against a named native session.

## Verification

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m unittest discover -s skills/product-driven-development/tests -p 'test_*.py' -v
python3 scripts/public_check.py
```

The public check rejects Cyrillic text, vendor-specific material, machine-specific paths, secret-like values, and unsafe generated files.

## Releasing

Every merged version is a git tag `vX.Y.Z` on `main` and a GitHub Release whose notes are that version's `CHANGELOG.md` section.

1. In the release pull request, bump every version file (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, and the pin in `tests/test_plugin_bundle.py`) and add a `## X.Y.Z — YYYY-MM-DD` section to `CHANGELOG.md`. `python3 scripts/release.py check --tag vX.Y.Z` confirms they agree.
2. After merge, tag the merged main commit and push the tag:

   ```bash
   git tag -a vX.Y.Z -m "product-driven-development X.Y.Z" <merged main sha>
   git push origin vX.Y.Z
   ```

3. The `Release` workflow checks the versions, runs the tests, and publishes the GitHub Release with the changelog section as notes.
4. To republish the release for an existing tag, run `gh workflow run release.yml -f tag=vX.Y.Z`.

## Privacy and portability

The helper opens native host sessions read-only, requires an exact session identity and selected product, applies fixed limits, searches only allowlisted visible fields, and returns bounded sanitized output. The plugin contains no credentials, lifecycle hooks, database, daemon, or bundled product data.

No license is included because the original source did not specify one.
