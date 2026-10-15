#!/usr/bin/env python3
"""
Generate an animated neofetch-style terminal info card SVG (info-card.svg).
Displays profile details, tech stack, experience, and system info with
a staggered typing/sliding animation.

Canvas: 840 x 880 (matches portrait and stats canvas).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")

W, H = 840, 880
PAD = 26
TITLEBAR_H = 34

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
CYAN = "#00fff0"
ORANGE = "#A63C06"
PINK = "#ff006e"
GREEN = "#39d353"
BLUE = "#58a6ff"
YELLOW = "#f2cc60"

STATIC = bool(os.environ.get("STATIC"))

lines_data = [
    # (type, key, value, color)
    ("header", "aagam@neural-node", "------------------------", CYAN),
    ("kv", "OS", "Neural Linux x86_64 (Knowledge Graph Distro)", TEXT),
    ("kv", "Host", "Aagam Mehta (AI & System Design Engineer)", TEXT),
    ("kv", "Education", "DJSCE Mumbai — B.Tech AI & Data Science", TEXT),
    ("kv", "Uptime", "Building, Shipping, Learning (Active)", GREEN),
    ("kv", "Focus", "Graph Intelligence • RAG • Agentic Systems", CYAN),
    ("divider", "", "", FRAME),
    ("kv", "Core", "Python, C++, Cypher, SQL, REST APIs", TEXT),
    ("kv", "AI / LLMs", "LangChain, LangGraph, LlamaIndex, Bedrock", PINK),
    ("kv", "Graphs & DBs", "Neo4j, PostgreSQL, MongoDB, Vector DBs, Kafka", BLUE),
    ("kv", "Cloud & Infra", "AWS (Lambda, SQS), Terraform, Docker, CI/CD", YELLOW),
    ("divider", "", "", FRAME),
    ("kv", "Work [Current]", "PearlThoughts — AI Intern (Dec 2025 – Present)", GREEN),
    ("kv", "Work [Prev]", "HEProAI — DevOps Intern (Oct 2025 – Dec 2025)", TEXT),
    ("kv", "Location", "Mumbai, India (Open to Global / Remote)", TEXT),
    ("kv", "Status", "Available for Freelance, Internships & Full-Time", CYAN),
]

def render():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<style>',
        '.line { opacity: 0; animation: fadeIn 0.4s ease-out both; }',
        '@keyframes fadeIn { 0% { opacity: 0; transform: translateY(8px); } 100% { opacity: 1; transform: translateY(0); } }',
        '@media (prefers-reduced-motion: reduce) { .line { opacity: 1 !important; transform: none !important; animation: none !important; } }',
        '</style>',
        '<defs>',
        f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient>',
        '</defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')

    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">aagam@github: ~$ neofetch --profile</text>')

    start_y = TITLEBAR_H + 42
    line_h = 36
    delay_step = 0.09

    for idx, item in enumerate(lines_data):
        item_type, key, val, color = item
        y = start_y + idx * line_h
        delay = idx * delay_step
        anim_attr = f'style="animation-delay:{delay:.2f}s"' if not STATIC else ''

        if item_type == "header":
            parts.append(
                f'<g class="line" {anim_attr}>'
                f'<text x="{PAD}" y="{y}" font-size="20" font-weight="700" fill="{CYAN}">{key}</text>'
                f'<text x="{PAD}" y="{y+16}" font-size="14" fill="{MUTED}">{val}</text>'
                f'</g>'
            )
        elif item_type == "divider":
            parts.append(
                f'<g class="line" {anim_attr}>'
                f'<line x1="{PAD}" y1="{y-10}" x2="{W-PAD}" y2="{y-10}" stroke="{FRAME}" stroke-dasharray="4,4"/>'
                f'</g>'
            )
        elif item_type == "kv":
            parts.append(
                f'<g class="line" {anim_attr}>'
                f'<text x="{PAD}" y="{y}" font-size="17" font-weight="600" fill="{CYAN}">{key}:</text>'
                f'<text x="{PAD + 175}" y="{y}" font-size="17" fill="{color}">{val}</text>'
                f'</g>'
            )

    # Neofetch color palette blocks at bottom
    palette_y = H - 56
    colors_row1 = ["#161b22", "#ff5f56", "#27c93f", "#ffbd2e", "#58a6ff", "#ff006e", "#00fff0", "#e6edf3"]
    block_w = 42
    block_h = 24
    start_x = PAD
    delay = len(lines_data) * delay_step
    anim_attr = f'style="animation-delay:{delay:.2f}s"' if not STATIC else ''

    parts.append(f'<g class="line" {anim_attr}>')
    for ci, c in enumerate(colors_row1):
        parts.append(
            f'<rect x="{start_x + ci * (block_w + 8)}" y="{palette_y}" width="{block_w}" height="{block_h}" '
            f'rx="4" fill="{c}"/>'
        )
    parts.append('</g>')

    parts.append('</svg>')
    svg = "".join(parts)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT}: {W} x {H}, {len(svg)//1024} KB")

if __name__ == "__main__":
    render()
