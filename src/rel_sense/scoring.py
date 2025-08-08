import sys
import pandas as pd
from pathlib import Path
from .radar import radar_plot

def weighted_total(df: pd.DataFrame):
    """Return (ex_total, cur_total) with df columns: Weight, ExScore, CurScore."""
    ex = (df["Weight"] * df["ExScore"]).sum()
    cur = (df["Weight"] * df["CurScore"]).sum()
    return float(ex), float(cur)

def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    need = {"Dimension", "Weight", "ExScore", "CurScore"}
    if not need.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {need}")
    if abs(df["Weight"].sum() - 1.0) > 1e-6:
        print(f"[warn] weights sum to {df['Weight'].sum():.4f}, normalizing.")
        df["Weight"] = df["Weight"] / df["Weight"].sum()
    return df

def main(csv_path: str):
    outdir = Path("outputs")
    outdir.mkdir(exist_ok=True)

    df = load_csv(csv_path)
    ex, cur = weighted_total(df)
    print(f"Ex Total: {ex:.2f} | Current Total: {cur:.2f} | Diff (Cur-Ex): {cur-ex:.2f}")

    fig = radar_plot(df, title="Relationship radar (unweighted scores)")
    fig.savefig(outdir / "radar_unweighted.png", dpi=180, bbox_inches="tight")

    fig2 = radar_plot(df, title="Relationship radar (weighted = weight*score)", use_weight=True)
    fig2.savefig(outdir / "radar_weighted.png", dpi=180, bbox_inches="tight")

    # export weighted breakdown
    df_out = df.copy()
    df_out["ExWeighted"] = df["Weight"] * df["ExScore"]
    df_out["CurWeighted"] = df["Weight"] * df["CurScore"]
    df_out.to_excel(outdir / "breakdown.xlsx", index=False)
    print(f"[ok] charts + breakdown exported to {outdir.resolve()}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/rel_sense/scoring.py examples/relationship.csv")
        sys.exit(1)
    main(sys.argv[1])
