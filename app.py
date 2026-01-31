import streamlit as st
from beam_solver import Beam

st.title("Beam SFD / BMD Solver (Matrix Method)")

# inputs
L = st.number_input("Beam Length (m)", value=10.0)
mesh = st.slider("Mesh size", 10, 100, 50)

E = st.number_input("Young's Modulus (Pa)", value=2e11)
I = st.number_input("Moment of Inertia (m⁴)", value=8e-6)

# create beam
beam = Beam(length=L, mesh=mesh)
for _ in range(mesh):
    beam.add_element(E, I)

# supports
st.subheader("Supports")
s1 = st.selectbox("Left support", ["fixed", "hinge", "roller"])
s2 = st.selectbox("Right support", ["fixed", "hinge", "roller"])

beam.add_support(0, s1)
beam.add_support(L, s2)

# loads
st.subheader("Loads")
P = st.number_input("Point Load (N)", value=-10000.0)
xP = st.number_input("Point Load Position (m)", value=L/2)

beam.add_point_load(xP, P)

# solve
if st.button("Solve"):
    D, R = beam.solve()
    st.write("Displacements:", D)
    st.write("Reactions:", R)
