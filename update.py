#!/usr/bin/env python3
"""
Keeps Mosaic's copy of the Nanakshahi Jantri (SGPC calendar) data up to date.

The data comes from janpreet/nanakshahi-ical (MIT licence; engine: janpreet/nanakshahi-jantri), which
publishes every printed Jantri year as "confirmed" and the next few years as "estimated" from an
astronomical model calibrated against the printed ones.

The same script lives in two places:
  * the public mosaic-data repo (as update.py): TVs download its sgpc-calendar.json about once a week
    (SGPC_CALENDAR_URL in SgpcUpdater.kt), and its workflow runs this monthly and opens a pull request;
  * the Mosaic app repo (tools/sgpc_calendar.py): it also refreshes the copy bundled in the app.

    python3 -I update.py update    # fetch the latest, check it, write the file(s)
    python3 -I update.py check     # check sgpc-calendar.json without changing it
"""
import datetime
import json
import os
import sys
import urllib.request

SOURCE = "https://janpreet.github.io/nanakshahi-ical/data.json"
HERE = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(HERE)
IN_APP_REPO = os.path.isdir(os.path.join(APP_ROOT, "app", "src", "main", "assets"))
# In the app repo: the mosaic-data checkout beside the app, plus the bundled asset. In mosaic-data: next to the script.
MIRROR = os.path.join(APP_ROOT, "mosaic-data", "sgpc-calendar.json") if IN_APP_REPO else os.path.join(HERE, "sgpc-calendar.json")
ASSET = os.path.join(APP_ROOT, "app", "src", "main", "assets", "sgpc-calendar.json") if IN_APP_REPO else None
MONTHS = ["Chet", "Vaisakh", "Jeth", "Harh", "Sawan", "Bhadon", "Assu", "Katak", "Maghar", "Poh", "Magh", "Phagan"]
CATEGORIES = {"gurpurab", "bhagat", "historical", "civil"}


def day(s):
    return datetime.date.fromisoformat(s)


def check(data):
    """Raises ValueError on anything the app would reject; returns one summary line per year."""
    if not isinstance(data.get("years"), dict) or not data["years"]:
        raise ValueError("no years")
    lines = []
    for key, y in sorted(data["years"].items()):
        ns = y.get("nsYear")
        if str(ns) != key or not isinstance(ns, int) or ns < 549:
            raise ValueError(f"year {key}: bad nsYear")
        if y.get("status") not in ("confirmed", "estimated"):
            raise ValueError(f"{ns}: bad status")
        months = y.get("months") or []
        if [m.get("name") for m in months] != MONTHS:
            raise ValueError(f"{ns}: months must be Chet…Phagan")
        starts = [day(m["start"]) for m in months]
        nxt = day(y["nextChet"])
        for a, b in zip(starts, starts[1:] + [nxt]):
            if not 29 <= (b - a).days <= 32:
                raise ValueError(f"{ns}: month starting {a} is {(b - a).days} days")
        n = 0
        for e in y.get("events") or []:
            d = day(e["date"])
            if not starts[0] <= d < nxt:
                raise ValueError(f"{ns}: {e.get('id')} on {d} is outside the year")
            if e.get("category") not in CATEGORIES or not str(e.get("pa", "")).strip():
                raise ValueError(f"{ns}: {e.get('id')} has a bad category or no Punjabi name")
            if e.get("status") not in ("confirmed", "estimated") or not 1 <= int(e.get("span", 1)) <= 3:
                raise ValueError(f"{ns}: {e.get('id')} has a bad status or span")
            n += 1
        lines.append(f"  Samvat {ns} ({starts[0]} – {nxt - datetime.timedelta(days=1)}): {y['status']}, {n} days")
    return lines


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "update":
        req = urllib.request.Request(SOURCE, headers={"User-Agent": "Mosaic-calendar-mirror/1"})
        data = json.load(urllib.request.urlopen(req, timeout=60))
        lines = check(data)
        text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        for path in [p for p in (MIRROR, ASSET) if p]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        print(f"Updated from {SOURCE} (generated {data.get('generated')}):")
    elif cmd == "check":
        data = json.load(open(MIRROR, encoding="utf-8"))
        lines = check(data)
        print(f"{MIRROR} is valid (generated {data.get('generated')}):")
    else:
        sys.exit(__doc__)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
