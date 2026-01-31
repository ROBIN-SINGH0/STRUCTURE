import streamlit as st
from beam_solver import Beam

st.title("Beam Reaction & Bending Moment Solver (Matrix Method)")

# ---------------- Beam ----------------
L = st.number_input("Beam Length (m)", value=12.0)
beam = Beam(length=L)

# ---------------- Supports ----------------
st.subheader("Supports (including internal hinge)")

n_supports = st.number_input(
    "Number of supports / hinges",
    min_value=1,
    step=1,
    value=2
)

for i in range(int(n_supports)):
    st.markdown(f"**Support / Hinge {i+1}**")

    xS = st.number_input(
        f"Position x{i+1} (m)",
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

    beam.add_support(xS, stype)

# ---------------- Point Loads ----------------
st.subheader("Point Loads")

n_loads = st.number_input(
    "Number of point loads",
    min_value=0,
    step=1,
    value=0
)

for i in range(int(n_loads)):
    st.markdown(f"**Point Load {i+1}**")

    P = st.number_input(
        f"Load value P{i+1} (kN)",
        value=-10.0,
        key=f"P{i}"
    )

    xP = st.number_input(
        f"Load position x{i+1} (m)",
        min_value=0.0,
        max_value=L,
        value=L/2,
        key=f"x{i}"
    )

    beam.add_point_load(xP, P)

# ---------------- UDL ----------------
st.subheader("UDL (Partial or Full)")

n_udl = st.number_input(
    "Number of UDLs",
    min_value=0,
    step=1,
    value=1
)

for i in range(int(n_udl)):
    st.markdown(f"**UDL {i+1}**")

    w = st.number_input(
        f"UDL value w{i+1} (kN/m)",
        value=-10.0,
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
        value=L/2,
        key=f"ux2{i}"
    )

    beam.add_udl(x1, x2, w)

# ---------------- Solve ----------------
if st.button("Solve"):
    reactions, BM = beam.solve()

    st.subheader("Support Reactions (Vertical)")
    for x, r in reactions.items():
        st.write(f"Support at x = {x} m → Reaction = {r} kN")

    st.subheader("Bending Moment (Element-wise)")
    for i, bm in enumerate(BM):
        st.write(
            f"Span {bm[0]} m → {bm[1]} m : "
            f"M_left = {bm[2]} kN·m , M_right = {bm[3]} kN·m"
        )
