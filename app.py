import streamlit as st
from beam_solver import Beam

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="Beam Solver – Matrix Method",
    layout="wide"
)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown("""
<h1 style='text-align:center;'>🧱 Beam Solver</h1>
<h4 style='text-align:center;color:gray;'>
Matrix (Stiffness / FEM) Method
</h4>
<hr>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Beam input
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    L = st.number_input("📏 Beam Length (m)", value=2.0)

with col2:
    n_sup = st.number_input(
        "🧱 Number of supports / internal hinges",
        min_value=1,
        step=1,
        value=2
    )

beam = Beam(length=L)

# -------------------------------------------------
# Supports
# -------------------------------------------------
with st.expander("🧱 Supports / Internal Hinges", expanded=True):
    for i in range(int(n_sup)):
        st.markdown(f"**Support / Hinge {i+1}**")

        c1, c2 = st.columns(2)

        with c1:
            x = st.number_input(
                f"Position {i+1} (m)",
                0.0, L,
                0.0 if i == 0 else L,
                key=f"sx{i}"
            )

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
    n_pl = st.number_input(
        "Number of point loads",
        min_value=0,
        step=1,
        value=0
    )

    for i in range(int(n_pl)):
        st.markdown(f"**Point Load {i+1}**")

        c1, c2 = st.columns(2)

        with c1:
            P = st.number_input(
                f"Load P{i+1} (N)",
                value=-300.0,
                key=f"P{i}"
            )

        with c2:
            xP = st.number_input(
                f"Position x{i+1} (m)",
                0.0, L,
                L/2,
                key=f"xp{i}"
            )

        beam.add_point_load(xP, P)
        st.divider()

# -------------------------------------------------
# UDL
# -------------------------------------------------
with st.expander("📐 Uniformly Distributed Load (UDL)"):
    n_udl = st.number_input(
        "Number of UDLs",
        min_value=0,
        step=1,
        value=0
    )

    for i in range(int(n_udl)):
        st.markdown(f"**UDL {i+1}**")

        c1, c2, c3 = st.columns(3)

        with c1:
            w = st.number_input(
                f"Intensity w{i+1} (N/m)",
                value=-500.0,
                key=f"w{i}"
            )

        with c2:
            x1 = st.number_input(
                f"Start x{i+1} (m)",
                0.0, L, 0.0,
                key=f"ux1{i}"
            )

        with c3:
            x2 = st.number_input(
                f"End x{i+1} (m)",
                0.0, L, L,
                key=f"ux2{i}"
            )

        beam.add_udl(x1, x2, w)
        st.divider()

# -------------------------------------------------
# UVL
# -------------------------------------------------
with st.expander("📊 Uniformly Varying Load (UVL)"):
    n_uvl = st.number_input(
        "Number of UVLs",
        min_value=0,
        step=1,
        value=0
    )

    for i in range(int(n_uvl)):
        st.markdown(f"**UVL {i+1}**")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            w1 = st.number_input(
                f"Start intensity w1{i+1}",
                value=0.0,
                key=f"w1{i}"
            )

        with c2:
            w2 = st.number_input(
                f"End intensity w2{i+1}",
                value=-500.0,
                key=f"w2{i}"
            )

        with c3:
            x1 = st.number_input(
                f"Start x{i+1}",
                0.0, L, 0.0,
                key=f"vx1{i}"
            )

        with c4:
            x2 = st.number_input(
                f"End x{i+1}",
                0.0, L, L,
                key=f"vx2{i}"
            )

        beam.add_uvl(x1, x2, w1, w2)
        st.divider()

# -------------------------------------------------
# Solve
# -------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
solve = st.button("🚀 Solve Beam", use_container_width=True)

if solve:
    reactions, shear, moment = beam.solve()

    st.markdown("## 📊 Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔵 Support Reactions")
        for x, r in reactions.items():
            st.success(f"x = {x} m → {r} N")

    with col2:
        st.markdown("### 🟢 Shear Force (Nodes)")
        st.line_chart(shear)

    with col3:
        st.markdown("### 🔴 Bending Moment (Nodes)")
        st.line_chart(moment)
