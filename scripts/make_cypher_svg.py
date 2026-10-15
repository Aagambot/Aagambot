#!/usr/bin/env python3
"""
Generate a sleek terminal window SVG for the Neo4j Cypher query (cypher.svg).
Matches the 860px width of contrib-heatmap.svg and the whoami table.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "cypher.svg")

W = 860
H = 240
PAD = 20
TITLEBAR_H = 30

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
CYAN = "#00fff0"
PINK = "#ff006e"
GREEN = "#39d353"
ORANGE = "#f0883e"
YELLOW = "#f2cc60"

def render():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<style>',
        '.f { opacity: 0; animation: in 0.5s ease-out both; }',
        '@keyframes in { 0% { opacity: 0; transform: translateY(6px); } 100% { opacity: 1; transform: translateY(0); } }',
        '@media (prefers-reduced-motion: reduce) { .f { opacity: 1 !important; transform: none !important; animation: none !important; } }',
        '</style>',
        '<defs>',
        f'<linearGradient id="cbg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient>',
        '</defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#cbg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')

    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">aagam@github: ~$ cypher-shell -u neo4j --format verbose</text>')

    # Cypher query lines
    query_y1 = TITLEBAR_H + 32
    query_y2 = query_y1 + 22
    table_y = query_y2 + 26
    
    parts.append(f'<g class="f" style="animation-delay:0.1s">')
    parts.append(f'<text x="{PAD}" y="{query_y1}" font-size="14">'
                 f'<tspan fill="{PINK}">neo4j&gt; </tspan>'
                 f'<tspan fill="{CYAN}">MATCH </tspan>'
                 f'<tspan fill="{TEXT}">(dev:</tspan><tspan fill="{YELLOW}">Engineer </tspan><tspan fill="{TEXT}">{{name: </tspan><tspan fill="{GREEN}">&quot;Aagam Mehta&quot;</tspan><tspan fill="{TEXT}">}})-[:</tspan><tspan fill="{ORANGE}">SPECIALIZES_IN</tspan><tspan fill="{TEXT}">]-&gt;(core)</tspan></text>')
    parts.append(f'<text x="{PAD}" y="{query_y2}" font-size="14">'
                 f'<tspan fill="{PINK}">      </tspan>'
                 f'<tspan fill="{CYAN}">RETURN </tspan>'
                 f'<tspan fill="{TEXT}">dev.role, dev.status, core.focus</tspan></text>')
    parts.append('</g>')

    # Cypher result table
    t_lines = [
        ("+--------------------------------------------------------------------------------+", MUTED),
        ("| dev.role       | dev.status | core.focus                                       |", CYAN),
        ("+--------------------------------------------------------------------------------+", MUTED),
        ('| "AI Engineer"  | "[ACTIVE]" | "Knowledge Graphs • Multi-Agent & RAG Systems"   |', TEXT),
        ("+--------------------------------------------------------------------------------+", MUTED),
    ]

    for idx, (t_text, t_col) in enumerate(t_lines):
        delay = 0.25 + idx * 0.07
        parts.append(
            f'<text class="f" style="animation-delay:{delay:.2f}s" x="{PAD}" y="{table_y + idx * 19}" '
            f'fill="{t_col}" font-size="13">{t_text}</text>'
        )

    # Footer status
    foot_y = table_y + len(t_lines) * 19 + 18
    parts.append(f'<g class="f" style="animation-delay:0.65s">')
    parts.append(f'<text x="{PAD}" y="{foot_y}" font-size="12" fill="{MUTED}">'
                 f'1 row available (after <tspan fill="{GREEN}">11 ms</tspan>). neo4j&gt; </text>')
    
    cursor_x = PAD + 258
    parts.append(f'<rect x="{cursor_x}" y="{foot_y - 10}" width="7" height="13" fill="{CYAN}">'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>')
    parts.append('</g>')

    parts.append('</svg>')
    svg = "".join(parts)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT}: {W} x {H}, {len(svg)//1024} KB")

if __name__ == "__main__":
    render()
