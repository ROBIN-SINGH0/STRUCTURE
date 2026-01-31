import streamlit as st
from beam_solver import Beam

st.title("Beam Solver – Reactions, Shear Force & Bending Moment")

L = st.number_input("Beam Length (m)", value=2.0)
beam = Beam(length=L)

# ---------- Supports ----------
st.subheader("Supports / Hinges")
n_sup = st.number_input("Number of supports", 1, step=1, value=2)

for i in range(int(n_sup)):
    x = st.number_input(f"Position {i+1} (m)", 0.0, L, 0.0 if i==0 else L, key=f"sx{i}")
    t = st.selectbox(f"Type {i+1}", ["fixed","hinge","roller","internal_hinge"], key=f"st{i}")
    beam.add_support(x,t)

# ---------- Point Loads ----------
st.subheader("Point Loads")
n_pl = st.number_input("Number of point loads", 0, step=1, value=0)
for i in range(int(n_pl)):
    P = st.number_input(f"P{i+1} (N)", value=-100.0, key=f"P{i}")
    x = st.number_input(f"x{i+1} (m)", 0.0, L, L/2, key=f"xp{i}")
    beam.add_point_load(x,P)

# ---------- UDL ----------
st.subheader("UDL")
n_udl = st.number_input("Number of UDLs", 0, step=1, value=0)
for i in range(int(n_udl)):
    w = st.number_input(f"w{i+1} (N/m)", value=-500.0, key=f"w{i}")
    x1 = st.number_input(f"x1{i+1}",0.0,L,0.0,key=f"ux1{i}")
    x2 = st.number_input(f"x2{i+1}",0.0,L,L/2,key=f"ux2{i}")
    beam.add_udl(x1,x2,w)

# ---------- UVL ----------
st.subheader("UVL")
n_uvl = st.number_input("Number of UVLs", 0, step=1, value=0)
for i in range(int(n_uvl)):
    w1 = st.number_input(f"w1{i+1} (N/m)", value=0.0, key=f"w1{i}")
    w2 = st.number_input(f"w2{i+1} (N/m)", value=-500.0, key=f"w2{i}")
    x1 = st.number_input(f"x1{i+1}",0.0,L,0.0,key=f"vx1{i}")
    x2 = st.number_input(f"x2{i+1}",0.0,L,L/2,key=f"vx2{i}")
    beam.add_uvl(x1,x2,w1,w2)

# ---------- Solve ----------
if st.button("Solve"):
    reactions, SF, BM = beam.solve()

    st.subheader("Support Reactions")
    for x,r in reactions.items():
        st.write(f"Reaction at x = {x} m : {r} N")

    st.subheader("Shear Force at Points (BOOK STYLE)")
    for x in sorted(SF.keys(), reverse=True):
        st.write(f"S.F at x = {x} m : {SF[x]} N")

    st.subheader("Bending Moment at Points (BOOK STYLE)")
    for x in sorted(BM.keys(), reverse=True):
        st.write(f"M at x = {x} m : {BM[x]} N·m")
