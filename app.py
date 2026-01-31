import streamlit as st
from beam_solver import Beam

st.title("Beam Solver (Matrix / FEM Logic)")

# ---------------- Beam ----------------
L = st.number_input("Beam Length (m)", value=2.0)
beam = Beam(length=L)

# ---------------- Supports ----------------
st.subheader("Supports / Internal Hinges")

n_sup = st.number_input(
    "Number of supports / hinges",
    min_value=1,
    step=1,
    value=2
)

for i in range(int(n_sup)):
    st.markdown(f"**Support / Hinge {i+1}**")

    x = st.number_input(
        f"Position {i+1} (m)",
        min_value=0.0,
        max_value=L,
        value=0.0 if i == 0 else L,
        key=f"sx{i}"
    )

    stype = st.selectbox(
        f"Type {i+1}",
        ["fixed", "hinge", "roller", "internal_hinge"],
        key=f"st{i}"
    )

    beam.add_support(x, stype)

# ---------------- Point Loads ----------------
st.subheader("Point Loads")

n_pl = st.number_input(
    "Number of point loads",
    min_value=0,
    step=1,
    value=0
)

for i in range(int(n_pl)):
    st.markdown(f"**Point Load {i+1}**")

    P = st.number_input(
        f"Load P{i+1} (N)",
        value=-300.0,
        key=f"P{i}"
    )

    xP = st.number_input(
        f"Load position x{i+1} (m)",
        min_value=0.0,
        max_value=L,
        value=L/2,
        key=f"xp{i}"
    )

    beam.add_point_load(xP, P)

# ---------------- UDL ----------------
st.subheader("Uniformly Distributed Load (UDL)")

n_udl = st.number_input(
    "Number of UDLs",
    min_value=0,
    step=1,
    value=0
)

for i in range(int(n_udl)):
    st.markdown(f"**UDL {i+1}**")

    w = st.number_input(
        f"UDL intensity w{i+1} (N/m)",
        value=-500.0,
        key=f"w{i}"
    )

    x1 = st.number_input(
        f"UDL start x{i+1} (m)",
        min_value=0.0,
        max_value=L,
        value=0.0,
        key=f"ux1{i}"
    )

    x2 = st.number_input(
        f"UDL end x{i+1} (m)",
        min_value=0.0,
        max_value=L,
        value=L,
        key=f"ux2{i}"
    )

    beam.add_udl(x1, x2, w)

# ---------------- UVL ----------------
st.subheader("Uniformly Varying Load (UVL)")

n_uvl = st.number_input(
    "Number of UVLs",
    min_value=0,
    step=1,
    value=0
)

for i in range(int(n_uvl)):
    st.markdown(f"**UVL {i+1}**")

    w1 = st.number_input(
        f"UVL start intensity w1{i+1} (N/m)",
        value=0.0,
        key=f"w1{i}"
    )

    w2 = st.number_input(
        f"UVL end intensity w2{i+1} (N/m)",
        value=-500.0,
        key=f"w2{i}"
    )

    x1 = st.number_input(
        f"UVL start x{i+1} (m)",
        min_value=0.0,
        max_value=L,
        value=0.0,
        key=f"vx1{i}"
    )

    x2 = st.number_input(
        f"UVL end x{i+1} (m)",
        min_value=0.0,
        max_value=L,
        value=L,
        key=f"vx2{i}"
    )

    beam.add_uvl(x1, x2, w1, w2)

# ---------------- Solve ----------------
if st.button("Solve"):
    reactions, shear, moment = beam.solve()

    st.subheader("Support Reactions (FEM)")
    for x, r in reactions.items():
        st.write(f"Reaction at x = {x} m : {r} N")

    st.subheader("Shear Force at Nodes (FEM Logic)")
    for x in sorted(shear.keys()):
        st.write(f"Shear at x = {x} m : {shear[x]} N")

    st.subheader("Bending Moment at Nodes (FEM Logic)")
    for x in sorted(moment.keys()):
        st.write(f"Moment at x = {x} m : {moment[x]} N·m")
