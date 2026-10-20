#!/usr/bin/env python3
"""Offline checks for the deliberately small Trunk distribution package."""

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ".agents/plugins/marketplace.json",
    "plugins/trunk/.codex-plugin/plugin.json",
    "plugins/trunk/.app.json",
    "README.md",
    "scripts/check-package.py",
}
APP_ID = "asdk_app_6ad6edd703888191938b9a0e53307965"
WEBSITE = "https://trunk.dev"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=object_pairs)


def local_path(base, value):
    require(isinstance(value, str) and value.startswith("./"), "Expected ./ path")
    path = (base / value).resolve()
    require(path.is_relative_to(base.resolve()), f"Path escapes package: {value}")
    require(path.exists(), f"Missing referenced path: {value}")
    return path


def main():
    # Include untracked files so accidental additions are caught before staging.
    paths = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    ).decode().split("\0")
    actual = set(filter(None, paths))
    require(actual == EXPECTED, f"Unexpected/missing files: {actual ^ EXPECTED}")
    for relative in EXPECTED:
        path = ROOT / relative
        require(path.is_file() and not path.is_symlink(), f"Not a plain file: {relative}")

    marketplace = read_json(ROOT / ".agents/plugins/marketplace.json")
    require(marketplace == {
        "name": "trunk",
        "interface": {"displayName": "Trunk"},
        "plugins": [{
            "name": "trunk",
            "source": {"source": "local", "path": "./plugins/trunk"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Developer Tools",
        }],
    }, "Marketplace contract changed")
    plugin_root = local_path(ROOT, marketplace["plugins"][0]["source"]["path"])
    plugin = read_json(plugin_root / ".codex-plugin/plugin.json")
    require(set(plugin) == {
        "name", "version", "description", "author", "apps", "interface", "homepage",
    }, "Unexpected plugin fields; review any new dependencies")
    require(plugin["name"] == "trunk" and plugin["version"] == "0.1.1", "Plugin identity/version")
    require(plugin["author"] == {"name": "Trunk", "url": WEBSITE}, "Author branding")
    require(plugin["homepage"] == WEBSITE, "Homepage")
    require(plugin["apps"] == "./.app.json", "App manifest location")
    app = read_json(local_path(plugin_root, plugin["apps"]))
    require(app == {"apps": {"trunk": {"id": APP_ID}}}, "Registered app mapping changed")

    ui = plugin["interface"]
    require(set(ui) == {
        "displayName", "shortDescription", "longDescription", "developerName",
        "category", "capabilities", "defaultPrompt", "websiteURL",
    }, "Unexpected interface fields; inspect referenced assets if adding them")
    for key in ("displayName", "developerName"):
        require(ui[key] == "Trunk", f"Branding: {key}")
    require(ui["websiteURL"] == WEBSITE, "Website link")
    require(ui["category"] == "Developer Tools", "Plugin category")
    require(ui["capabilities"] == ["Interactive", "Read", "Write"], "Capabilities changed")
    for value in [plugin["description"], ui["shortDescription"], ui["longDescription"]]:
        require(isinstance(value, str) and value.strip(), "Description must be nonempty")
    require(isinstance(ui["defaultPrompt"], list) and len(ui["defaultPrompt"]) == 3,
            "Expected three prompts")
    require(all(isinstance(p, str) and p.strip() for p in ui["defaultPrompt"]), "Empty prompt")
    require("balearic" not in json.dumps([marketplace, plugin]).lower(), "Stale visible branding")

    readme = (ROOT / "README.md").read_text()
    for setting in [
        WEBSITE, APP_ID, ".agents/plugins/marketplace.json",
        "plugins/trunk/.codex-plugin/plugin.json", "./plugins/trunk", "./.app.json",
        "https://github.com/balearic-labs/trunk-chatgpt-plugin",
        "https://github.com/mettke/trunk-chatgpt-plugin",
        "Leave unset", "accepted release ref", "trunk_whoami",
    ]:
        require(setting in readme, f"Installation documentation missing: {setting}")
    print("PASS: 3 JSON manifests, package paths, app mapping, branding, website,")
    print("      installation settings and 5-file public artifact allowlist.")
    print("Live import, installation, authentication and MCP reads are not tested.")


if __name__ == "__main__":
    main()
