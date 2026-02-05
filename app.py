import streamlit as st
import matplotlib.pyplot as plt
from beam_solver import Beam

# -----------------------------
# helpers
# -----------------------------
def get_float(label, default):
    val = st.text_input(label, default)
    try:
        return float(val)
    except:
        return float(default)

def get_int(label, default):
    val = st.text_input(label, default)
    try:
        return int(val)
    except:
        return int(default)

# -----------------------------
# Page
# -----------------------------
st.set_page_config(page_title="Beam Solver – FEM", layout="wide")

st.markdown("""
<h1 style='text-align:center;'>🧱 Beam Solver</h1>
<h4 style='text-align:center;color:gray;'>Matrix / FEM Method</h4>
<hr>
""", unsafe_allow_html=True)

# -----------------------------
# Beam input
# -----------------------------
col1, col2 = st.columns(2)
with col1:
    L = get_float("📏 Beam Length (m)", "2.0")
with col2:
    n_sup = get_int("🧱 Number of supports", "1")

beam = Beam(length=L)

# -----------------------------
# Supports
# -----------------------------
with st.expander("🧱 Supports", expanded=True):
    for i in range(n_sup):
        c1, c2 = st.columns(2)
        with c1:
            x = get_float(f"Support position {i+1} (m)", "0.0")
        with c2:
            stype = st.selectbox(
                f"Support type {i+1}",
                ["fixed", "hinge", "roller"],
                key=f"s{i}"
            )
        beam.add_support(x, stype)

# -----------------------------
# Point Load
# -----------------------------
with st.expander("📍 Point Load"):
    n_pl = get_int("Number of point loads", "0")
    for i in range(n_pl):
        c1, c2 = st.columns(2)
        with c1:
            P = get_float(f"P{i+1} (N, downward -)", "-1")
        with c2:
            xP = get_float(f"x{i+1} (m)", str(L/2))
        beam.add_point_load(xP, P)

# -----------------------------
# UDL
# -----------------------------
with st.expander("📐 UDL"):
    n_udl = get_int("Number of UDLs", "0")
    for i in range(n_udl):
        c1, c2, c3 = st.columns(3)
        with c1:
            w = get_float(f"w{i+1} (N/m)", "-1")
        with c2:
            x1 = get_float(f"start x{i+1}", "0.0")
        with c3:
            x2 = get_float(f"end x{i+1}", str(L))
        beam.add_udl(x1, x2, w)

# -----------------------------
# UVL
# -----------------------------
with st.expander("📊 UVL"):
    n_uvl = get_int("Number of UVLs", "0")
    for i in range(n_uvl):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            w1 = get_float(f"w1{i+1}", "0")
        with c2:
            w2 = get_float(f"w2{i+1}", "-1")
        with c3:
            x1 = get_float(f"start x{i+1}", "0.0")
        with c4:
            x2 = get_float(f"end x{i+1}", str(L))
        beam.add_uvl(x1, x2, w1, w2)

# -----------------------------
# Solve
# -----------------------------
if st.button("🚀 Solve Beam", use_container_width=True):

    result = beam.solve(npts=200)

    x = result["x"]
    V = result["shear"]
    M = result["moment"]
    reactions = result["reactions"]

    st.success("Analysis completed")

    # -----------------------------
    # REACTIONS (IMPORTANT)
    # -----------------------------
    st.markdown("## 🔵 Support Reactions")
    for xp, r in reactions.items():
        st.write(f"Reaction at x = {xp} m = **{r} N**")

    # -----------------------------
    # SF & BM ANSWERS (TEXTBOOK)
    # -----------------------------
    st.markdown("## 📘 Shear Force & Bending Moment Values")

    key_points = sorted(set([0, L] + list(reactions.keys())))

    labels = [chr(65+i) for i in range(len(key_points))]

    for lbl, xp in zip(labels, key_points):
        idx = min(range(len(x)), key=lambda i: abs(x[i] - xp))
        st.write(
            f"**S.F. at {lbl}** = {V[idx]} N , "
            f"**B.M. at {lbl}** = {M[idx]} N·m"
        )

    # -----------------------------
    # Diagrams
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        ax.step(x, V, where="post")
        ax.axhline(0)
        ax.set_title("Shear Force Diagram")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots()
        ax.plot(x, M)
        ax.axhline(0)
        ax.set_title("Bending Moment Diagram")
        ax.grid(True)
        st.pyplot(fig)
        plt.close(fig)
