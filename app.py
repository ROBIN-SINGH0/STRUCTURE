import streamlit as st
import pandas as pd
from beam_solver import Beam

# -------------------------------------------------
# Safe input helpers (keyboard friendly)
# -------------------------------------------------
def get_float(label, default):
    val = st.text_input(label, default)
    try:
        return float(val)
    except:
        return float(default)

def get_int(label, default):
    val = st.text_input(label, default)
    try:
        return int(val)
    except:
        return int(default)

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
<h4 style='text-align:center;color:gray;'>Matrix / FEM Method</h4>
<hr>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Beam input
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    L = get_float("📏 Beam Length (m)", "6.0")

with col2:
    n_sup = get_int("🧱 Number of supports / internal hinges", "2")

beam = Beam(length=L)

# -------------------------------------------------
# Supports
# -------------------------------------------------
with st.expander("🧱 Supports / Internal Hinges", expanded=True):
    for i in range(n_sup):
        st.markdown(f"**Support / Hinge {i+1}**")

        c1, c2 = st.columns(2)

        with c1:
            x = get_float(
                f"Position {i+1} (m)",
                "0.0" if i == 0 else str(L)
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
    n_pl = get_int("Number of point loads", "0")

    for i in range(n_pl):
        c1, c2 = st.columns(2)

        with c1:
            P = get_float(f"Load P{i+1} (N)", "-1000")

        with c2:
            xP = get_float(f"Position x{i+1} (m)", str(L/2))

        beam.add_point_load(xP, P)
        st.divider()

# -------------------------------------------------
# UDL
# -------------------------------------------------
with st.expander("📐 Uniformly Distributed Load (UDL)"):
    n_udl = get_int("Number of UDLs", "0")

    for i in range(n_udl):
        c1, c2, c3 = st.columns(3)

        with c1:
            w = get_float(f"Intensity w{i+1} (N/m)", "-500")

        with c2:
            x1 = get_float(f"Start x{i+1} (m)", "0.0")

        with c3:
            x2 = get_float(f"End x{i+1} (m)", str(L))

        beam.add_udl(x1, x2, w)
        st.divider()

# -------------------------------------------------
# UVL
# -------------------------------------------------
with st.expander("📊 Uniformly Varying Load (UVL)"):
    n_uvl = get_int("Number of UVLs", "0")

    for i in range(n_uvl):
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            w1 = get_float(f"Start intensity w1{i+1}", "0")

        with c2:
            w2 = get_float(f"End intensity w2{i+1}", "-500")

        with c3:
            x1 = get_float(f"Start x{i+1}", "0.0")

        with c4:
            x2 = get_float(f"End x{i+1}", str(L))

        beam.add_uvl(x1, x2, w1, w2)
        st.divider()

# -------------------------------------------------
# Solve
# -------------------------------------------------
if st.button("🚀 Solve Beam", use_container_width=True):

    result = beam.solve()

    x = result["x"]
    V = result["shear"]
    M = result["moment"]
    reactions = result["reactions"]

    st.success("Analysis completed successfully")

    # -----------------------------
    # Reactions
    # -----------------------------
    st.markdown("## 🔵 Support Reactions")
    cols = st.columns(len(reactions))
    for i, (xp, r) in enumerate(reactions.items()):
        cols[i].metric(f"x = {xp} m", f"{r} N")

    # -----------------------------
    # SF & BM key values (LIKE reactions)
    # -----------------------------
    st.markdown("## 📌 Key Shear Force & Bending Moment Values")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🟢 Shear Force")
        st.metric("Maximum SF", f"{max(V)} N")
        st.metric("Minimum SF", f"{min(V)} N")

    with c2:
        st.markdown("### 🔴 Bending Moment")
        st.metric("Maximum BM", f"{max(M)} N·m")
        st.metric("Minimum BM", f"{min(M)} N·m")

    # -----------------------------
    # SF & BM at supports
    # -----------------------------
    st.markdown("## 🧱 SF & BM at Supports")

    for xs in beam.supports.keys():
        idx = min(range(len(x)), key=lambda i: abs(x[i] - xs))
        st.info(
            f"Support at x = {xs} m → "
            f"SF = {V[idx]} N , "
            f"BM = {M[idx]} N·m"
        )

    # -----------------------------
    # Diagrams
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🟢 Shear Force Diagram")
        st.line_chart(
            pd.DataFrame({"x": x, "Shear (N)": V}).set_index("x")
        )

    with col2:
        st.markdown("### 🔴 Bending Moment Diagram")
        st.line_chart(
            pd.DataFrame({"x": x, "Moment (N·m)": M}).set_index("x")
        )

    # -----------------------------
    # Full table
    # -----------------------------
    st.markdown("### 📋 SF & BM at Every Point")
    st.dataframe(
        pd.DataFrame({
            "x (m)": x,
            "Shear (N)": V,
            "Moment (N·m)": M
        }),
        use_container_width=True
    )
