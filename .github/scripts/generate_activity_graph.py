#!/usr/bin/env python3
"""
generate_activity_graph.py
Fetches live daily contribution counts from GitHub's public contributions
calendar and generates a compact, animated obsidian SVG area-line graph
at assets/activity-graph.svg.
"""

from datetime import datetime
import os
import re
import urllib.request

USERNAME = "AP24110011314"
OUTPUT_PATH = "assets/activity-graph.svg"
DAYS_WINDOW = 31


def fetch_contributions(username: str):
    """Return sorted list of (YYYY-MM-DD, count) tuples from GitHub HTML."""
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8")

    cells = re.findall(
        r'data-date="(\d{4}-\d{2}-\d{2})"\s+id="([^"]+)"[^>]*data-level="\d+"',
        html,
    )
    tips = dict(re.findall(r'for="([^"]+)"[^>]*>([^<]+)</tool-tip>', html))

    days = []
    for date_str, cell_id in cells:
        tip = tips.get(cell_id, "")
        match = re.match(r"(\d+)\s+contribution", tip)
        count = int(match.group(1)) if match else 0
        days.append((date_str, count))

    days.sort(key=lambda item: item[0])
    return days


def monotone_cubic_path(points):
    """Build a smooth SVG cubic Bezier path without vertical overshoot."""
    n = len(points)
    if n < 2:
        return ""

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    secants = []
    for i in range(n - 1):
        dx = xs[i + 1] - xs[i]
        secants.append((ys[i + 1] - ys[i]) / dx if dx else 0.0)

    tangents = [0.0] * n
    tangents[0] = secants[0]
    tangents[-1] = secants[-1]
    for i in range(1, n - 1):
        if secants[i - 1] * secants[i] > 0:
            tangents[i] = 0.5 * (secants[i - 1] + secants[i])
        else:
            tangents[i] = 0.0

    # Fritsch-Carlson monotonicity constraint
    for i in range(n - 1):
        if abs(secants[i]) < 1e-9:
            tangents[i] = 0.0
            tangents[i + 1] = 0.0
        else:
            alpha = tangents[i] / secants[i]
            beta = tangents[i + 1] / secants[i]
            sq = alpha * alpha + beta * beta
            if sq > 9.0:
                tau = 3.0 / (sq ** 0.5)
                tangents[i] = tau * alpha * secants[i]
                tangents[i + 1] = tau * beta * secants[i]

    cmds = [f"M{xs[0]:.2f},{ys[0]:.2f}"]
    for i in range(n - 1):
        dx = (xs[i + 1] - xs[i]) / 3.0
        cp1x = xs[i] + dx
        cp1y = ys[i] + tangents[i] * dx
        cp2x = xs[i + 1] - dx
        cp2y = ys[i + 1] - tangents[i + 1] * dx
        cmds.append(
            f"C{cp1x:.2f},{cp1y:.2f} {cp2x:.2f},{cp2y:.2f} {xs[i + 1]:.2f},{ys[i + 1]:.2f}"
        )
    return " ".join(cmds)


def nice_ceil(val: int) -> int:
    if val <= 5:
        return 5
    if val <= 10:
        return 10
    if val <= 20:
        return 20
    step = 10 if val <= 60 else 20
    return ((val + step - 1) // step) * step


def build_svg(recent_days) -> str:
    width, height = 900, 180
    x_start, x_end = 48.0, 872.0
    y_top, y_bottom = 48.0, 146.0
    plot_w = x_end - x_start
    plot_h = y_bottom - y_top

    counts = [c for _, c in recent_days]
    total_31d = sum(counts)
    peak_val = max(counts) if counts else 0
    peak_idx = counts.index(peak_val) if counts else 0
    y_max = nice_ceil(max(peak_val, 1))

    n = len(recent_days)
    points = []
    for i, (_, cnt) in enumerate(recent_days):
        px = x_start + (i / max(n - 1, 1)) * plot_w
        py = y_bottom - (cnt / y_max) * plot_h
        points.append((px, py))

    line_d = monotone_cubic_path(points)
    area_d = f"{line_d} L{x_end:.2f},{y_bottom:.2f} L{x_start:.2f},{y_bottom:.2f} Z"

    # Horizontal gridlines (3 steps)
    grid_lines = []
    for step in range(4):
        val = int(round((y_max / 3.0) * step))
        gy = y_bottom - (step / 3.0) * plot_h
        grid_lines.append(
            f'<line x1="{x_start:.0f}" y1="{gy:.1f}" x2="{x_end:.0f}" y2="{gy:.1f}" '
            f'stroke="#21262D" stroke-width="1" stroke-dasharray="3 4"/>'
            f'<text class="axis" x="{x_start - 8:.0f}" y="{gy + 3.5:.1f}" text-anchor="end">{val}</text>'
        )

    # Bottom x-axis date labels (6 evenly spaced ticks)
    x_labels = []
    tick_indices = sorted(set([0, 5, 10, 15, 20, 25, n - 1]))
    for idx in tick_indices:
        dt_obj = datetime.strptime(recent_days[idx][0], "%Y-%m-%d")
        label = dt_obj.strftime("%b %d")
        lx = points[idx][0]
        anchor = "start" if idx == 0 else ("end" if idx == n - 1 else "middle")
        x_labels.append(
            f'<text class="axis" x="{lx:.1f}" y="166" text-anchor="{anchor}">{label}</text>'
        )

    # Data point dots
    dots = []
    for i, (px, py) in enumerate(points):
        cnt = counts[i]
        if i == n - 1:
            # Today's latest point with live radar ring
            dots.append(
                f'<circle class="halo-last" cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="none" stroke="#38BDF8" stroke-width="1.5"/>'
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#38BDF8" stroke="#0D1117" stroke-width="1.2"/>'
            )
        elif i == peak_idx and peak_val > 0:
            dots.append(
                f'<circle class="halo-peak" cx="{px:.1f}" cy="{py:.1f}" r="5" fill="none" stroke="#F85D7F" stroke-width="1.5"/>'
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="#F85D7F" stroke="#0D1117" stroke-width="1.2"/>'
            )
        elif cnt > 0:
            dots.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.3" fill="#E6EDF3" stroke="#8B5CF6" stroke-width="1"/>'
            )

    peak_date = datetime.strptime(recent_days[peak_idx][0], "%Y-%m-%d").strftime("%b %d")
    px_last, py_last = points[-1]
    px_peak, py_peak = points[peak_idx]

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">'
        '<defs>'
        '<linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#0D1117"/>'
        '<stop offset="100%" stop-color="#111723"/>'
        '</linearGradient>'
        '<linearGradient id="lineGrad" gradientUnits="userSpaceOnUse" x1="48" y1="0" x2="872" y2="0">'
        '<stop offset="0%" stop-color="#F85D7F"/>'
        '<stop offset="55%" stop-color="#8B5CF6"/>'
        '<stop offset="100%" stop-color="#38BDF8"/>'
        '</linearGradient>'
        '<linearGradient id="pulseGrad" gradientUnits="userSpaceOnUse" x1="48" y1="0" x2="872" y2="0">'
        '<stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.9"/>'
        '<stop offset="50%" stop-color="#F85D7F" stop-opacity="1"/>'
        '<stop offset="100%" stop-color="#38BDF8" stop-opacity="1"/>'
        '</linearGradient>'
        '<linearGradient id="areaGrad" x1="0%" y1="0%" x2="0%" y2="100%">'
        '<stop offset="0%" stop-color="#F85D7F" stop-opacity="0.28"/>'
        '<stop offset="55%" stop-color="#8B5CF6" stop-opacity="0.10"/>'
        '<stop offset="100%" stop-color="#0D1117" stop-opacity="0"/>'
        '</linearGradient>'
        '</defs>'
        '<style>'
        '@keyframes liveBlink { 0%, 100% { opacity: 0.4; } 50% { opacity: 1; } }'
        '@keyframes pathComet { 0% { stroke-dashoffset: 1100; } 100% { stroke-dashoffset: 0; } }'
        '@keyframes haloPing { 0% { transform: scale(1); opacity: 0.85; } 100% { transform: scale(2.4); opacity: 0; } }'
        '.live-dot { animation: liveBlink 2s ease-in-out infinite; }'
        '.comet-line { stroke-dasharray: 120 980; animation: pathComet 4.8s linear infinite; }'
        f'.halo-peak {{ transform-origin: {px_peak:.1f}px {py_peak:.1f}px; animation: haloPing 2.6s ease-out infinite; }}'
        f'.halo-last {{ transform-origin: {px_last:.1f}px {py_last:.1f}px; animation: haloPing 2.2s ease-out infinite 0.7s; }}'
        '.title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 13.5px; font-weight: 700; fill: #E6EDF3; }'
        '.meta { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 11px; font-weight: 600; fill: #8B949E; }'
        '.axis { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 10px; fill: #6E7681; }'
        '</style>'
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="10" ry="10" fill="url(#cardBg)" stroke="#30363D" stroke-width="1.2"/>'
        '<circle class="live-dot" cx="22" cy="24" r="4" fill="#F85D7F"/>'
        '<text class="title" x="34" y="28">Contribution Activity — Last 31 Days</text>'
        f'<text class="meta" x="872" y="28" text-anchor="end">31D TOTAL: {total_31d}  •  PEAK: {peak_val} ({peak_date})</text>'
        + "".join(grid_lines)
        + f'<path d="{area_d}" fill="url(#areaGrad)"/>'
        + f'<path d="{line_d}" fill="none" stroke="url(#lineGrad)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
        + f'<path class="comet-line" d="{line_d}" fill="none" stroke="url(#pulseGrad)" stroke-width="2.8" stroke-linecap="round"/>'
        + "".join(dots)
        + "".join(x_labels)
        + "</svg>"
    )


def main():
    days = fetch_contributions(USERNAME)
    recent = days[-DAYS_WINDOW:]
    if not recent:
        raise RuntimeError("No contribution data found from GitHub")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    svg = build_svg(recent)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {OUTPUT_PATH} ({len(recent)} days, total={sum(c for _, c in recent)})")


if __name__ == "__main__":
    main()
