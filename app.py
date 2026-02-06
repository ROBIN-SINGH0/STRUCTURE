import streamlit as st
from beam_solver import Beam

# -----------------------------
# helpers
# -----------------------------
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

# -----------------------------
# page
# -----------------------------
st.set_page_config("Beam Reaction App", layout="centered")
st.title("🧱 Beam Reaction Calculator")
st.caption("FEM based • Cantilever fixed")

# -----------------------------
# beam
# -----------------------------
L = get_float("Beam length (m)", "4")
beam = Beam(L)

# -----------------------------
# supports
# -----------------------------
st.subheader("Supports")
n_sup = get_int("Number of supports", "1")

for i in range(n_sup):
    c1, c2 = st.columns(2)
    with c1:
        x = get_float(f"Support {i+1} position (m)", "0")
    with c2:
        stype = st.selectbox(
            f"Support {i+1} type",
            ["fixed", "hinge", "roller"],
            key=f"s{i}"
        )
    beam.add_support(x, stype)

# -----------------------------
# point loads
# -----------------------------
st.subheader("Point Loads")
n_pl = get_int("Number of point loads", "1")

for i in range(n_pl):
    c1, c2 = st.columns(2)
    with c1:
        P = get_float(f"P{i+1} (N) ↓ negative", "-10")
    with c2:
        x = get_float(f"x{i+1} (m)", str(L))
    beam.add_point_load(x, P)

# -----------------------------
# UDL
# -----------------------------
st.subheader("UDL")
n_udl = get_int("Number of UDLs", "0")

for i in range(n_udl):
    c1, c2, c3 = st.columns(3)
    with c1:
        w = get_float(f"w{i+1} (N/m)", "-2")
    with c2:
        x1 = get_float(f"Start x{i+1}", "0")
    with c3:
        x2 = get_float(f"End x{i+1}", str(L))
    beam.add_udl(x1, x2, w)

# -----------------------------
# solve
# -----------------------------
if st.button("🚀 Calculate Reactions", use_container_width=True):

    reactions = beam.solve_reactions()
    st.success("Reactions calculated")

    st.subheader("🔵 Support Reactions")

    for x, r in reactions.items():
        st.write(f"**Support at x = {x} m**")
        st.write(f"• Vertical reaction = **{abs(r['V'])} N**")
        if "M" in r:
            st.write(f"• Fixing moment = **{abs(r['M'])} N·m**")
