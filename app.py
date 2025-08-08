import streamlit as st
import pandas as pd
from src.rel_sense.scoring import weighted_total
from src.rel_sense.radar import radar_plot
from src.rel_sense.sensitivity import one_dim_boundary, tri_dim_grid
import matplotlib.pyplot as plt

st.title("Decision & Sensitivity Playground")

up = st.file_uploader("Upload CSV (Dimension,Weight,ExScore,CurScore)", type="csv")
if up:
    df = pd.read_csv(up)
    st.dataframe(df)
    ex, cur = weighted_total(df)
    st.success(f"Ex Total: {ex:.2f} | Current Total: {cur:.2f} | Diff: {cur-ex:.2f}")

    st.subheader("Radar")
    st.pyplot(radar_plot(df, "Unweighted"))
    st.pyplot(radar_plot(df, "Weighted", use_weight=True))

    # -------- 1D sensitivity --------
    st.subheader("1D Boundary (weight sweep)")
    dim = st.selectbox("Dimension to sweep", df["Dimension"].tolist())
    low, high = st.slider("Weight range", 0.0, 0.6, (0.0, 0.5), 0.01)
    steps = st.slider("Steps", 20, 300, 101, 1)
    if st.button("Run 1D sweep"):
        out = one_dim_boundary(df, dim, low, high, steps)
        st.line_chart(out.set_index("weight")[["diff"]])
        st.download_button("Download 1D CSV", out.to_csv(index=False).encode("utf-8"),
                           f"boundary_{dim.replace(' ','_')}.csv")

    # -------- 3D sensitivity --------
    st.subheader("3D Sensitivity (three dims sweep together)")
    dims = df["Dimension"].tolist()
    dim_a = st.selectbox("Dim A", dims, index=0)
    dim_b = st.selectbox("Dim B", dims, index=1 if len(dims) > 1 else 0)
    dim_c = st.selectbox("Dim C", dims, index=2 if len(dims) > 2 else 0)
    low3, high3 = st.slider("Weight range for all three dims", 0.0, 0.6, (0.05, 0.4), 0.01)
    steps3 = st.slider("Grid steps per dim", 5, 30, 10, 1)
    eps = st.slider("Boundary threshold |diff| ≤ eps", 0.0, 0.2, 0.02, 0.005)

    if st.button("Run 3D sweep"):
        if len({dim_a, dim_b, dim_c}) < 3:
            st.error("Please choose three different dimensions.")
        else:
            out3 = tri_dim_grid(df, dims=[dim_a, dim_b, dim_c], low=low3, high=high3, steps=steps3)
            st.caption(f"3D grid generated: {len(out3)} rows. |diff| ≤ {eps} is considered boundary.")
            st.download_button("Download 3D CSV", out3.to_csv(index=False).encode("utf-8"), "tri_sensitivity.csv")

            # plot
            x, y, z = out3[dim_a], out3[dim_b], out3[dim_c]
            diff = out3["diff"]
            mask = diff.abs() <= eps
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection="3d")
            p = ax.scatter(x, y, z, c=diff, s=10)
            ax.scatter(x[mask], y[mask], z[mask], s=25, marker="^", label=f"|diff| ≤ {eps:g}")
            ax.set_xlabel(dim_a)
            ax.set_ylabel(dim_b)
            ax.set_zlabel(dim_c)
            fig.colorbar(p, ax=ax, shrink=0.6, label="Diff (Current − Ex)")
            ax.legend(loc="upper left")
            st.pyplot(fig)
