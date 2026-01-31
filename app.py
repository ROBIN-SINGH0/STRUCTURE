import streamlit as st
from beam_solver import Beam

st.title("Beam Reaction & Bending Moment Solver")

# -------- beam ----------
L = st.number_input("Beam Length (m)", value=10.0)
beam = Beam(length=L)

# -------- supports ----------
st.subheader("Supports")

n_supports = st.number_input(
    "Number of supports",
    min_value=1,
    step=1,
    value=2
)

for i in range(int(n_supports)):
    st.markdown(f"**Support {i+1}**")

    xS = st.number_input(
        f"Support position x{i+1} (m)",
        min_value=0.0,
        max_value=L,
        value=0.0 if i == 0 else L,
        key=f"sx{i}"
    )

    stype = st.selectbox(
        f"Support type {i+1}",
        ["fixed", "hinge", "roller"],
        key=f"st{i}"
    )

    beam.add_support(xS, stype)

# -------- point loads ----------
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
        f"Load position x{i+1} (m)",
        min_value=0.0,
        max_value=L,
        value=L/2,
        key=f"x{i}"
    )

    beam.add_point_load(xP, P)

# -------- solve ----------
if st.button("Solve"):
    reactions, BM = beam.solve()

    st.subheader("Support Reactions")
    for x, r in reactions.items():
        st.write(f"Support at x = {x} m → Reaction = {r} kN")

    st.subheader("Bending Moment")
    for i, bm in enumerate(BM):
        st.write(
            f"Element {i+1} ({bm[0]} m → {bm[1]} m): "
            f"M_left = {bm[2]} kN·m, M_right = {bm[3]} kN·m"
        )
