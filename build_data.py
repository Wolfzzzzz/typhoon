#!/usr/bin/env python3
# 由 Mac 定时运行：抓取中央气象台(nmc)台风数据，解析后写成同源 JSON 快照，供 GitHub Pages 前端直接读取。
# 这样前端无需浏览器直连 nmc（避开跨域/境外 IP 限制），数据来自 GitHub Pages 同源，必然可达。
import urllib.request, json, time, os, sys

BASE = "http://typhoon.nmc.cn/weatherservice/typhoon/jsons"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DEFAULT_ID = 3257931  # 巴威 BAVI

LEVEL_CN = {
    "TD": "热带低压", "TS": "热带风暴", "STS": "强热带风暴",
    "TY": "台风", "STY": "强台风", "SuperTY": "超强台风",
}
RADII_MAP = {"30KTS": "7", "50KTS": "10", "64KTS": "12"}


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def unwrap(raw):
    i = raw.index("(")
    rest = raw[i + 1:]
    while rest.endswith(")"):
        rest = rest[:-1]
    return json.loads(rest)


def parse_dt(ts):
    try:
        return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}"
    except Exception:
        return ts


def parse_view(data):
    t = data["typhoon"]
    tid, en, cn = t[0], t[1], t[2]
    status = t[7] if len(t) > 7 else None
    raw_pts = t[8] if len(t) > 8 else []
    points = []
    for p in raw_pts:
        try:
            radii = {}
            for r in (p[10] or []):
                label = RADII_MAP.get(r[0], r[0])
                radii[label] = [r[1], r[2], r[3], r[4]]
            points.append({
                "time": parse_dt(p[1]), "ts": p[2], "level": p[3],
                "level_cn": LEVEL_CN.get(p[3], p[3]),
                "lon": p[4], "lat": p[5], "pressure": p[6], "wind": p[7],
                "move_dir": p[8], "move_speed": p[9], "radii": radii,
            })
        except Exception:
            continue
    forecast = []
    if raw_pts:
        try:
            fc = raw_pts[-1][11] or {}
            for f in fc.get("BABJ", []):
                forecast.append({
                    "hour": f[0], "time": f[1], "lon": f[2], "lat": f[3],
                    "pressure": f[4], "wind": f[5], "level": f[7],
                    "level_cn": LEVEL_CN.get(f[7], f[7]),
                })
        except Exception:
            pass
    return {"id": tid, "en": en, "cn": cn, "status": status,
            "points": points, "forecast": forecast}


def gen(tid):
    raw = fetch(f"{BASE}/view_{tid}")
    d = parse_view(unwrap(raw))
    d["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    d["source"] = "nmc-snapshot"
    return d


def main():
    os.makedirs(OUT, exist_ok=True)
    ids = {DEFAULT_ID}
    # 拉取当前活动台风列表，一并生成
    try:
        lst = unwrap(fetch(f"{BASE}/list_default"))
        for row in lst.get("typhoonList", []):
            try:
                ids.add(int(row[0]))
            except Exception:
                pass
    except Exception as e:
        print("list_default 失败，仅生成默认台风:", e, file=sys.stderr)

    written = []
    for tid in sorted(ids):
        try:
            d = gen(tid)
            path = os.path.join(OUT, f"{tid}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=1)
            written.append(tid)
            print(f"  ✓ {tid} {d.get('cn')} {d.get('en')} 点={len(d['points'])}")
        except Exception as e:
            print(f"  ✗ {tid} 失败: {e}", file=sys.stderr)

    # 活动列表快照
    try:
        active = []
        for tid in written:
            with open(os.path.join(OUT, f"{tid}.json"), encoding="utf-8") as f:
                d = json.load(f)
            active.append({"id": d["id"], "cn": d.get("cn"), "en": d.get("en"),
                           "status": d.get("status"), "generated_at": d.get("generated_at")})
        with open(os.path.join(OUT, "list.json"), "w", encoding="utf-8") as f:
            json.dump({"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                       "typhoons": active}, f, ensure_ascii=False, indent=1)
        print(f"list.json 已写（{len(active)} 个）")
    except Exception as e:
        print("list.json 失败:", e, file=sys.stderr)

    print(f"完成，生成 {len(written)} 个台风快照。")


if __name__ == "__main__":
    main()
