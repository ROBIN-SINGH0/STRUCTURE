import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from beam_solver import BeamStiffnessSolver, sf_at_x, bm_at_x, compute_sfd_bmd


# -----------------------------
# Helpers
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


def generate_labels(n):
    labels = []
    for i in range(n):
        s = ""
        x = i
        while True:
            s = chr(65 + x % 26) + s
            x = x // 26 - 1
            if x < 0:
                break
        labels.append(s)
    return labels


# -----------------------------
# Page
# -----------------------------
st.set_page_config(page_title="Beam Solver – FEM", layout="wide")

st.markdown("""
<h1 style='text-align:center;'>🧱 Beam Solver</h1>
<h4 style='text-align:center;color:gray;'>
FEM Reactions + Friend Right-Side SFD/BMD Logic
</h4>
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


supports = []
loads = []


# -----------------------------
# Supports
# -----------------------------
with st.expander("🧱 Supports", expanded=True):
    for i in range(n_sup):
        c1, c2 = st.columns(2)
        with c1:
            xs = get_float(f"Support position {i+1} (m)", "0.0")
        with c2:
            stype = st.selectbox(
                f"Support type {i+1}",
                ["fixed", "hinge", "roller"],
                key=f"s{i}"
            )

        supports.append({
            "pos": xs,
            "type": stype
        })


# -----------------------------
# Point Loads
# -----------------------------
with st.expander("📍 Point Loads"):
    n_pl = get_int("Number of point loads", "0")
    for i in range(n_pl):
        c1, c2 = st.columns(2)
        with c1:
            P = get_float(f"P{i+1} (N)", "-300")
        with c2:
            xp = get_float(f"x{i+1} (m)", str(L / 2))

        loads.append({
            "type": "point",
            "pos": xp,
            "value": abs(P)
        })


# -----------------------------
# UDL
# -----------------------------
with st.expander("📐 Uniformly Distributed Load (UDL)"):
    n_udl = get_int("Number of UDLs", "0")
    for i in range(n_udl):
        c1, c2, c3 = st.columns(3)
        with c1:
            w = get_float(f"w{i+1} (N/m)", "-1")
        with c2:
            x1 = get_float(f"Start x{i+1} (m)", "0.0")
        with c3:
            x2 = get_float(f"End x{i+1} (m)", str(L))

        loads.append({
            "type": "udl",
            "start": x1,
            "end": x2,
            "value": abs(w)
        })


# -----------------------------
# Solve
# -----------------------------
if st.button("🚀 Solve Beam", use_container_width=True):

    data = {
        "beam": {"length": L},
        "supports": supports,
        "loads": loads
    }

    solver = BeamStiffnessSolver(data)
    reactions = solver.solve()

    st.success("Analysis completed")

    # -----------------------------
    # SFD & BMD
    # -----------------------------
    x, V, M = compute_sfd_bmd(
        data["beam"],
        reactions,
        loads
    )

    st.markdown("## 📘 Shear Force & Bending Moment")

    key_points = sorted(
        {0, L}
        | {l["pos"] for l in loads if l["type"] == "point"}
    )

    labels = generate_labels(len(key_points))

    for lbl, xp in zip(labels, key_points):
        SF = sf_at_x(xp, reactions, loads)
        BM = bm_at_x(xp, reactions, loads)

        st.write(
            f"**Point {lbl} (x = {xp} m)** → "
            f"S.F. = {round(SF, 3)} N , "
            f"B.M. = {round(BM, 3)} N·m"
        )

    # -----------------------------
    # Plots
    # -----------------------------
    fig1, ax1 = plt.subplots()
    ax1.plot(x, V)
    ax1.axhline(0)
    ax1.set_title("Shear Force Diagram")
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    ax2.plot(x, M)
    ax2.axhline(0)
    ax2.set_title("Bending Moment Diagram")
    st.pyplot(fig2)
