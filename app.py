import streamlit as st
from beam_solver import Beam

st.title("Beam Solver – Reaction, SFD & BMD")

L = st.number_input("Beam Length (m)", value=2.0)
beam = Beam(length=L)

# ---------- Supports ----------
st.subheader("Supports / Hinges")
n_supports = st.number_input("Number of supports", min_value=1, step=1, value=2)

for i in range(int(n_supports)):
    x = st.number_input(f"Support position {i+1} (m)", 0.0, L, 0.0 if i==0 else L, key=f"sx{i}")
    t = st.selectbox(f"Type {i+1}", ["fixed","hinge","roller","internal_hinge"], key=f"st{i}")
    beam.add_support(x,t)

# ---------- Loads ----------
st.subheader("Point Loads")
n_pl = st.number_input("Number of point loads", 0, step=1, value=0)
for i in range(int(n_pl)):
    P = st.number_input(f"P{i+1} (kN)", value=-10.0, key=f"P{i}")
    x = st.number_input(f"x{i+1} (m)", 0.0, L, L/2, key=f"xp{i}")
    beam.add_point_load(x,P)

st.subheader("UDL")
n_udl = st.number_input("Number of UDL", 0, step=1, value=0)
for i in range(int(n_udl)):
    w = st.number_input(f"w{i+1} (kN/m)", value=-10.0, key=f"w{i}")
    x1 = st.number_input(f"x1{i+1}",0.0,L,0.0,key=f"ux1{i}")
    x2 = st.number_input(f"x2{i+1}",0.0,L,L/2,key=f"ux2{i}")
    beam.add_udl(x1,x2,w)

# ---------- Solve ----------
if st.button("Solve"):
    reactions, data = beam.solve()

    st.subheader("Support Reactions")
    for x,r in reactions.items():
        st.write(f"Support at x={x} m → Reaction = {r} kN")

    st.subheader("Shear Force & Bending Moment")
    for d in data:
        st.write(
            f"Span {d[0]} m → {d[1]} m :  "
            f"V_left = {d[2]} kN , V_right = {d[3]} kN | "
            f"M_left = {d[4]} kN·m , M_right = {d[5]} kN·m"
        )
