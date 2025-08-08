# src/rel_sense/sensitivity.py
import numpy as np
import pandas as pd

def one_dim_boundary(df: pd.DataFrame, dim_name: str, low=0.0, high=0.5, steps=101):
    """Sweep weight of `dim_name`, rescale others proportionally; return DataFrame."""
    df = df.copy()
    idx = df.index[df["Dimension"] == dim_name]
    if len(idx) != 1:
        raise ValueError(f"dimension '{dim_name}' not found or not unique.")
    i = idx[0]
    base = df["Weight"].to_numpy()
    ex = df["ExScore"].to_numpy()
    cur = df["CurScore"].to_numpy()

    others = [k for k in range(len(base)) if k != i]
    base_other_sum = base[others].sum()

    rows = []
    grid = np.linspace(low, high, steps)
    for w in grid:
        remaining = 1 - w
        scale = remaining / base_other_sum
        weights = base.copy()
        weights[i] = w
        weights[others] = base[others] * scale
        ex_total = float((weights * ex).sum())
        cur_total = float((weights * cur).sum())
        rows.append({
            "weight": w,
            "ex_total": ex_total,
            "cur_total": cur_total,
            "diff": cur_total - ex_total
        })
    return pd.DataFrame(rows)

def tri_dim_grid(df: pd.DataFrame, dims, low=0.05, high=0.40, steps=16):
    """3D sweep over three dims; others rescaled. Return DataFrame with diff."""
    df = df.copy()
    idxs = [int(df.index[df["Dimension"] == d][0]) for d in dims]
    base = df["Weight"].to_numpy()
    ex = df["ExScore"].to_numpy()
    cur = df["CurScore"].to_numpy()

    others = [k for k in range(len(base)) if k not in idxs]
    base_other_sum = base[others].sum()

    rows = []
    grid = np.linspace(low, high, steps)
    for w0 in grid:
        for w1 in grid:
            for w2 in grid:
                sel = w0 + w1 + w2
                if sel >= 0.95:
                    continue
                weights = base.copy()
                weights[idxs[0]] = w0
                weights[idxs[1]] = w1
                weights[idxs[2]] = w2
                remaining = 1 - sel
                scale = remaining / base_other_sum
                weights[others] = base[others] * scale

                ex_total = float((weights * ex).sum())
                cur_total = float((weights * cur).sum())
                rows.append({
                    dims[0]: w0, dims[1]: w1, dims[2]: w2,
                    "ex_total": ex_total, "cur_total": cur_total,
                    "diff": cur_total - ex_total
                })
    return pd.DataFrame(rows)
