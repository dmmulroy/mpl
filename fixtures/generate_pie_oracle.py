"""Axes.pie geometry, texts and errors from matplotlib itself -> fixtures/pie_oracle.json (test/pie.test.ts).

Path.arc and Wedge path vertices (bit-exact, as repr strings), pie()'s wedges (centre, r, theta1, theta2, colours,
edge, width), its texts (position, string, alignment, rotation, size, colour) and the axes state it leaves (aspect,
frame, limits, ticks), Python printf-style autopct strings, and the errors pie() raises.
Run with matplotlib 3.11.2 (fixtures/requirements.txt): python fixtures/generate_pie_oracle.py
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import Shadow, Wedge
from matplotlib.colors import to_hex, to_rgba

OUT = os.path.join(os.path.dirname(__file__), "pie_oracle.json")
r = lambda v: repr(float(v))

def path_rec(p):
    return {"x": [r(v) for v in p.vertices[:, 0]], "y": [r(v) for v in p.vertices[:, 1]], "codes": [int(c) for c in p.codes]}

ARCS = [[0, 90], [0, 360], [30, 200], [-45, 45], [90, 450], [10, 10.5], [200, 100], [54, 162], [0, 359.9999]]
WEDGES = [
    {"center": [0, 0], "r": 1, "theta1": 0, "theta2": 54},
    {"center": [0.1, -0.2], "r": 0.8, "theta1": 54, "theta2": 162, "width": 0.3},
    {"center": [0, 0], "r": 1, "theta1": 0, "theta2": 360},
    {"center": [0, 0], "r": 1.5, "theta1": 90, "theta2": 450, "width": 0.5},
]

# printf-style autopct: (format, value) -> fmt % value
FMTS = ["%1.1f%%", "%.0f%%", "%d%%", "%1.0f", "%.2f", "%5.1f|", "%-7.2f|", "%+.1f", "% .1f", "%05.1f", "%e", "%.3E", "%g",
        "%.3g", "%#.3g", "%G", "%s", "%r", "%.3s", "%i", "%.3d", "%u", "%F", "%.0e", "%#.0f", "pct=%.1f!", "%%%.1f"]
VALUES = [0.0, 12.5, 37.5, 2.5, 0.125, 33.33333333333333, 66.66666666666667, 100.0, 1e-05, 123456789.0, 0.5, 1.5, 99.95, 7.0, 14.285714285714286]
formats = [{"fmt": f, "value": r(v), "out": f % v} for f in FMTS for v in VALUES]

def text_rec(t):
    x, y = t.get_position()
    return {"x": r(x), "y": r(y), "s": t.get_text(), "ha": t.get_horizontalalignment(), "va": t.get_verticalalignment(),
            "rotation": r(t.get_rotation()), "size": r(t.get_fontsize()), "color": to_hex(t.get_color(), keep_alpha=True),
            "weight": t.get_fontweight(), "clip": t.get_clip_on()}

def pie_case(name, x, **kw):
    fig, ax = plt.subplots()
    pc = ax.pie(x, **kw)
    wedges = []
    for p in ax.patches:
        if isinstance(p, Shadow):
            w = p.patch
            wedges.append({"shadow": True, "of": ax.patches.index(w), "face": [r(v) for v in p.get_facecolor()],
                           "edge": [r(v) for v in p.get_edgecolor()], "lw": r(p.get_linewidth()), "zorder": r(p.get_zorder()),
                           "ox": r(p._ox), "oy": r(p._oy)})
        else:
            wedges.append({"shadow": False, "cx": r(p.center[0]), "cy": r(p.center[1]), "r": r(p.r), "theta1": r(p.theta1), "theta2": r(p.theta2),
                           "width": None if p.width is None else r(p.width), "face": [r(v) for v in p.get_facecolor()],
                           "edge": [r(v) for v in p.get_edgecolor()], "lw": r(p.get_linewidth()), "label": p.get_label(),
                           "zorder": r(p.get_zorder()), "clip": p.get_clip_on()})
    texts = pc.texts
    labelled = kw.get("labeldistance", 1.1) is not None
    rec = {"name": name, "x": x, "kw": kw, "wedges": wedges,
           "texts": [text_rec(t) for t in (texts[0] if labelled and texts else [])],
           "autotexts": [text_rec(t) for t in (texts[-1] if kw.get("autopct") is not None else [])],
           "fracs": [r(v) for v in pc.fracs],
           "aspect": ax.get_aspect(), "frame_on": ax.get_frame_on(), "xlim": [r(v) for v in ax.get_xlim()], "ylim": [r(v) for v in ax.get_ylim()],
           "xticks": [r(v) for v in ax.get_xticks()], "yticks": [r(v) for v in ax.get_yticks()],
           "legend": [h.get_label() for h in ax.get_legend_handles_labels()[0]]}
    plt.close(fig)
    return rec

PIES = [
    pie_case("basic", [15, 30, 45, 10], labels=["Frogs", "Hogs", "Dogs", "Logs"]),
    pie_case("autopct_explode_shadow", [15, 30, 45, 10], labels=["a", "b", "c", "d"], autopct="%1.1f%%", explode=[0, 0.1, 0, 0], shadow=True, startangle=90),
    pie_case("clockwise_rotate", [10, 20, 30, 25, 15], labels=["n", "e", "s", "w", "l"], counterclock=False, rotatelabels=True, startangle=45, labeldistance=1.05),
    pie_case("rotate_inside", [1, 2, 3], labels=["i", "j", "k"], rotatelabels=True, labeldistance=0.5),
    pie_case("partial", [0.2, 0.3, 0.15], normalize=False, autopct="%.0f%%", colors=["C3", "C4", "C5"]),
    pie_case("donut_shadow_dict", [30, 25, 20, 15, 10], wedgeprops={"width": 0.4, "edgecolor": "w", "linewidth": 2},
             shadow={"ox": -0.04, "oy": -0.03, "shade": 0.5}, startangle=30, pctdistance=0.8, autopct="%.0f%%"),
    pie_case("props", [3, 1, 2, 2.5], radius=0.8, center=(0.2, -0.1), labels=["w", "x", "y", "z"], labeldistance=None, autopct="%.2f",
             colors=["0.8", "tab:orange"], textprops={"fontsize": "small", "color": "C3", "fontweight": "bold"}),
    pie_case("wedgeprops_alpha_face", [1, 1, 2], wedgeprops={"alpha": 0.5, "facecolor": "red", "linewidth": 0}, textprops={"size": 14, "c": "b"}, autopct="%d"),
    pie_case("single", [7], labels=["all"], autopct="%1.1f%%"),
    pie_case("zero_slice", [0, 3, 1], labels=["zero", "three", "one"]),
    pie_case("floats_sum", [0.1, 0.2, 0.3, 0.4, 0.05, 0.15, 0.25, 0.35, 0.45], startangle=-30),
    pie_case("underscore_label", [1, 2], labels=["_hidden", "shown"]),
]

def error(name, x, **kw):
    fig, ax = plt.subplots()
    try:
        ax.pie(x, **kw)
        msg = None
    except Exception as e:
        msg = {"type": type(e).__name__, "message": str(e)}
    plt.close(fig)
    enc = [v if np.isfinite(v) else {"$float": repr(v)} for v in x]
    return {"name": name, "x": enc, "kw": kw, "error": msg}

ERRORS = [
    error("negative", [1, -1]), error("all_zero", [0, 0]), error("unnormalized_over", [0.6, 0.6], normalize=False),
    error("labels_len", [1, 2], labels=["a"]), error("explode_len", [1, 2], explode=[0]), error("radius", [1, 2], radius=0),
    error("shade", [1, 2], shadow={"shade": 2}), error("nonfinite", [1, float("inf")]),
]

rec = {"matplotlib": matplotlib.__version__, "numpy": np.__version__,
       "arcs": [{"theta1": a, "theta2": b, **path_rec(Path.arc(a, b))} for a, b in ARCS],
       "wedges": [{**w, **path_rec(Wedge(tuple(w["center"]), w["r"], w["theta1"], w["theta2"], width=w.get("width")).get_path())} for w in WEDGES],
       "formats": formats, "pies": PIES, "errors": ERRORS}
with open(OUT, "w") as f:
    json.dump(rec, f, indent=1)
print(f"wrote {OUT}")
