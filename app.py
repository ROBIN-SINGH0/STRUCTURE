import streamlit as st
from beam_solver import Beam

st.title("Beam Bending Moment Solver (Matrix Method)")

# -------- beam ----------
L = st.number_input("Beam Length (m)", value=10.0)
beam = Beam(length=L)

# -------- supports ----------
st.subheader("Supports")
left = st.selectbox("Left Support", ["fixed", "hinge", "roller"])
right = st.selectbox("Right Support", ["fixed", "hinge", "roller"])

beam.add_support(0, left)
beam.add_support(L, right)

# -------- multiple point loads ----------
st.subheader("Point Loads")

n_loads = st.number_input(
    "Number of point loads",
    min_value=0,
    step=1,
    value=1
)

for i in range(int(n_loads)):
    st.markdown(f"**Load {i+1}**")
    P = st.number_input(
        f"Load value P{i+1} (kN)",
        value=-10.0,
        key=f"P{i}"
    )
    xP = st.number_input(
        f"Position x{i+1} (m)",
        value=L/2,
        key=f"x{i}"
    )
    beam.add_point_load(xP, P)

# -------- solve ----------
if st.button("Solve"):
    nodes, R, BM = beam.solve()

    st.subheader("Support Reactions")
    st.write(R)

    st.subheader("Bending Moments (Element-wise)")
    for i, bm in enumerate(BM):
        st.write(
            f"Element {i+1} ({bm[0]} m → {bm[1]} m): "
            f"M_left = {bm[2]:.3f}, M_right = {bm[3]:.3f}"
        )
