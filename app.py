import streamlit as st
import pandas as pd
from beam_solver import Beam

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Beam Solver – FEM",
    layout="wide"
)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown("""
<h1 style='text-align:center;'>🧱 Beam Solver</h1>
<h4 style='text-align:center;color:gray;'>
Matrix / FEM Method
</h4>
<hr>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Beam input
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    L = float(st.text_input("📏 Beam Length (m)", "6.0"))

with col2:
    n_sup = int(st.text_input(
        "🧱 Number of supports / internal hinges", "2"
    ))

beam = Beam(length=L)

# -------------------------------------------------
# Supports
# -------------------------------------------------
with st.expander("🧱 Supports / Internal Hinges", expanded=True):
    for i in range(n_sup):
        st.markdown(f"**Support / Hinge {i+1}**")

        c1, c2 = st.columns(2)

        with c1:
            x = float(st.text_input(
                f"Position {i+1} (m)",
                "0.0" if i == 0 else str(L),
                key=f"sx{i}"
            ))

        with c2:
            stype = st.selectbox(
                f"Type {i+1}",
                ["fixed", "hinge", "roller", "internal_hinge"],
                key=f"st{i}"
            )

        beam.add_support(x, stype)
        st.divider()

# -------------------------------------------------
# Point Loads
# -------------------------------------------------
with st.expander("📍 Point Loads"):
    n_pl = int(st.text_input(
        "Number of point loads", "0"
    ))

    for i in range(n_pl):
        st.markdown(f"**Point Load {i+1}**")

        c1, c2 = st.columns(2)

        with c1:
            P = float(st.text_input(
                f"Load P{i+1} (N)",
                "-1000",
                key=f"P{i}"
            ))

        with c2:
            xP = float(st.text_input(
                f"Position x{i+1} (m)",
                str(L/2),
                key=f"xp{i}"
            ))

        beam.add_point_load(xP, P)
        st.divider()

# -------------------------------------------------
# UDL
# -------------------------------------------------
with st.expander("📐 Uniformly Distributed Load (UDL)"):
    n_udl = int(st.text_input(
        "Number of UDLs", "0"
    ))

    for i in range(n_udl):
        st.markdown(f"**UDL {i+1}**")

        c1, c2, c3 = st.columns(3)

        with c1:
            w = float(st.text_input(
                f"Intensity w{i+1} (N/m)",
                "-500",
                key=f"w{i}"
            ))

        with c2:
            x1 = float(st.text_input(
                f"Start x{i+1} (m)",
                "0.0",
                key=f"ux1{i}"
            ))

        with c3:
            x2 = float(st.text_input(
                f"End x{i+1} (m)",
                str(L),
                key=f"ux2{i}"
            ))

        beam.add_udl(x1, x2, w)
        st.divider()

# -------------------------------------------------
# UVL
# -------------------------------------------------
with st.expander("📊 Uniformly Varying Load (UVL)"):
    n_uvl = int(st.text_input(
        "Number of UVLs", "0"
    ))

    for i in range(n_uvl):
        st.markdown(f"**UVL {i+1}**")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            w1 = float(st.text_input(
                f"Start intensity w1{i+1}",
                "0",
                key=f"w1{i}"
            ))

        with c2:
            w2 = float(st.text_input(
                f"End intensity w2{i+1}",
                "-500",
                key=f"w2{i}"
            ))

        with c3:
            x1 = float(st.text_input(
                f"Start x{i+1}",
                "0.0",
                key=f"vx1{i}"
            ))

        with c4:
            x2 = float(st.text_input(
                f"End x{i+1}",
                str(L),
                key=f"vx2{i}"
            ))

        beam.add_uvl(x1, x2, w1, w2)
        st.divider()

# -------------------------------------------------
# Solve
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
solve = st.button("🚀 Solve Beam", use_container_width=True)

if solve:
    result = beam.solve()

    reactions = result["reactions"]
    x = result["x"]
    V = result["shear"]
    M = result["moment"]

    st.markdown("## 📊 Results")

    # Reactions
    st.markdown("### 🔵 Support Reactions")
    cols = st.columns(len(reactions))
    for i, (xp, r) in enumerate(reactions.items()):
        cols[i].metric(f"x = {xp} m", f"{r} N")

    # Diagrams
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🟢 Shear Force Diagram")
        st.line_chart(pd.DataFrame({"x": x, "V": V}).set_index("x"))

    with c2:
        st.markdown("### 🔴 Bending Moment Diagram")
        st.line_chart(pd.DataFrame({"x": x, "M": M}).set_index("x"))

    # Table
    st.markdown("### 📋 Values at Every Point")
    st.dataframe(
        pd.DataFrame({
            "x (m)": x,
            "Shear (N)": V,
            "Moment (N·m)": M
        }),
        use_container_width=True
    )
