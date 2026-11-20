import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; FIG = ROOT / "paper" / "figures"; FIG.mkdir(exist_ok=True)
FONT = "Times New Roman, Times, serif"; INK = "#222"; MUTED = "#555"


def box(x, y, w, h, lines, fs=11, fill="#fff", rx=6):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{INK}" stroke-width="1.1"/>']
    for i, line in enumerate(lines):
        yy = y + h/2 + (i - (len(lines)-1)/2)*(fs+5) + fs*.35
        s.append(f'<text x="{x+w/2}" y="{yy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="{fs}" fill="{INK}">{line}</text>')
    return "".join(s)


def arrow(x1, y1, x2, y2):
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#a)"/>'


def framework():
    W, H = 920, 540
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#fff"/>']
    p.append(f'<text x="230" y="28" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="bold">Human fatigue</text>')
    p.append(f'<text x="690" y="28" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="bold">LLM agent under load</text>')
    human = [(50, 50, ["effort / energy", "attention narrows", "input sampled, not encoded", "protective disengagement", "recovery: look away, rest"])]
    ai = [(510, 50, ["context + compute + task load", "token/attention budget", "some inputs not used", "defer / checkpoint / escalate", "recovery: resume state"])]
    for x, y, lines in human:
        for i, line in enumerate(lines):
            p.append(box(x, y+i*82, 360, 58, [line], fs=10.8))
            if i < len(lines)-1: p.append(arrow(x+180, y+i*82+58, x+180, y+(i+1)*82))
    for x, y, lines in ai:
        for i, line in enumerate(lines):
            p.append(box(x, y+i*82, 360, 58, [line], fs=10.8))
            if i < len(lines)-1: p.append(arrow(x+180, y+i*82+58, x+180, y+(i+1)*82))
    p.append(f'<text x="460" y="492" text-anchor="middle" font-family="{FONT}" font-size="11" font-style="italic" fill="{MUTED}">functional analogue, not phenomenal claim</text>')
    p.append(f'<text x="460" y="514" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{INK}">HAP: monitor → regulate → protect → recover</text>')
    p.append("</svg>")
    (FIG / "fig_framework.svg").write_text("".join(p), encoding="utf-8")


def main_fig():
    s = json.loads((ROOT / "results/batch_summary.json").read_text())
    conds = ["baseline", "overload", "hap", "governor"]
    labels = ["Baseline", "Overload", "Overload + HAP", "Overload + governor"]
    vals = [s["conditions"][c]["valid_json"]*100 for c in conds]
    vals2 = [s["conditions"][c]["critical_recall"]*100 for c in conds]
    W, H = 760, 320; left, bottom, top = 80, 70, 50; pw, ph = W-left-30, H-bottom-top
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="#fff"/>']
    p.append(f'<line x1="{left}" y1="{H-bottom}" x2="{W-30}" y2="{H-bottom}" stroke="{INK}"/>')
    p.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{H-bottom}" stroke="{INK}"/>')
    for v in range(0, 101, 20):
        y = H-bottom-v/100*ph
        p.append(f'<line x1="{left}" y1="{y}" x2="{W-30}" y2="{y}" stroke="#eee"/>')
        p.append(f'<text x="{left-8}" y="{y+4}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{MUTED}">{v}</text>')
    p.append(f'<text x="20" y="{top+ph/2}" transform="rotate(-90 20,{top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="10">Percent</text>')
    gw = pw/4; bw = gw*.28
    for i, (a, b) in enumerate(zip(vals, vals2)):
        cx = left+gw*(i+.5)
        for j, (v, col, lab) in enumerate([(a, "#3d5a80", "Valid JSON"), (b, "#c26a3a", "Critical recall")]):
            x = cx-bw+j*(bw+4); y = H-bottom-v/100*ph
            p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{H-bottom-y:.1f}" fill="{col}" opacity=".92"/>')
            p.append(f'<text x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" font-family="{FONT}" font-size="9">{v:.0f}</text>')
        p.append(f'<text x="{cx:.1f}" y="{H-bottom+20}" text-anchor="middle" font-family="{FONT}" font-size="9.5">{labels[i]}</text>')
    for j, (col, lab) in enumerate([("#3d5a80", "Valid JSON"), ("#c26a3a", "Critical recall")]):
        lx = left+10+j*100
        p.append(f'<rect x="{lx}" y="{top-24}" width="11" height="8" fill="{col}"/><text x="{lx+16}" y="{top-17}" font-family="{FONT}" font-size="10">{lab}</text>')
    p.append("</svg>")
    (FIG / "fig_main.svg").write_text("".join(p), encoding="utf-8")


def bars(data, labels, title, fname, colors=None):
    vals = [x*100 for x in data]
    W, H = 700, 300; left, bottom, top = 78, 64, 40; pw, ph = W-left-30, H-bottom-top
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="#fff"/>']
    p.append(f'<line x1="{left}" y1="{H-bottom}" x2="{W-30}" y2="{H-bottom}" stroke="{INK}"/><line x1="{left}" y1="{top}" x2="{left}" y2="{H-bottom}" stroke="{INK}"/>')
    for v in range(0, 101, 20):
        y = H-bottom-v/100*ph
        p.append(f'<line x1="{left}" y1="{y}" x2="{W-30}" y2="{y}" stroke="#eee"/><text x="{left-8}" y="{y+4}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{MUTED}">{v}</text>')
    p.append(f'<text x="20" y="{top+ph/2}" transform="rotate(-90 20,{top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="10">Percent</text>')
    gw = pw/len(vals); bw = gw*.5
    for i, v in enumerate(vals):
        cx = left+gw*(i+.5); x = cx-bw/2; y = H-bottom-v/100*ph
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{H-bottom-y:.1f}" fill="{ (colors[i] if colors else "#3d5a80") }" opacity=".92"/>')
        p.append(f'<text x="{cx:.1f}" y="{y-5:.1f}" text-anchor="middle" font-family="{FONT}" font-size="9">{v:.0f}</text>')
        p.append(f'<text x="{cx:.1f}" y="{H-bottom+18}" text-anchor="middle" font-family="{FONT}" font-size="9">{labels[i]}</text>')
    p.append(f'<text x="{W/2}" y="{H-8}" text-anchor="middle" font-family="{FONT}" font-size="10" fill="{MUTED}">{title}</text>')
    p.append("</svg>")
    (FIG / fname).write_text("".join(p), encoding="utf-8")


def analysis_figs():
    s = json.loads((ROOT / "results/summary.json").read_text())
    pos = [s["position"][k]["success"] for k in ("begin", "middle", "end")]
    bars(pos, ["Beginning", "Middle", "End"], "Critical-input position (overload)", "fig_position.svg", ["#3d5a80", "#c26a3a", "#5b8c5a"])
    keys = ["0s/700tok", "6s/700tok", "0s/250tok", "6s/250tok"]
    dose = [s["dose"][k]["success"] for k in keys]
    bars(dose, ["0s/700", "6s/700", "0s/250", "6s/250"], "Latency and token-budget dose", "fig_dose.svg", ["#3d5a80", "#5b8c5a", "#c26a3a", "#8a5a99"])


if __name__ == "__main__":
    framework()
    if (ROOT / "results/summary.json").exists(): main_fig(); analysis_figs()
    print("figs ok")
