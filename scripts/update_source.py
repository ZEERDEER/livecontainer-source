#!/usr/bin/env python3
"""Regenerate apps.json for the LiveContainer source.

Sources:
- GestaltX: huami1314/GestaltX GitHub releases
- Roam Control: seanhowarthdev/Roam-Control GitHub releases
- twoyi: scrape https://twoyi.app/ios/ for the current IPA link

If a fetch fails, the previous entry is kept so a transient error
never wipes an app from the source.
"""

import json
import os
import re
import urllib.request
from datetime import date

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apps.json")

APPS = [
    {
        "name": "GestaltX",
        "bundleIdentifier": "com.huami.gestultx",
        "developerName": "huami1314",
        "subtitle": "MobileGestalt editor",
        "localizedDescription": "MobileGestalt editor for iOS.",
        "kind": "github",
        "repo": "huami1314/GestaltX",
    },
    {
        "name": "Roam Control",
        "bundleIdentifier": "com.roamcontrol",
        "developerName": "seanhowarthdev",
        "subtitle": "Choose, test and move an iPhone's reported location",
        "localizedDescription": "Choose, test and move an iPhone's reported location.",
        "kind": "github",
        "repo": "seanhowarthdev/Roam-Control",
    },
    {
        "name": "twoyi",
        "bundleIdentifier": "app.twoyi",
        "developerName": "weishu",
        "subtitle": "A full Android, inside one app",
        "localizedDescription": "A full Android system inside one app. No jailbreak, no JIT.",
        "kind": "twoyi",
    },
    {
        "name": "Tamio",
        "bundleIdentifier": "sb.moe.tamio",
        "developerName": "zxfccmm4",
        "subtitle": "Native iOS SSH client with Ghostty terminal",
        "localizedDescription": "Native iOS/iPadOS & macOS SSH client with Ghostty terminal, live telemetry charts, SFTP and iCloud sync.",
        "kind": "github",
        "repo": "zxfccmm4/tamio",
        # tag looks like v0.2.21-ios.8 -> version 0.2.21, build 8
        "tag_regex": r"v?([\d.]+)-ios\.(\d+)",
    },
    {
        "name": "WrapPin",
        "bundleIdentifier": "com.suversal.wrappin",
        "developerName": "suversal",
        "subtitle": "iOS 27+ 本机虚拟定位与步行路线测试工具",
        "localizedDescription": "iOS 27+ 本机虚拟定位与步行路线测试工具。",
        "kind": "github",
        "repo": "suversal/WrapPin",
        # two variants are published; Standard is the one signable with a free Apple ID
        "asset_match": "Standard",
    },
    {
        "name": "Nestvane",
        "bundleIdentifier": "com.atomsprout.nestvane",
        "developerName": "atomsprout",
        "subtitle": "Android 17 running inside an iOS app, without JIT",
        "localizedDescription": "Android 17 running inside an iOS app, without JIT.",
        "kind": "github",
        "repo": "atomsprout/nestvane",
    },
]


OFFICIAL_SOURCES = [
    # WQ Files
    "https://raw.githubusercontent.com/kolbicz/WQFiles/main/source.json",
    # INSAV
    "https://raw.githubusercontent.com/ios151/Insav-releases/main/altsource.json",
    # Erosion-CN
    "https://raw.githubusercontent.com/Kianuni/Erosion-CN/main/apps.json",
    # Andarium (Kernarium)
    "https://raw.githubusercontent.com/imxieyi/Kernarium/main/sideload/source.json",
    # SideInstaller (+ Nightflix)
    "https://raw.githubusercontent.com/FrizzleM/SideInstaller/main/frizzlem.json",
]


def fetch_official(url):
    data = json.loads(http_get(url, {"User-Agent": "Mozilla/5.0"}))
    return data.get("apps", [])
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def github_latest(repo, tag_regex=None, asset_match=None):
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.loads(http_get(f"https://api.github.com/repos/{repo}/releases/latest", headers))
    tag = data["tag_name"]
    version = tag[1:] if tag.startswith("v") else tag
    build = None
    if tag_regex:
        m = re.search(tag_regex, tag)
        if m:
            version = m.group(1)
            build = m.group(2) if m.lastindex and m.lastindex >= 2 else None
    ipas = [a for a in data["assets"] if a["name"].lower().endswith(".ipa")]
    if asset_match:
        ipas = [a for a in ipas if asset_match in a["name"]]
    ipa = ipas[0]
    return {
        "version": version,
        "buildVersion": build,
        "versionDate": (data.get("published_at") or "")[:10],
        "downloadURL": ipa["browser_download_url"],
        "size": ipa["size"],
        "versionDescription": (data.get("body") or "")[:2000],
    }


def twoyi_latest():
    html = http_get("https://twoyi.app/ios/", {"User-Agent": "Mozilla/5.0"}).decode("utf-8", "replace")
    m = re.search(r'https://dl\.twoyi\.ai/[^\s"\'<>]+\.ipa', html)
    if not m:
        raise RuntimeError("twoyi IPA link not found on twoyi.app/ios/")
    url = m.group(0)
    fn = url.rsplit("/", 1)[-1]
    vm = re.search(r'twoyi_([\d.]+)_(\d+)\.ipa', fn)
    if not vm:
        raise RuntimeError(f"cannot parse version from {fn}")
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        size = int(r.headers.get("Content-Length") or 0)
    return {
        "version": vm.group(1),
        "buildVersion": vm.group(2),
        "versionDate": date.today().isoformat(),
        "downloadURL": url,
        "size": size,
        "versionDescription": "",
    }


def load_existing():
    try:
        with open(OUT) as f:
            return {a["bundleIdentifier"]: a for a in json.load(f).get("apps", [])}
    except Exception:
        return {}


def main():
    old = load_existing()
    apps = []
    for cfg in APPS:
        kind = cfg["kind"]
        try:
            if kind == "github":
                info = github_latest(cfg["repo"], cfg.get("tag_regex"), cfg.get("asset_match"))
            else:
                info = twoyi_latest()
        except Exception as e:
            print(f"WARN {cfg['name']}: {e}; keeping previous entry")
            if cfg["bundleIdentifier"] in old:
                apps.append(old[cfg["bundleIdentifier"]])
            continue
        entry = {
            "name": cfg["name"],
            "bundleIdentifier": cfg["bundleIdentifier"],
            "developerName": cfg["developerName"],
            "subtitle": cfg["subtitle"],
            "localizedDescription": cfg["localizedDescription"],
            "version": info["version"],
            "versionDate": info["versionDate"],
            "versionDescription": info.get("versionDescription", ""),
            "downloadURL": info["downloadURL"],
            "size": info["size"],
            "versions": [
                {
                    "version": info["version"],
                    "date": info["versionDate"],
                    "localizedDescription": info.get("versionDescription", ""),
                    "downloadURL": info["downloadURL"],
                    "size": info["size"],
                }
            ],
        }
        if info.get("buildVersion"):
            entry["buildVersion"] = info["buildVersion"]
            entry["versions"][0]["buildVersion"] = info["buildVersion"]
        apps.append(entry)
        print(f"OK {cfg['name']}: {info['version']} ({info['downloadURL']})")

    # Merge in apps from official sources (mirrored verbatim).
    auto_ids = {a["bundleIdentifier"] for a in apps}
    old_official = [a for bid, a in old.items() if bid not in auto_ids]
    official_apps = []
    official_failed = False
    for url in OFFICIAL_SOURCES:
        try:
            got = fetch_official(url)
            print(f"OK official {url}: {len(got)} apps")
            official_apps.extend(got)
        except Exception as e:
            official_failed = True
            print(f"WARN official {url}: {e}; keeping previous entries")
    seen = set()
    merged = []
    for a in apps + official_apps:
        bid = a.get("bundleIdentifier")
        if bid in seen:
            continue
        seen.add(bid)
        merged.append(a)
    if official_failed:
        for a in old_official:
            if a["bundleIdentifier"] not in seen:
                seen.add(a["bundleIdentifier"])
                merged.append(a)
    apps = merged

    src = {
        "name": "ZEERDEER",
        "identifier": "com.zeerdeer.livecontainer.source",
        "subtitle": "自用自动更新源",
        "description": "全部应用的自动更新源：每天同步官方源并检查上游新版本。",
        "website": "https://github.com/ZEERDEER/livecontainer-source",
        "apps": apps,
    }
    with open(OUT, "w") as f:
        json.dump(src, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {OUT} with {len(apps)} apps")


if __name__ == "__main__":
    main()
