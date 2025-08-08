# src/rel_sense/plots.py
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


def plot_1d_boundary(csv_path: str, out_path: str):
    """
    Plot diff vs weight from boundary_* CSV (columns: weight, ex_total, cur_total, diff).
    Marks the point with |diff| closest to zero.
    """
    df = pd.read_csv(csv_path)
    if not {"weight", "diff"}.issubset(df.columns):
        raise ValueError("1D CSV must contain columns: weight, diff")

    # Find closest-to-zero diff
    idx_star = (df["diff"].abs()).idxmin()

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(df["weight"], df["diff"], marker="o", linewidth=1.5, label="Current - Ex")
    ax.axhline(0.0, linestyle="--", linewidth=1, label="Zero line")
    ax.scatter([df.at[idx_star, "weight"]], [df.at[idx_star, "diff"]],
               s=60, marker="D", label=f"Closest to 0 (w={df.at[idx_star, 'weight']:.3f})")
    ax.set_xlabel("Weight")
    ax.set_ylabel("Score difference (Person B - Person A)")
    ax.set_title("1D Sensitivity: diff vs weight")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=180, bbox_inches="tight")
    print(f"[ok] 1D plot saved -> {Path(out_path).resolve()}")


def plot_3d_boundary(csv_path: str, out_path: str, eps: float = 0.02):
    """
    3D plot for tri_sensitivity.csv with a colorbar.
    - Colors show diff = Current - Ex (continuous)
    - Triangles mark boundary points where |diff| <= eps
    """
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    from pathlib import Path

    df3 = pd.read_csv(csv_path)
    if "diff" not in df3.columns or "ex_total" not in df3.columns or "cur_total" not in df3.columns:
        raise ValueError("tri_sensitivity.csv must have columns: ex_total, cur_total, diff")

    # Heuristic: first 3 non-total columns are the three weight dims produced by tri_dim_grid
    weight_cols = [c for c in df3.columns if c not in {"ex_total", "cur_total", "diff"}][:3]
    if len(weight_cols) != 3:
        raise ValueError(f"Could not infer 3 weight columns. Found: {weight_cols}")

    # Data
    x, y, z = df3[weight_cols[0]], df3[weight_cols[1]], df3[weight_cols[2]]
    diff = df3["diff"]

    # Boundary mask
    boundary_mask = diff.abs() <= eps

    # ---- Plot ----
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    # Full scatter colored by diff
    p = ax.scatter(x, y, z, c=diff, s=10)

    # Boundary points highlighted
    ax.scatter(x[boundary_mask], y[boundary_mask], z[boundary_mask],
               s=25, marker="^", label=f"|diff| ≤ {eps:g}")

    # Labels & title
    ax.set_xlabel(f"Weight: {weight_cols[0]}")
    ax.set_ylabel(f"Weight: {weight_cols[1]}")
    ax.set_zlabel(f"Weight: {weight_cols[2]}")
    ax.set_title("3D Sensitivity (Color = Current − Ex)")

    # Colorbar with explanation
    cb = fig.colorbar(p, ax=ax, shrink=0.65)
    cb.set_label("Score Difference (Current − Ex)\n(> 0 = Current ahead)")

    ax.legend(loc="upper left")
    plt.tight_layout()

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=180, bbox_inches="tight")
    print(f"[ok] 3D boundary plot saved -> {Path(out_path).resolve()}")


def main():
    p = argparse.ArgumentParser(description="Plot sensitivity outputs.")
    p.add_argument("--one", help="Path to boundary_*.csv for 1D plot.")
    p.add_argument("--tri", help="Path to tri_sensitivity.csv for 3D plot.")
    p.add_argument("--eps", type=float, default=0.02, help="|diff| threshold for 3D boundary.")
    p.add_argument("--outdir", default="outputs", help="Directory to save plots.")
    args = p.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(exist_ok=True)

    if not args.one and not args.tri:
        print("Nothing to do. Pass --one and/or --tri.")
        return

    if args.one:
        one_out = outdir / "plot_boundary_1d.png"
        plot_1d_boundary(args.one, str(one_out))

    if args.tri:
        tri_out = outdir / "plot_tri_boundary.png"
        plot_3d_boundary(args.tri, str(tri_out), eps=args.eps)


if __name__ == "__main__":
    main()
