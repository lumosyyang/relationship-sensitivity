# src/rel_sense/run_sensitivity.py
import argparse
import re
from pathlib import Path
import pandas as pd
from src.rel_sense.sensitivity import one_dim_boundary, tri_dim_grid

def _normalize_text(s: str) -> str:
    return re.sub(r"[^\w]+", "", s.strip().lower())

def _load_and_normalize(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    rename_map = {}
    if "ExScore" not in df.columns and "Ex_score_raw" in df.columns:
        rename_map["Ex_score_raw"] = "ExScore"
    if "CurScore" not in df.columns and "Cur_score_raw" in df.columns:
        rename_map["Cur_score_raw"] = "CurScore"
    if rename_map:
        df = df.rename(columns=rename_map)

    must = {"Dimension", "Weight", "ExScore", "CurScore"}
    missing = must - set(df.columns)
    if missing:
        raise ValueError(f"CSV must contain columns {must}, missing: {missing}")

    df["Dimension"] = df["Dimension"].astype(str).str.strip()

    s = df["Weight"].sum()
    if abs(s - 1.0) > 1e-6:
        print(f"[warn] Weight sum = {s:.4f} ≠ 1. Normalizing.")
        df["Weight"] = df["Weight"] / s
    return df

def _list_dimensions(df: pd.DataFrame):
    print("Available Dimension values:")
    for i, v in enumerate(df["Dimension"].tolist(), 1):
        print(f"  {i:2d}. {v}")

def _resolve_dim_name(user_name: str, df: pd.DataFrame) -> str:
    dims = df["Dimension"].tolist()
    if user_name in dims:
        return user_name
    target = _normalize_text(user_name)
    matches = [d for d in dims if _normalize_text(d) == target]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(f"Ambiguous name '{user_name}'. Candidates: {matches}")
    suggestions = [d for d in dims if target in _normalize_text(d)]
    raise ValueError(
        f"Dimension '{user_name}' not found. "
        f"Try one of: {suggestions or dims}"
    )

def main():
    ap = argparse.ArgumentParser(description="Run 1D & 3D sensitivity analysis.")
    ap.add_argument("csv", help="Path to CSV with Dimension, Weight, ExScore, CurScore.")
    ap.add_argument("--list", action="store_true", help="List Dimension names and exit.")

    ap.add_argument("--dim", default="Emotional connection",
                    help="Dimension name for 1D sweep.")
    ap.add_argument("--low", type=float, default=0.0)
    ap.add_argument("--high", type=float, default=0.5)
    ap.add_argument("--steps", type=int, default=101)

    ap.add_argument("--tri",
        default="Emotional connection,Shared values & life goals,Aesthetics & taste",
        help="Three dims for 3D sweep, comma-separated.")
    ap.add_argument("--tri-low", type=float, default=0.05)
    ap.add_argument("--tri-high", type=float, default=0.40)
    ap.add_argument("--tri-steps", type=int, default=16)

    args = ap.parse_args()
    outdir = Path("outputs"); outdir.mkdir(exist_ok=True)

    df = _load_and_normalize(args.csv)

    if args.list:
        _list_dimensions(df)
        return

    try:
        dim_1d = _resolve_dim_name(args.dim, df)
    except Exception as e:
        print(f"[err] 1D sweep: {e}")
        print("Hint: run with --list to see exact names.")
        return

    try:
        tri_raw = [s.strip() for s in args.tri.split(",")]
        tri_dims = [_resolve_dim_name(n, df) for n in tri_raw]
    except Exception as e:
        print(f"[err] 3D sweep: {e}")
        print("Hint: run with --list to see exact names.")
        return

    # 1D
    try:
        out1 = one_dim_boundary(df, dim_name=dim_1d, low=args.low, high=args.high, steps=args.steps)
        p1 = outdir / f"boundary_{_normalize_text(dim_1d)}.csv"
        out1.to_csv(p1, index=False)
        print(f"[ok] 1D boundary -> {p1.resolve()} ({len(out1)} rows)  dimension={dim_1d}")
    except Exception as e:
        print(f"[err] 1D sweep failed: {e}")

    # 3D
    try:
        out3 = tri_dim_grid(df, dims=tri_dims, low=args.tri_low, high=args.tri_high, steps=args.tri_steps)
        p3 = outdir / "tri_sensitivity.csv"
        out3.to_csv(p3, index=False)
        print(f"[ok] 3D sensitivity -> {p3.resolve()} ({len(out3)} rows)  dims={tri_dims}")
    except Exception as e:
        print(f"[err] 3D sweep failed: {e}")

    print("Tip: diff = cur_total - ex_total; diff>0 means Current ahead; ~0 is the boundary.")

if __name__ == "__main__":
    main()
