import streamlit as st
import matplotlib.pyplot as plt
from beam_solver import Beam

st.set_page_config("Beam Solver", layout="wide")
st.title("🧱 Final Beam Solver (FEM)")

L = st.number_input("Beam Length (m)", value=6.0)

beam = Beam(L)

# -------- Supports --------
st.subheader("Supports")
n_sup = st.number_input("Number of supports", 1, step=1)

for i in range(n_sup):
    c1, c2 = st.columns(2)
    x = c1.number_input(f"x{i+1}", value=0.0)
    t = c2.selectbox(f"type{i+1}", ["fixed", "hinge", "roller", "internal_hinge"])
    beam.add_support(x, t)

# -------- Point Load --------
st.subheader("Point Load")
P = st.number_input("Load (N, downward = negative)", value=-10.0)
xp = st.number_input("Position (m)", value=L/2)
beam.add_point_load(xp, P)

# -------- Solve --------
if st.button("Solve Beam"):
    res = beam.solve()

    st.success("Solved")

    st.subheader("Reactions")
    for x, r in res["reactions"].items():
        st.write(f"x = {x} m → Reaction = {abs(r)} N")

    # -------- Plots --------
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))

    ax[0].plot(res["x"], res["shear"])
    ax[0].axhline(0)
    ax[0].set_title("Shear Force Diagram")

    ax[1].plot(res["x"], res["moment"])
    ax[1].axhline(0)
    ax[1].set_title("Bending Moment Diagram")

    st.pyplot(fig)
