"""
gen_diagrams.py — generate ECO-LINK's ERD and DFD as standalone SVG files.

These match Chapter 3 of the report (Figures 5 and 4). SVG imports cleanly into
Microsoft Word (Insert > Pictures) and scales without blurring.

Run:  ./venv/Scripts/python.exe docs/diagrams/gen_diagrams.py
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent
GREEN = "#16a34a"
DARK = "#14532d"
INK = "#1f2937"

# --------------------------------------------------------------------------- #
# Small SVG helpers
# --------------------------------------------------------------------------- #

def entity(x, y, w, title, fields):
    """A database-table box: green header + white body with field rows."""
    row_h = 20
    h = 30 + row_h * len(fields)
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
        f'fill="#ffffff" stroke="{DARK}" stroke-width="1.5"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="6" fill="{GREEN}"/>',
        f'<rect x="{x}" y="{y+14}" width="{w}" height="14" fill="{GREEN}"/>',
        f'<text x="{x+w/2}" y="{y+19}" text-anchor="middle" fill="#fff" '
        f'font-weight="700" font-size="14">{title}</text>',
    ]
    for i, f in enumerate(fields):
        ty = y + 30 + row_h * i + 14
        parts.append(
            f'<text x="{x+12}" y="{ty}" fill="{INK}" font-size="12.5">{f}</text>'
        )
    return "\n".join(parts), h


def line(x1, y1, x2, y2):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{DARK}" stroke-width="1.6"/>')


def polyline(points):
    pts = " ".join(f"{x},{y}" for x, y in points)
    return (f'<polyline points="{pts}" fill="none" '
            f'stroke="{DARK}" stroke-width="1.6"/>')


def label(x, y, text, size=13):
    return (f'<text x="{x}" y="{y}" fill="{DARK}" font-size="{size}" '
            f'font-weight="700">{text}</text>')


def svg(width, height, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'font-family="Segoe UI, Arial, sans-serif">\n'
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>\n'
        f'<text x="{width/2}" y="30" text-anchor="middle" fill="{DARK}" '
        f'font-size="18" font-weight="800">{title}</text>\n'
        f'{body}\n</svg>\n'
    )


# --------------------------------------------------------------------------- #
# ERD
# --------------------------------------------------------------------------- #

def build_erd():
    b = []
    user, _ = entity(40, 70, 220, "User", [
        "id  (PK)", "email  (unique)", "role", "status",
        "eco_points_balance", "first_name", "last_name",
    ])
    dropoff, _ = entity(400, 70, 220, "DropOff", [
        "id  (PK)", "user  (FK)", "hub  (FK)", "plastic_type",
        "weight_kg", "status", "created_at", "verified_at",
    ])
    hub, _ = entity(760, 70, 200, "Hub", [
        "id  (PK)", "name", "location", "capacity_kg",
        "status", "manufacturer  (FK)",
    ])
    mfr, _ = entity(760, 300, 200, "Manufacturer", [
        "id  (PK)", "name", "email", "phone_number",
        "location", "is_certified",
    ])
    redemption, _ = entity(400, 360, 220, "Redemption", [
        "id  (PK)", "user  (FK)", "reward  (FK)",
        "points_spent", "created_at",
    ])
    reward, _ = entity(760, 500, 200, "Reward", [
        "id  (PK)", "name", "points_required", "is_active",
    ])
    b += [user, dropoff, hub, mfr, redemption, reward]

    # Relationships (1 --- * ) with cardinality labels.
    # User 1 -- * DropOff
    b.append(line(260, 150, 400, 150))
    b += [label(268, 144, "1"), label(384, 144, "*")]
    # Hub 1 -- * DropOff
    b.append(line(760, 150, 620, 150))
    b += [label(742, 144, "1"), label(628, 144, "*")]
    # Manufacturer 1 -- * Hub
    b.append(line(860, 300, 860, 210))
    b += [label(866, 300, "1"), label(866, 222, "*")]
    # User 1 -- * Redemption  (down the left, across)
    b.append(polyline([(150, 210), (150, 420), (400, 420)]))
    b += [label(156, 230, "1"), label(384, 414, "*")]
    # Reward 1 -- * Redemption
    b.append(polyline([(760, 540), (690, 540), (690, 420), (620, 420)]))
    b += [label(742, 534, "1"), label(628, 414, "*")]

    (OUT / "erd.svg").write_text(
        svg(1000, 640, "\n".join(b), "ECO-LINK Entity Relationship Diagram"),
        encoding="utf-8",
    )


# --------------------------------------------------------------------------- #
# DFD — Level 0 (context diagram)
# --------------------------------------------------------------------------- #

def ext_entity(x, y, w, h, text):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#dcfce7" '
        f'stroke="{DARK}" stroke-width="1.6"/>'
        f'<text x="{x+w/2}" y="{y+h/2+5}" text-anchor="middle" fill="{INK}" '
        f'font-size="13" font-weight="600">{text}</text>'
    )


def arrow(x1, y1, x2, y2, text, tx, ty):
    """A labelled data-flow arrow."""
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    a1 = ang + math.radians(150)
    a2 = ang - math.radians(150)
    h1 = (x2 + 11 * math.cos(a1), y2 + 11 * math.sin(a1))
    h2 = (x2 + 11 * math.cos(a2), y2 + 11 * math.sin(a2))
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.5"/>'
        f'<polygon points="{x2},{y2} {h1[0]:.1f},{h1[1]:.1f} {h2[0]:.1f},{h2[1]:.1f}" fill="{INK}"/>'
        f'<text x="{tx}" y="{ty}" text-anchor="middle" fill="{INK}" font-size="11">{text}</text>'
    )


def build_dfd_context():
    b = []
    # Central process
    b.append(
        f'<circle cx="500" cy="270" r="90" fill="{GREEN}" stroke="{DARK}" stroke-width="2"/>'
        f'<text x="500" y="265" text-anchor="middle" fill="#fff" font-size="15" font-weight="700">ECO-LINK</text>'
        f'<text x="500" y="285" text-anchor="middle" fill="#fff" font-size="12">System</text>'
    )
    # External entities
    b.append(ext_entity(60, 220, 150, 100, "User"))         # left
    b.append(ext_entity(790, 220, 150, 100, "Manufacturer"))  # right
    b.append(ext_entity(415, 40, 170, 70, "Administrator"))   # top

    # User <-> system
    b.append(arrow(210, 250, 410, 250, "registration, drop-offs, redemptions", 300, 235))
    b.append(arrow(410, 300, 210, 300, "dashboard, points, leaderboard", 300, 320))
    # Admin <-> system
    b.append(arrow(500, 110, 500, 180, "verify, config", 560, 150))
    b.append(arrow(540, 180, 540, 110, "stats, pending", 610, 150))
    # Manufacturer <-> system
    b.append(arrow(790, 255, 590, 255, "profile, schedule", 690, 240))
    b.append(arrow(590, 300, 790, 300, "pickup alerts", 690, 320))

    (OUT / "dfd_context.svg").write_text(
        svg(1000, 380, "\n".join(b), "ECO-LINK Data Flow Diagram (Level 0 — Context)"),
        encoding="utf-8",
    )


if __name__ == "__main__":
    build_erd()
    build_dfd_context()
    print(f"OK -> {OUT/'erd.svg'}")
    print(f"OK -> {OUT/'dfd_context.svg'}")
