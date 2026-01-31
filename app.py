import streamlit as st
from beam_solver import Beam

st.title("Beam Solver – Matrix (Stiffness) Method")

L = st.number_input("Beam Length (m)", value=2.0)
beam = Beam(length=L)

# ---------------- Supports ----------------
st.subheader("Supports / Internal Hinges")
n_sup = st.number_input("Number of supports / hinges", 1, step=1, value=2)

for i in range(int(n_sup)):
    x = st.number_input(f"Position {i+1} (m)", 0.0, L, 0.0 if i==0 else L, key=f"sx{i}")
    stype = st.selectbox(f"Type {i+1}", ["fixed","hinge","roller","internal_hinge"], key=f"st{i}")
    beam.add_support(x, stype)

# ---------------- Point Loads ----------------
st.subheader("Point Loads")
n_pl = st.number_input("Number of point loads", 0, step=1)

for i in range(int(n_pl)):
    P = st.number_input(f"Load P{i+1} (N)", value=-300.0, key=f"P{i}")
    xP = st.number_input(f"Position x{i+1} (m)", 0.0, L, L/2, key=f"xp{i}")
    beam.add_point_load(xP, P)

# ---------------- UDL ----------------
st.subheader("UDL")
n_udl = st.number_input("Number of UDLs", 0, step=1)

for i in range(int(n_udl)):
    w = st.number_input(f"UDL w{i+1} (N/m)", value=-500.0, key=f"w{i}")
    x1 = st.number_input(f"Start x{i+1}", 0.0, L, 0.0, key=f"ux1{i}")
    x2 = st.number_input(f"End x{i+1}", 0.0, L, L, key=f"ux2{i}")
    beam.add_udl(x1, x2, w)

# ---------------- UVL ----------------
st.subheader("UVL")
n_uvl = st.number_input("Number of UVLs", 0, step=1)

for i in range(int(n_uvl)):
    w1 = st.number_input(f"Start intensity w1{i+1}", value=0.0, key=f"w1{i}")
    w2 = st.number_input(f"End intensity w2{i+1}", value=-500.0, key=f"w2{i}")
    x1 = st.number_input(f"Start x{i+1}", 0.0, L, 0.0, key=f"vx1{i}")
    x2 = st.number_input(f"End x{i+1}", 0.0, L, L, key=f"vx2{i}")
    beam.add_uvl(x1, x2, w1, w2)

# ---------------- Solve ----------------
if st.button("Solve"):
    reactions, shear, moment = beam.solve()

    st.subheader("Support Reactions")
    for x,r in reactions.items():
        st.write(f"Reaction at x = {x} m : {r} N")

    st.subheader("Shear Force (FEM – nodal)")
    for x in sorted(shear):
        st.write(f"V({x}) = {shear[x]} N")

    st.subheader("Bending Moment (FEM – nodal)")
    for x in sorted(moment):
        st.write(f"M({x}) = {moment[x]} N·m")
