import numpy as np
import matplotlib.pyplot as plt

def radar_plot(df, title="Radar", use_weight=False):
    labels = df["Dimension"].tolist()
    ex = df["ExScore"].to_numpy()
    cur = df["CurScore"].to_numpy()
    if use_weight:
        w = df["Weight"].to_numpy()
        ex = ex * w
        cur = cur * w
        ymax = max(1.0, max(ex.max(), cur.max()) * 1.1)  # weighted usually <=1
    else:
        ymax = 10

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    ex_vals = ex.tolist() + [ex[0]]
    cur_vals = cur.tolist() + [cur[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, ex_vals, linewidth=2, label="Ex")
    ax.fill(angles, ex_vals, alpha=0.15)
    ax.plot(angles, cur_vals, linewidth=2, linestyle="--", label="Current")
    ax.fill(angles, cur_vals, alpha=0.15)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    ax.set_ylim(0, ymax)
    ax.set_title(title, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.15))
    plt.tight_layout()
    return fig
