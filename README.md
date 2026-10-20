# Trunk for ChatGPT

Use [Trunk](https://trunk.dev) to inspect repositories and Change state and
prepare change proposals through Trunk's existing policy and review lifecycle.
This repository contains plugin packaging, not the Trunk service.

## Package

| File | Purpose |
| --- | --- |
| `.agents/plugins/marketplace.json` | Trunk marketplace; resolves `./plugins/trunk` from the repository root |
| `plugins/trunk/.codex-plugin/plugin.json` | Trunk listing and `https://trunk.dev` website metadata |
| `plugins/trunk/.app.json` | Existing authenticated Trunk app dependency |

The plugin keeps the supported `.codex-plugin/plugin.json` compatibility format.
Its `apps` path, `./.app.json`, resolves from `plugins/trunk`, not from
`.codex-plugin`. No icons, screenshots or other external assets are referenced.
The package contains no MCP server implementation, OAuth configuration or secrets.

The registered app mapping is:

```text
apps.trunk.id = asdk_app_6ad6edd703888191938b9a0e53307965
```

That app ID is not a marketplace listing ID. Installation reuses the registered
app; it does not provision another MCP server or grant new Trunk permissions.

## Import and installation

Use a ChatGPT surface and account/workspace that supports repository plugin
marketplaces and permits the existing Trunk app. Availability varies by surface
and workspace policy; a public GitHub repository does not establish eligibility.
You also need a Trunk account with access to the organization/repository you
intend to use. If workspace controls block the app or repository import, ask the
workspace administrator to verify eligibility before proceeding.

For an approved import, use these settings:

| Setting | Value |
| --- | --- |
| Distribution repository, after acceptance and publication | `https://github.com/balearic-labs/trunk-chatgpt-plugin` |
| Ref | The accepted release ref; use `main` only after it contains the accepted package |
| Marketplace file | `.agents/plugins/marketplace.json` |
| Repository root / sparse path | Leave unset; import the full repository |
| Plugin source | `./plugins/trunk` (already declared in the marketplace) |

Review candidates live at `https://github.com/mettke/trunk-chatgpt-plugin`.
An explicitly authorized candidate import must select its exact review branch
and record the resolved commit, using the same file/root settings above.
Neither repository being present nor this README means a release or source
cutover has happened. Do not select the plugin subdirectory as the repository
root: that excludes the marketplace file.

1. In the supported ChatGPT plugin marketplace UI, add the approved repository
   and ref, then import/sync it.
2. Open **Trunk** and check the listing, website and existing Trunk app dependency.
3. Install/select the plugin. Complete authentication only if required; keep
   an existing working Trunk connection instead of recreating or revoking it.
4. Start a fresh supported ChatGPT session and select Trunk. Verify identity
   with `trunk_whoami`, then perform one bounded read of an authorized repository.
   Do not use a write operation as the installation smoke test.

Record the repository, configured ref, resolved commit, host/workspace, listing
and app dependency, install outcome, authentication outcome, and actual read
result separately. Repository checks cannot prove these live acceptance steps.
ChatGPT acceptance also does not establish Codex Cloud compatibility.

## If installation is unavailable

If **Install** is disabled, capture the host, account/workspace eligibility,
selected repository/ref and exact visible error or disabled state. Ask the
workspace/plugin administrator to investigate the observed restriction.
Do not assume repository migration or adding the website field fixes it.
Do not change OAuth, app permissions or connections to work around an unknown
cause. Redact credentials and private repository content from support reports.

Source cutover is a separate approved action after replacement acceptance.
Keep the previous packaging and working connection available until then.

## Packaging checks

After independent review, run from this repository:

```sh
python3 scripts/check-package.py
git diff --check
```

The dependency-free check validates this package's JSON shapes, relative paths,
app identity, branding, website metadata, documentation settings and distributable
file allowlist. It is a focused contract check, not an official host schema
validator or a live installation test. Inspect every changed public file as part
of review. No Trunk application build or full application validation is required.

Manifest/path reference:
[OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins).
