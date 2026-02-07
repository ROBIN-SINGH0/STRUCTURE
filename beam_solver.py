import numpy as np
import matplotlib.pyplot as plt

# ======================================================
# FEM SOLVER (REACTIONS ONLY – SAME LOGIC)
# ======================================================

class Beam:
    def __init__(self, data, E=2e11, I=8e-6):
        self.beam = data["beam"]
        self.supports = data["supports"]
        self.loads = data["loads"]
        self.E = E
        self.I = I
        self.nodes = []
        self.elements = []
        self._build_nodes()
        self._build_elements()

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

    def _build_elements(self):
        for i in range(len(self.nodes) - 1):
            self.elements.append((self.nodes[i], self.nodes[i + 1]))

    def element_stiffness(self, L):
        EI = self.E * self.I
        return (EI / L**3) * np.array([
            [12,   6*L,  -12,   6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L,   12,  -6*L],
            [6*L, 2*L**2, -6*L, 4*L**2]
        ])

    def solve(self):
        n = len(self.nodes)
        dof = 2 * n

        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        # stiffness assembly
        for e in self.elements:
            i = self.nodes.index(e[0])
            j = self.nodes.index(e[1])
            L = e[1] - e[0]
            ke = self.element_stiffness(L)
            idx = [2*i, 2*i+1, 2*j, 2*j+1]
            for a in range(4):
                for b in range(4):
                    K[idx[a], idx[b]] += ke[a, b]

        # loads
        for l in self.loads:
            if l["type"] == "point":
                i = self.nodes.index(l["pos"])
                F[2*i] -= l["value"]

            elif l["type"] == "udl":
                w = l["value"]
                for e in self.elements:
                    x1, x2 = e
                    a = max(x1, l["start"])
                    b = min(x2, l["end"])
                    if b > a:
                        Le = b - a
                        i = self.nodes.index(x1)
                        j = self.nodes.index(x2)
                        F[2*i]     -= w * Le / 2
                        F[2*i + 1] -= w * Le**2 / 12
                        F[2*j]     -= w * Le / 2
                        F[2*j + 1] += w * Le**2 / 12

        # supports
        fixed = []
        for s in self.supports:
            i = self.nodes.index(s["pos"])
            if s["type"] == "fixed":
                fixed += [2*i, 2*i+1]
            else:
                fixed.append(2*i)

        free = sorted(set(range(dof)) - set(fixed))
        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])

        reactions = K @ D - F

        results = []
        for s in self.supports:
            i = self.nodes.index(s["pos"])
            results.append({
                "node": s["pos"],
                "reaction": {"Fy": round(reactions[2*i], 3)}
            })

        return results


# ======================================================
# FRIEND LOGIC – RIGHT SIDE (SFD & BMD)
# ======================================================

def sf_at_x(xp, reactions, loads):
    V = 0.0

    for r in reactions:
        if r["node"] > xp:
            V -= r["reaction"]["Fy"]

    for l in loads:
        if l["type"] == "point" and l["pos"] > xp:
            V += abs(l["value"])

        elif l["type"] == "udl":
            a = max(xp, l["start"])
            b = l["end"]
            if b > a:
                V += abs(l["value"]) * (b - a)

    return V


def bm_at_x(xp, reactions, loads):
    M = 0.0

    for r in reactions:
        if r["node"] > xp:
            M -= r["reaction"]["Fy"] * (r["node"] - xp)

    for l in loads:
        if l["type"] == "point" and l["pos"] > xp:
            M += abs(l["value"]) * (l["pos"] - xp)

        elif l["type"] == "udl":
            a = max(xp, l["start"])
            b = l["end"]
            if b > a:
                L = b - a
                xc = (a + b) / 2
                M += abs(l["value"]) * L * (xc - xp)

    return M


def compute_sfd_bmd(beam, reactions, loads, n=200):
    L = beam["length"]
    x = np.linspace(0, L, n)
    V = [sf_at_x(xi, reactions, loads) for xi in x]
    M = [bm_at_x(xi, reactions, loads) for xi in x]
    return x, np.array(V), np.array(M)


# ======================================================
# RUN (NO FLASK)
# ======================================================

if __name__ == "__main__":

    data = {
        "beam": {"length": 2.0},
        "supports": [
            {"pos": 0.0, "type": "fixed"}
        ],
        "loads": [
            {"type": "point", "pos": 1.0, "value": 300}
        ]
    }

    solver = Beam(data)
    reactions = solver.solve()

    x, V, M = compute_sfd_bmd(
        data["beam"],
        reactions,
        data["loads"]
    )

    print("Reactions:", reactions)
    print("SF at mid:", sf_at_x(1.0, reactions, data["loads"]))
    print("BM at mid:", bm_at_x(1.0, reactions, data["loads"]))

    plt.figure(figsize=(10, 4))
    plt.plot(x, V)
    plt.axhline(0)
    plt.title("Shear Force Diagram")
    plt.show()

    plt.figure(figsize=(10, 4))
    plt.plot(x, M)
    plt.axhline(0)
    plt.title("Bending Moment Diagram")
    plt.show() 
