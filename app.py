import streamlit as st
import matplotlib.pyplot as plt
from beam_solver import Beam

st.set_page_config("Beam Solver", layout="wide")
st.title("🧱 Beam Solver (FEM – Full Logic)")

# -----------------------------
# Beam
# -----------------------------
L = st.number_input("Beam Length (m)", value=6.0, min_value=0.1)
beam = Beam(L)

# -----------------------------
# Supports
# -----------------------------
st.subheader("Supports")
n_sup = st.number_input("Number of supports", min_value=1, step=1)

for i in range(n_sup):
    c1, c2 = st.columns(2)
    xs = c1.number_input(f"Support {i+1} position (m)", value=0.0)
    stype = c2.selectbox(
        f"Support {i+1} type",
        ["fixed", "hinge", "roller", "internal_hinge"],
        key=f"s{i}"
    )
    beam.add_support(xs, stype)

# -----------------------------
# Point Loads
# -----------------------------
st.subheader("Point Loads")
n_pl = st.number_input("Number of point loads", min_value=0, step=1)

for i in range(n_pl):
    c1, c2 = st.columns(2)
    P = c1.number_input(f"P{i+1} (N, downward = negative)", value=-10.0)
    xp = c2.number_input(f"x{i+1} (m)", value=L/2)
    beam.add_point_load(xp, P)

# -----------------------------
# UDL
# -----------------------------
st.subheader("UDL (Uniformly Distributed Load)")
n_udl = st.number_input("Number of UDLs", min_value=0, step=1)

for i in range(n_udl):
    c1, c2, c3 = st.columns(3)
    w = c1.number_input(f"w{i+1} (N/m)", value=-5.0)
    x1 = c2.number_input(f"Start x{i+1} (m)", value=0.0)
    x2 = c3.number_input(f"End x{i+1} (m)", value=L)
    beam.add_udl(x1, x2, w)

# -----------------------------
# UVL
# -----------------------------
st.subheader("UVL (Uniformly Varying Load)")
n_uvl = st.number_input("Number of UVLs", min_value=0, step=1)

for i in range(n_uvl):
    c1, c2, c3, c4 = st.columns(4)
    w1 = c1.number_input(f"w1{i+1} (N/m)", value=0.0)
    w2 = c2.number_input(f"w2{i+1} (N/m)", value=-5.0)
    x1 = c3.number_input(f"Start x{i+1} (m)", value=0.0)
    x2 = c4.number_input(f"End x{i+1} (m)", value=L)
    beam.add_uvl(x1, x2, w1, w2)

# -----------------------------
# Solve
# -----------------------------
if st.button("🚀 Solve Beam", use_container_width=True):
    res = beam.solve(npts=300)

    st.success("Analysis completed")

    # Reactions
    st.subheader("Support Reactions")
    for x, r in res["reactions"].items():
        st.write(f"x = {x} m → Reaction = **{abs(r)} N**")

    # Plots
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        ax.plot(res["x"], res["shear"])
        ax.axhline(0)
        ax.set_title("Shear Force Diagram")
        ax.set_xlabel("Length (m)")
        ax.set_ylabel("Shear (N)")
        ax.grid(True)
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        ax.plot(res["x"], res["moment"])
        ax.axhline(0)
        ax.set_title("Bending Moment Diagram")
        ax.set_xlabel("Length (m)")
        ax.set_ylabel("Moment (N·m)")
        ax.grid(True)
        st.pyplot(fig)
