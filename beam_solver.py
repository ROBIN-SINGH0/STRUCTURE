import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# SIGN CONVENTION
# +Fy upward
# +M clockwise
# Downward loads are negative
# --------------------------------------------------

# ==================================================
# BEAM CLASS (FEM → REACTIONS ONLY)
# ==================================================
class Beam:
    def __init__(self, beam, supports, loads, E=2e11, I=8e-6):
        self.beam = beam
        self.supports = supports
        self.loads = loads
        self.E = E
        self.I = I
        self.nodes = []
        self.elements = []
        self._build_nodes()
        self._build_elements()
        self.node_index = {x: i for i, x in enumerate(self.nodes)}

    # -----------------------------
    # CREATE NODES
    # -----------------------------
    def _build_nodes(self):
        pos = {0, self.beam["length"]}

        for s in self.supports:
            pos.add(s["pos"])

        for l in self.loads:
            if l["type"] == "point":
                pos.add(l["pos"])
            elif l["type"] == "udl":
                pos.add(l["start"])
                pos.add(l["end"])

        self.nodes = sorted(pos)

    # -----------------------------
    # CREATE ELEMENTS
    # -----------------------------
    def _build_elements(self):
        for i in range(len(self.nodes) - 1):
            self.elements.append((self.nodes[i], self.nodes[i + 1]))

    # -----------------------------
    # ELEMENT STIFFNESS (Euler–Bernoulli)
    # -----------------------------
    def element_stiffness(self, L):
        EI = self.E * self.I
        return (EI / L**3) * np.array([
            [12,    6*L,   -12,   6*L],
            [6*L,  4*L**2, -6*L, 2*L**2],
            [-12,  -6*L,    12,  -6*L],
            [6*L,  2*L**2, -6*L, 4*L**2]
        ])

    # -----------------------------
    # SOLVE → REACTIONS ONLY (FEM)
    # -----------------------------
    def solve_reactions(self):
        n = len(self.nodes)
        dof = 2 * n

        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        # Assemble stiffness matrix
        for x1, x2 in self.elements:
            i = self.node_index[x1]
            j = self.node_index[x2]
            L = x2 - x1
            ke = self.element_stiffness(L)
            idx = [2*i, 2*i+1, 2*j, 2*j+1]
            K[np.ix_(idx, idx)] += ke

        # Apply loads (FEM-consistent)
        for l in self.loads:

            # Point load
            if l["type"] == "point":
                i = self.node_index[l["pos"]]
                F[2*i] -= l["value"]

            # UDL
            elif l["type"] == "udl":
                w = l["value"]
                for x1, x2 in self.elements:
                    a = max(x1, l["start"])
                    b = min(x2, l["end"])
                    if b > a:
                        L = x2 - x1
                        Le = b - a
                        r = Le / L
                        i = self.node_index[x1]
                        j = self.node_index[x2]

                        F[2*i]     -= w * L * r / 2
                        F[2*i + 1] -= w * L**2 * r / 12
                        F[2*j]     -= w * L * r / 2
                        F[2*j + 1] += w * L**2 * r / 12

        # Apply supports
        fixed = []
        for s in self.supports:
            i = self.node_index[s["pos"]]
            if s["type"] == "fixed":
                fixed += [2*i, 2*i+1]
            elif s["type"] in ["pinned", "roller"]:
                fixed.append(2*i)

        free = sorted(set(range(dof)) - set(fixed))

        # Solve
        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])

        reactions_vec = K @ D - F

        reactions = []
        for s in self.supports:
            i = self.node_index[s["pos"]]
            r = {"Fy": round(reactions_vec[2*i], 3)}
            if s["type"] == "fixed":
                r["M"] = round(reactions_vec[2*i + 1], 3)
            else:
                r["M"] = 0.0

            reactions.append({
                "node": s["pos"],
                "type": s["type"],
                "reaction": r
            })

        return reactions


# ==================================================
# SFD & BMD → PURE STATICS
# ==================================================
def compute_sfd_bmd(beam, supports, loads, reactions, n=300):
    L = beam["length"]
    x = np.linspace(0, L, n)
    V = np.zeros(n)
    M = np.zeros(n)

    reaction_forces = {r["node"]: r["reaction"]["Fy"] for r in reactions}
    reaction_moments = {r["node"]: r["reaction"].get("M", 0.0) for r in reactions}

    # Fixed-end moment offset
    moment_offset = -reaction_moments.get(0, 0.0)

    for i, xi in enumerate(x):
        shear = 0.0
        moment = 0.0

        # Reactions
        for a, R in reaction_forces.items():
            if xi >= a:
                shear += R
                moment += R * (xi - a)

        # Loads
        for l in loads:
            if l["type"] == "point" and xi >= l["pos"]:
                shear -= l["value"]
                moment -= l["value"] * (xi - l["pos"])

            elif l["type"] == "udl" and xi >= l["start"]:
                b = min(xi, l["end"])
                Ld = b - l["start"]
                shear -= l["value"] * Ld
                moment -= l["value"] * Ld * (xi - (l["start"] + b) / 2)

        V[i] = shear
        M[i] = moment + moment_offset

    return x, V, M


# ==================================================
# PLOT DIAGRAMS
# ==================================================
def plot_diagram(x, y, title, ylabel):
    y = np.where(np.abs(y) < 1e-6, 0, y)

    plt.figure(figsize=(10, 4))
    plt.plot(x, y, linewidth=3)
    plt.axhline(0, color="black")
    plt.fill_between(x, y, 0, where=y >= 0, alpha=0.3)
    plt.fill_between(x, y, 0, where=y <= 0, alpha=0.3)

    plt.title(title)
    plt.xlabel("Beam length (m)")
    plt.ylabel(ylabel)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.show()


# ==================================================
# EXAMPLE USAGE
# ==================================================
if __name__ == "__main__":

    beam = {"length": 6}

    supports = [
        {"pos": 0, "type": "fixed"}
    ]

    loads = [
        {"type": "point", "pos": 4, "value": 10},
        {"type": "udl", "start": 2, "end": 6, "value": 5}
    ]

    beam_model = Beam(beam, supports, loads)
    reactions = beam_model.solve_reactions()

    print("Reactions:")
    for r in reactions:
        print(r)

    x, V, M = compute_sfd_bmd(beam, supports, loads, reactions)

    plot_diagram(x, V, "Shear Force Diagram", "Shear Force")
    plot_diagram(x, M, "Bending Moment Diagram", "Bending Moment")
