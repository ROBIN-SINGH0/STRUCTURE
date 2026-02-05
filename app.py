import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from beam_solver import Beam

# -------------------------------------------------
# Safe input helpers
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
# Inputs
# -------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    L = get_float("📏 Beam Length (m)", "2.0")

with col2:
    n_sup = get_int("🧱 Number of supports / internal hinges", "1")

beam = Beam(length=L)

# -------------------------------------------------
# Supports
# -------------------------------------------------
with st.expander("🧱 Supports / Internal Hinges", expanded=True):
    for i in range(n_sup):
        c1, c2 = st.columns(2)
        with c1:
            x = get_float(f"Position {i+1} (m)", "0.0")
        with c2:
            stype = st.selectbox(
                f"Type {i+1}",
                ["fixed", "hinge", "roller", "internal_hinge"],
                key=f"st{i}"
            )
        beam.add_support(x, stype)

# -------------------------------------------------
# UDL
# -------------------------------------------------
with st.expander("📐 Uniformly Distributed Load (UDL)"):
    n_udl = get_int("Number of UDLs", "1")
    for i in range(n_udl):
        c1, c2, c3 = st.columns(3)
        with c1:
            w = get_float("Intensity w (N/m)", "-1")
        with c2:
            x1 = get_float("Start x (m)", "0.5")
        with c3:
            x2 = get_float("End x (m)", "2.0")
        beam.add_udl(x1, x2, w)

# -------------------------------------------------
# Solve
# -------------------------------------------------
if st.button("🚀 Solve Beam", use_container_width=True):

    result = beam.solve(npts=200)  # more points for smooth BM

    x = result["x"]
    V = result["shear"]
    M = result["moment"]

    st.success("Analysis completed successfully")

    # -------------------------------------------------
    # TEXTBOOK-STYLE PLOTS (FIXED)
    # -------------------------------------------------
    col1, col2 = st.columns(2)

    # -------- SFD (STEP PLOT) --------
    with col1:
        fig, ax = plt.subplots()
        ax.step(x, V, where="post")
        ax.axhline(0)
        ax.set_title("Shear Force Diagram")
        ax.set_xlabel("Length (m)")
        ax.set_ylabel("Shear Force (N)")
        ax.grid(True)
        st.pyplot(fig)

    # -------- BMD (SMOOTH CURVE) --------
    with col2:
        fig, ax = plt.subplots()
        ax.plot(x, M)
        ax.axhline(0)
        ax.set_title("Bending Moment Diagram")
        ax.set_xlabel("Length (m)")
        ax.set_ylabel("Bending Moment (N·m)")
        ax.grid(True)
        st.pyplot(fig)
