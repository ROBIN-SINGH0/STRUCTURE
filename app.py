import matplotlib.pyplot as plt
import numpy as np
from beam_solver import Beam

# ================================
# Statics → SFD & BMD
# ================================
def sfd_bmd(L, reactions, loads, n=400):
    x = np.linspace(0, L, n)
    V = np.zeros(n)
    M = np.zeros(n)

    for i, xi in enumerate(x):
        for xr, R in reactions.items():
            if xi >= xr:
                V[i] += R

        for load in loads:
            if load[0] == "point" and xi >= load[2]:
                V[i] -= load[1]

        if i > 0:
            dx = x[i] - x[i-1]
            M[i] = M[i-1] + V[i] * dx

    return x, V, M


# ================================
# Example
# ================================
L = 6.0
beam = Beam(length=L, n_elem=12)

beam.add_support(0, "pinned")
beam.add_support(L, "roller")

beam.add_point_load(10, 2)

reactions = beam.solve_reactions()
loads = [("point", 10, 2)]

x, V, M = sfd_bmd(L, reactions, loads)

plt.plot(x, V)
plt.title("Shear Force Diagram")
plt.axhline(0)
plt.show()

plt.plot(x, M)
plt.title("Bending Moment Diagram")
plt.axhline(0)
plt.show()
