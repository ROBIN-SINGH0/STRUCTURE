import streamlit as st
from beam_solver import Beam

def get_float(label, default):
    v = st.text_input(label, default)
    try:
        return float(v)
    except:
        return float(default)

def get_int(label, default):
    v = st.text_input(label, default)
    try:
        return int(v)
    except:
        return int(default)

st.set_page_config("Beam Reaction App", layout="centered")
st.title("🧱 Beam Reaction Calculator")
st.caption("Correct cantilever physics")

L = get_float("Beam length (m)", "4")
beam = Beam(L)

st.subheader("Supports")
n_sup = get_int("Number of supports", "1")

for i in range(n_sup):
    c1, c2 = st.columns(2)
    with c1:
        x = get_float(f"Support {i+1} position", "0")
    with c2:
        stype = st.selectbox(
            f"Support {i+1} type",
            ["fixed", "hinge", "roller"],
            key=f"s{i}"
        )
    beam.add_support(x, stype)

st.subheader("Point Loads")
n_pl = get_int("Number of point loads", "1")

for i in range(n_pl):
    c1, c2 = st.columns(2)
    with c1:
        P = get_float(f"P{i+1} (N) ↓ negative", "-10")
    with c2:
        x = get_float(f"x{i+1} (m)", str(L))
    beam.add_point_load(x, P)

if st.button("🚀 Calculate Reactions", use_container_width=True):
    reactions = beam.solve_reactions()
    st.success("Reactions calculated")

    st.subheader("🔵 Support Reactions (ONLY)")
    for x, r in reactions.items():
        st.write(f"Support at x = **{x} m**")
        st.write(f"• Vertical reaction = **{abs(r['V'])} N**")
        if "M" in r:
            st.write(f"• Fixing moment = **{abs(r['M'])} N·m**")
