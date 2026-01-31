import streamlit as st
from beam_solver import Beam

st.title("Beam Reaction & Bending Moment Solver")

# -------- beam ----------
L = st.number_input("Beam Length (m)", value=10.0)
beam = Beam(length=L)

# -------- supports ----------
st.subheader("Supports")
n_supports = st.number_input("Number of supports", min_value=1, step=1, value=2)

for i in range(int(n_supports)):
    xS = st.number_input(f"Support position {i+1} (m)", 0.0, L, 0.0 if i == 0 else L, key=f"sx{i}")
    stype = st.selectbox(f"Support type {i+1}", ["fixed", "hinge", "roller"], key=f"st{i}")
    beam.add_support(xS, stype)

# -------- point loads ----------
st.subheader("Point Loads")
n_loads = st.number_input("Number of point loads", min_value=0, step=1, value=0)

for i in range(int(n_loads)):
    P = st.number_input(f"Point load {i+1} (kN)", value=-10.0, key=f"P{i}")
    xP = st.number_input(f"Position of load {i+1} (m)", 0.0, L, L/2, key=f"x{i}")
    beam.add_point_load(xP, P)

# -------- UDL ----------
st.subheader("UDL (Partial or Full)")
n_udl = st.number_input("Number of UDLs", min_value=0, step=1, value=1)

for i in range(int(n_udl)):
    w = st.number_input(f"UDL value w{i+1} (kN/m)", value=-5.0, key=f"w{i}")
    x1 = st.number_input(f"UDL start x{i+1} (m)", 0.0, L, 0.0, key=f"ux1{i}")
    x2 = st.number_input(f"UDL end x{i+1} (m)", 0.0, L, L/2, key=f"ux2{i}")
    beam.add_udl(x1, x2, w)

# -------- solve ----------
if st.button("Solve"):
    reactions, BM = beam.solve()

    st.subheader("Support Reactions")
    for x, r in reactions.items():
        st.write(f"Support at x = {x} m → Reaction = {r} kN")

    st.subheader("Bending Moment")
    for i, bm in enumerate(BM):
        st.write(
            f"Span {bm[0]} m → {bm[1]} m : "
            f"M_left = {bm[2]} kN·m , M_right = {bm[3]} kN·m"
        )
