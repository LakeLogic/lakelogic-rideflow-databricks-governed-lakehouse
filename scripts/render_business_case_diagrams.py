"""Render the two diagrams in docs/business-case.md, in light and dark SVG.

- rideflow_systems_{light,dark}.svg: domains sized by contract count, with the Shared
  products they feed (dependencies read from each Shared contract's table paths).
- rideflow_ontology_{light,dark}.svg: business entities sized by how many Silver
  contracts carry their key.

Every size and dependency is counted from contracts/, so re-run after contract changes:
    python scripts/render_business_case_diagrams.py
"""
import math
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent
CONTRACTS = REPO / "contracts"
OUT = REPO / "docs" / "images"
SILVER = list(CONTRACTS.glob("*/*/contracts/silver/*.yaml"))

THEMES = {
    "light": dict(bg="#FFFFFF", ink="#0B1620", ink2="#4A5A66", line="#C3CDD4", keyc="#00616F",
                  mp="#0891B2", pay="#D97706", ops="#7C3AED", mkt="#DB2777", ref="#475569",
                  biz="#059669", shr="#0E7490", fillop=0.12),
    "dark":  dict(bg="#0D1117", ink="#E8EEF0", ink2="#9AA8B2", line="#33414C", keyc="#3FC3DA",
                  mp="#22D3EE", pay="#FBBF24", ops="#A78BFA", mkt="#F472B6", ref="#94A3B8",
                  biz="#34D399", shr="#2DD4BF", fillop=0.16),
}
FONT = "Inter, Segoe UI, Helvetica, Arial, sans-serif"


def svg_open(W, H, t):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">',
            f'<rect width="{W}" height="{H}" fill="{t["bg"]}"/>']


def circle(o, t, x, y, r, colour, strong=True):
    o.append(f'<circle cx="{x}" cy="{y}" r="{r:.0f}" fill="{t["bg"]}"/>')
    o.append(f'<circle cx="{x}" cy="{y}" r="{r:.0f}" fill="{colour}" fill-opacity="{t["fillop"]}" '
             f'stroke="{colour}" stroke-width="{2.5 if strong else 1.5}"/>')


def text_block(o, t, x, y, lines, fs, weight=600, colour=None, sub=None):
    y0 = y - (len(lines) - 1) * fs * 0.6 - (7 if sub else 0)
    for i, ln in enumerate(lines):
        o.append(f'<text x="{x}" y="{y0 + i*fs*1.2 + fs*0.35:.0f}" font-size="{fs}" font-weight="{weight}" '
                 f'fill="{colour or t["ink"]}" text-anchor="middle">{ln}</text>')
    if sub:
        o.append(f'<text x="{x}" y="{y0 + len(lines)*fs*1.2 + 6:.0f}" font-size="11.5" fill="{t["ink2"]}" text-anchor="middle">{sub}</text>')


def key_label(o, t, x1, y1, x2, y2, lab):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    w = 7.2 * len(lab) + 12
    o.append(f'<rect x="{mx-w/2:.0f}" y="{my-10:.0f}" width="{w:.0f}" height="20" rx="3" fill="{t["bg"]}" stroke="{t["line"]}"/>')
    o.append(f'<text x="{mx:.0f}" y="{my+4:.0f}" font-size="11.5" font-family="Consolas, monospace" fill="{t["keyc"]}" text-anchor="middle">{lab}</text>')


def legend(o, t, items, notes, x=24, y=30):
    o.append(f'<text x="{x}" y="{y}" font-size="13" font-weight="600" fill="{t["ink"]}">Owning domain</text>')
    for i, (d, name) in enumerate(items):
        yy = y + 24 + i * 22
        o.append(f'<circle cx="{x+7}" cy="{yy-4}" r="6" fill="{t[d]}" fill-opacity="{t["fillop"]*2}" stroke="{t[d]}" stroke-width="2"/>')
        o.append(f'<text x="{x+20}" y="{yy}" font-size="12.5" fill="{t["ink2"]}">{name}</text>')
    base = y + 24 + len(items) * 22 + 12
    for i, n in enumerate(notes):
        o.append(f'<text x="{x}" y="{base + i*16}" font-size="11.5" fill="{t["ink2"]}">{n}</text>')


# ── Ontology ────────────────────────────────────────────────────────────────

def key_count(key):
    pat = re.compile(rf"name: {key}\b")
    return sum(1 for f in SILVER if pat.search(f.read_text(encoding="utf-8")))


ENTITIES = {  # id: (label, domain, key or None, x, y)
    "trip":     ("Trip", "mp", "trip_id", 450, 560),
    "city":     ("City", "ref", "city_code", 230, 380),
    "rider":    ("Rider", "mp", "rider_id", 680, 380),
    "driver":   ("Driver", "mp", "driver_id", 230, 770),
    "charge":   ("Charge", "pay", "charge_id", 680, 770),
    "campaign": ("Campaign", "mkt", "campaign_id", 610, 95),
    "push":     ("Push\nnotification", "mkt", None, 760, 205),
    "request":  ("Trip\nrequest", "mp", None, 845, 330),
    "cancel":   ("Cancellation", "mp", None, 450, 335),
    "ticket":   ("Support\nticket", "ops", None, 850, 575),
    "incident": ("Safety\nincident", "ops", None, 455, 800),
    "refund":   ("Refund", "pay", None, 830, 905),
    "payout":   ("Payout", "pay", None, 385, 950),
    "receipt":  ("Expense\nreceipt", "pay", None, 165, 965),
    "check":    ("Background\ncheck", "ops", None, 65, 845),
    "doc":      ("Licence /\ninsurance", "ops", None, 75, 640),
    "vehicle":  ("Vehicle\ntype", "ref", None, 70, 470),
}
RELATIONS = [  # (a, b, joining key shown on the line, or "")
    ("rider", "trip", "rider_id"), ("driver", "trip", "driver_id"), ("city", "trip", "city_code"),
    ("trip", "charge", "trip_id"), ("charge", "refund", "charge_id"), ("trip", "cancel", ""),
    ("rider", "request", ""), ("campaign", "push", ""), ("push", "rider", "rider_id"),
    ("trip", "ticket", "trip_id"), ("rider", "ticket", ""), ("charge", "ticket", ""),
    ("trip", "incident", ""), ("driver", "payout", "driver_id"), ("driver", "receipt", ""),
    ("driver", "check", ""), ("driver", "doc", ""), ("vehicle", "driver", ""), ("city", "driver", ""),
]


def render_ontology(t):
    o = svg_open(920, 1050, t)
    sizes = {k: key_count(v[2]) if v[2] else 0 for k, v in ENTITIES.items()}
    for a, b, lab in RELATIONS:
        x1, y1, x2, y2 = ENTITIES[a][3], ENTITIES[a][4], ENTITIES[b][3], ENTITIES[b][4]
        o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["line"]}" stroke-width="1.5"/>')
        if lab:
            key_label(o, t, x1, y1, x2, y2, lab)
    for k, (label, dom, _key, x, y) in ENTITIES.items():
        n = sizes[k]
        circle(o, t, x, y, 34 + 15 * math.sqrt(n) if n else 40, t[dom], strong=bool(n))
        fs = 17 if n >= 6 else (14 if n else 12.5)
        text_block(o, t, x, y, label.split("\n"), fs, 600 if n else 500, sub=f"{n} contracts" if n else None)
    legend(o, t, [("mp", "Marketplace"), ("pay", "Payments"), ("ops", "Operations"), ("mkt", "Marketing"), ("ref", "Reference")],
           ["Size: Silver contracts carrying", "the entity's key. Labels on", "lines: the key that joins them."])
    o.append("</svg>")
    return "\n".join(o)


# ── Systems ─────────────────────────────────────────────────────────────────

DOMAINS = {  # folder: (label, colour, systems, x, y, systems text above or below)
    "marketplace": ("Marketplace", "mp", ["RideFlow app"], 170, 250, "above"),
    "payments":    ("Payments", "pay", ["Stripe", "Driver expenses"], 460, 250, "above"),
    "reference":   ("Reference", "ref", ["Internal lists"], 750, 250, "above"),
    "operations":  ("Operations", "ops", ["Onboarding, Checkr,", "Trust &amp; Safety,", "Zendesk, Twilio"], 170, 830, "below"),
    "business":    ("Business", "biz", ["Salesforce"], 460, 830, "below"),
    "marketing":   ("Marketing", "mkt", ["Google Ads, Meta Ads,", "Analytics, HubSpot"], 750, 830, "below"),
}
SHARED = {  # contract file: (label, x)
    "gold_fact_revenue_daily.yaml": ("Daily\nrevenue", 140),
    "gold_mart_marketplace_health.yaml": ("Marketplace\nhealth", 360),
    "gold_dim_driver_360.yaml": ("Driver\n360", 580),
    "gold_mart_acquisition_cost.yaml": ("Acquisition\ncost", 800),
}
SHARED_Y = 540


def domain_contracts(folder):
    return len(list((CONTRACTS / folder).glob("*/contracts/*/*.yaml")))


def shared_reads(fname):
    text = (CONTRACTS / "shared" / "shared" / "contracts" / "gold" / fname).read_text(encoding="utf-8")
    return sorted(set(re.findall(r"domain_catalog_prefix\}_([a-z]+)`", text)))


def render_systems(t):
    o = svg_open(920, 1080, t)
    for fname, (_label, sx) in SHARED.items():
        for dom in shared_reads(fname):
            if dom in DOMAINS:
                d = DOMAINS[dom]
                o.append(f'<line x1="{d[3]}" y1="{d[4]}" x2="{sx}" y2="{SHARED_Y}" stroke="{t[d[1]]}" stroke-opacity="0.55" stroke-width="2"/>')
    for folder, (label, col, systems, x, y, pos) in DOMAINS.items():
        n = domain_contracts(folder)
        r = 30 + 9 * math.sqrt(n)
        circle(o, t, x, y, r, t[col])
        text_block(o, t, x, y, [label], 17, sub=f"{n} contracts")
        start = y - r - 14 - (len(systems) - 1) * 16 if pos == "above" else y + r + 24
        for i, s in enumerate(systems):
            o.append(f'<text x="{x}" y="{start + i*16:.0f}" font-size="12.5" fill="{t["ink2"]}" text-anchor="middle">{s}</text>')
    for _fname, (label, sx) in SHARED.items():
        circle(o, t, sx, SHARED_Y, 52, t["shr"])
        text_block(o, t, sx, SHARED_Y, label.split("\n"), 13.5)
    # legend: one row along the bottom, clear of every circle and line
    items = [("mp", "Marketplace"), ("pay", "Payments"), ("ref", "Reference"), ("ops", "Operations"),
             ("biz", "Business"), ("mkt", "Marketing"), ("shr", "Shared product")]
    x, y = 24, 1040
    for d, name in items:
        o.append(f'<circle cx="{x+7}" cy="{y-4}" r="6" fill="{t[d]}" fill-opacity="{t["fillop"]*2}" stroke="{t[d]}" stroke-width="2"/>')
        o.append(f'<text x="{x+19}" y="{y}" font-size="12.5" fill="{t["ink2"]}">{name}</text>')
        x += 26 + 7.4 * len(name)
    o.append(f'<text x="24" y="{y+24}" font-size="11.5" fill="{t["ink2"]}">Circle size: contracts in the domain. Lines: a Shared product reads tables from that domain.</text>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    for name, theme in THEMES.items():
        (OUT / f"rideflow_ontology_{name}.svg").write_text(render_ontology(theme), encoding="utf-8")
        (OUT / f"rideflow_systems_{name}.svg").write_text(render_systems(theme), encoding="utf-8")
    print("keys:", {k: key_count(v[2]) for k, v in ENTITIES.items() if v[2]})
    print("domains:", {d: domain_contracts(d) for d in DOMAINS})
    print("shared reads:", {f: shared_reads(f) for f in SHARED})
