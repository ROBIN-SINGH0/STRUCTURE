import streamlit as st
import matplotlib.pyplot as plt
from beam_solver import Beam


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
# SF AT POINT (FRIEND LOGIC)
def sf_at_x(xp, reactions, point_loads, udls, uvls):
    Vx = 0.0

    # reactions
    for xr, R in reactions.items():
        if xp > xr:
            Vx += R

    # point loads
    for xl, P in point_loads:
        if xp > xl:
            Vx -= abs(P)

    # UDL
    for x1, x2, w in udls:
        if xp > x1:
            L = min(xp, x2) - x1
            if L > 0:
                Vx -= abs(w) * L

    # UVL
    for x1, x2, w1, w2 in uvls:
        if xp > x1:
            L = min(xp, x2) - x1
            if L > 0:
                w_avg = (abs(w1) + abs(w2)) / 2
                Vx -= w_avg * L

    return Vx


# -----------------------------
# BM AT POINT (FRIEND LOGIC)  ✅ KEEP ONLY THIS
def bm_at_x(xp, reactions, point_loads, udls, uvls):
    Mx = 0.0

    # reactions
    for xr, R in reactions.items():
        if xp > xr:
            Mx += R * (xp - xr)

    # point loads
    for xl, P in point_loads:
        if xp > xl:
            Mx -= abs(P) * (xp - xl)

    # UDL
    for x1, x2, w in udls:
        if xp > x1:
            a = x1
            b = min(xp, x2)
            if b > a:
                L = b - a
                Mx -= abs(w) * L * (xp - (a + b) / 2)

    # UVL
    for x1, x2, w1, w2 in uvls:
        if xp > x1:
            a = x1
            b = min(xp, x2)
            if b > a:
                L = b - a
                w_avg = (abs(w1) + abs(w2)) / 2
                Mx -= w_avg * L * (xp - (a + b) / 2)

    return Mx


# -----------------------------
# Page
# -----------------------------
st.set_page_config(page_title="Beam Solver – FEM", layout="wide")

st.markdown("""
<h1 style='text-align:center;'>🧱 Beam Solver</h1>
<h4 style='text-align:center;color:gray;'>
Matrix / FEM Method — Consistent Sign Convention
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

beam = Beam(length=L)


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
                ["fixed", "hinge", "roller", "internal_hinge"],
                key=f"s{i}"
            )
        beam.add_support(xs, stype)


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
            xp = get_float(f"x{i+1} (m)", str(L/2))
        beam.add_point_load(xp, P)


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
        beam.add_udl(x1, x2, w)


# -----------------------------
# UVL
# -----------------------------
with st.expander("📊 Uniformly Varying Load (UVL)"):
    n_uvl = get_int("Number of UVLs", "0")
    for i in range(n_uvl):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            w1 = get_float(f"w1{i+1}", "0")
        with c2:
            w2 = get_float(f"w2{i+1}", "-1")
        with c3:
            x1 = get_float(f"Start x{i+1}", "0.0")
        with c4:
            x2 = get_float(f"End x{i+1}", str(L))
        beam.add_uvl(x1, x2, w1, w2)


# -----------------------------
# Solve
# -----------------------------
if st.button("🚀 Solve Beam", use_container_width=True):

    result = beam.solve(npts=300)
    reactions = result["reactions"]

    st.success("Analysis completed")

    st.markdown("## 📘 Shear Force & Bending Moment (Book Answers)")

    key_points = sorted({0, L} | set(x for x, _ in beam.point_loads))

    labels = generate_labels(len(key_points))

    for lbl, xp in zip(labels, key_points):
        SF = sf_at_x(xp, reactions, beam.point_loads, beam.udls, beam.uvls)
        BM = bm_at_x(xp, reactions, beam.point_loads, beam.udls, beam.uvls)

        st.write(
            f"**Point {lbl} (x = {xp} m)** → "
            f"S.F. = {abs(round(SF, 3))} N , "
            f"B.M. = {abs(round(BM, 3))} N·m"
        )
