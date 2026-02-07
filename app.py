import streamlit as st
import matplotlib.pyplot as plt
from beam_solver import Beam

st.title("Beam Solver (Friend Logic)")

L = st.number_input("Beam length (m)", 1.0)
beam = Beam(length=L)

# supports
n_sup = st.number_input("Number of supports", 1, step=1)
for i in range(n_sup):
    x = st.number_input(f"Support {i+1} position", 0.0)
    t = st.selectbox(f"Type {i+1}", ["fixed","pinned","roller"])
    beam.add_support(x, t)

# point loads
n_pl = st.number_input("Point loads", 0, step=1)
for i in range(n_pl):
    P = st.number_input(f"P{i+1} (N)")
    x = st.number_input(f"x{i+1} (m)")
    beam.add_point_load(x, P)

# UDL
n_udl = st.number_input("UDLs", 0, step=1)
for i in range(n_udl):
    w = st.number_input(f"w{i+1} (N/m)")
    a = st.number_input(f"start{i+1}")
    b = st.number_input(f"end{i+1}")
    beam.add_udl(a, b, w)

if st.button("Solve"):
    result = beam.solve()

    st.write("Reactions:", result["reactions"])

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(result["x"], result["shear"])
    ax.axhline(0)
    ax.set_title("Shear Force Diagram")
    st.pyplot(fig)
    plt.close(fig)
    
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(result["x"], result["moment"])
    ax.axhline(0)
    ax.set_title("Bending Moment Diagram")
    st.pyplot(fig)
    plt.close(fig)
    
