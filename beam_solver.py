import numpy as np
import matplotlib.pyplot as plt

# ======================================================
# FEM SOLVER (REACTIONS ONLY – FRIEND LOGIC SAFE)
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

    # -----------------------------
    # DATA ADD METHODS (ONLY APPEND)
    # -----------------------------
    def add_support(self, x, stype):
        self.supports.append({
            "pos": x,
            "type": stype
        })

    def add_point_load(self, x, P):
        self.loads.append({
            "type": "point",
            "pos": x,
            "value": P
        })

    def add_udl(self, x1, x2, w):
        self.loads.append({
            "type": "udl",
            "start": x1,
            "end": x2,
            "value": w
        })

    def add_uvl(self, x1, x2, w1, w2):
        self.loads.append({
            "type": "uvl",
            "start": x1,
            "end": x2,
            "w1": w1,
            "w2": w2
        })

    # -----------------------------
    # NODE / ELEMENT SETUP
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

    def _build_elements(self):
        self.elements = []
        for i in range(len(self.nodes) - 1):
            self.elements.append((self.nodes[i], self.nodes[i + 1]))

    # -----------------------------
    # STIFFNESS MATRIX
    # -----------------------------
    def element_stiffness(self, L):
        EI = self.E * self.I
        return (EI / L**3) * np.array([
            [12,   6*L,  -12,   6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L,   12,  -6*L],
            [6*L, 2*L**2, -6*L, 4*L**2]
        ])

    # -----------------------------
    # SOLVER (REACTIONS ONLY)
    # -----------------------------
    def solve(self, npts=200):
        self._build_nodes()
        self._build_elements()

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

        reaction_dict = {}
        for s in self.supports:
            i = self.nodes.index(s["pos"])
            reaction_dict[s["pos"]] = round(reactions[2*i], 3)

        return {
            "reactions": reaction_dict
        }
