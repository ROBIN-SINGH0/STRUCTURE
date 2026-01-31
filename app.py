import streamlit as st
from beam_solver import Beam

st.title("Beam Bending Moment Solver (Matrix Method)")

# -------- inputs ----------
L = st.number_input("Beam Length (m)", value=10.0)

beam = Beam(length=L)

# -------- supports ----------
st.subheader("Supports")
left = st.selectbox("Left Support", ["fixed", "hinge", "roller"])
right = st.selectbox("Right Support", ["fixed", "hinge", "roller"])

beam.add_support(0, left)
beam.add_support(L, right)

# -------- point load ----------
st.subheader("Point Load")
P = st.number_input("Load value (kN)", value=-10.0)
xP = st.number_input("Load position (m)", value=L/2)

beam.add_point_load(xP, P)

# -------- solve ----------
if st.button("Solve"):
    nodes, R, BM = beam.solve()

    st.subheader("Reactions")
    st.write(R)

    st.subheader("Bending Moments (Element wise)")
    for i, bm in enumerate(BM):
        st.write(
            f"Element {i+1} ({bm[0]} m to {bm[1]} m): "
            f"M_left = {bm[2]:.3f}, M_right = {bm[3]:.3f}"
        )
