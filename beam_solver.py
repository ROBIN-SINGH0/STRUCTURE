import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# SIGN CONVENTION
# +Fy upward
# +M clockwise
# Downward loads are negative
# --------------------------------------------------


# ==================================================
# BEAM CLASS
# FEM → REACTIONS ONLY
# ==================================================
class Beam:
    def __init__(self, beam=None, supports=None, loads=None, length=None,
                 E=2e11, I=8e-6):

        if length is not None:
            self.beam = {"length": length}
            self.supports = supports if supports is not None else []
            self.loads = loads if loads is not None else []
        else:
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
        self.elements = []
        for i in range(len(self.nodes) - 1):
            self.elements.append((self.nodes[i], self.nodes[i + 1]))

    # -----------------------------
    # ELEMENT STIFFNESS
    # -----------------------------
    def element_stiffness(self, L):
        EI = self.E * self.I
        return (EI / L**3) * np.array([
            [12, 6*L, -12, 6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L, 12, -6*L],
            [6*L, 2*L**2, -6*L, 4*L**2]
        ])

    # -----------------------------
    # FEM → REACTIONS ONLY
    # -----------------------------
    def solve_reactions(self):

        self._build_nodes()
        self._build_elements()
        self.node_index = {x: i for i, x in enumerate(self.nodes)}

        n = len(self.nodes)
        dof = 2 * n

        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        for x1, x2 in self.elements:
            i = self.node_index[x1]
            j = self.node_index[x2]
            L = x2 - x1
            ke = self.element_stiffness(L)
            idx = [2*i, 2*i+1, 2*j, 2*j+1]
            K[np.ix_(idx, idx)] += ke

        for l in self.loads:
            if l["type"] == "point":
                i = self.node_index[l["pos"]]
                F[2*i] -= l["value"]

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

        fixed = []
        for s in self.supports:
            i = self.node_index[s["pos"]]
            if s["type"] == "fixed":
                fixed += [2*i, 2*i+1]
            elif s["type"] in ["pinned", "roller"]:
                fixed.append(2*i)

        free = sorted(set(range(dof)) - set(fixed))

        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])

        reactions_vec = K @ D - F

        reactions = []
        for s in self.supports:
            i = self.node_index[s["pos"]]
            r = {"Fy": round(reactions_vec[2*i], 3)}
            r["M"] = round(reactions_vec[2*i + 1], 3) if s["type"] == "fixed" else 0.0
            reactions.append({"node": s["pos"], "type": s["type"], "reaction": r})

        return reactions

    # ==================================================
    # METHODS REQUIRED BY STREAMLIT APP
    # ==================================================

    def add_support(self, x, stype):
        self.supports.append({"pos": x, "type": stype})

    def add_point_load(self, x, P):
        self.loads.append({"type": "point", "pos": x, "value": P})

    def add_udl(self, x1, x2, w):
        self.loads.append({"type": "udl", "start": x1, "end": x2, "value": w})

    def add_uvl(self, x1, x2, w1, w2):
        self.loads.append({
            "type": "uvl",
            "start": x1,
            "end": x2,
            "w1": w1,
            "w2": w2
        })

    def solve(self, npts=300):
        reactions_list = self.solve_reactions()

        x, V, M = compute_sfd_bmd(
            self.beam,
            self.supports,
            self.loads,
            reactions_list,
            n=npts
        )

        reactions_dict = {r["node"]: r["reaction"]["Fy"] for r in reactions_list}

        return {
            "x": x,
            "shear": V,
            "moment": M,
            "reactions": reactions_dict
        }
