import numpy as np

# ==================================================
# BEAM CLASS
# FEM → REACTIONS ONLY
# ==================================================
class Beam:
    def __init__(self, length, E=2e11, I=8e-6):
        self.beam = {"length": length}
        self.supports = []
        self.loads = []
        self.E = E
        self.I = I

    # -----------------------------
    # INPUT METHODS (for app)
    # -----------------------------
    def add_support(self, x, stype):
        self.supports.append({"pos": x, "type": stype})

    def add_point_load(self, x, P):
        self.loads.append({"type": "point", "pos": x, "value": P})

    def add_udl(self, x1, x2, w):
        self.loads.append({"type": "udl", "start": x1, "end": x2, "value": w})

    def add_uvl(self, x1, x2, w1, w2):
        # stored only (not solved yet)
        self.loads.append({
            "type": "uvl",
            "start": x1,
            "end": x2,
            "w1": w1,
            "w2": w2
        })

    # -----------------------------
    # FEM → REACTIONS ONLY
    # -----------------------------
    def solve_reactions(self):

        # ---- nodes ----
        nodes = {0, self.beam["length"]}
        for s in self.supports:
            nodes.add(s["pos"])
        for l in self.loads:
            if l["type"] == "point":
                nodes.add(l["pos"])
            else:
                nodes.add(l["start"])
                nodes.add(l["end"])

        nodes = sorted(nodes)
        idx = {x: i for i, x in enumerate(nodes)}

        # ---- elements ----
        elements = [(nodes[i], nodes[i+1]) for i in range(len(nodes)-1)]

        n = len(nodes)
        dof = 2 * n
        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        # ---- stiffness ----
        def ke(L):
            EI = self.E * self.I
            return (EI / L**3) * np.array([
                [12, 6*L, -12, 6*L],
                [6*L, 4*L**2, -6*L, 2*L**2],
                [-12, -6*L, 12, -6*L],
                [6*L, 2*L**2, -6*L, 4*L**2]
            ])

        for x1, x2 in elements:
            i, j = idx[x1], idx[x2]
            L = x2 - x1
            idof = [2*i,2*i+1,2*j,2*j+1]
            K[np.ix_(idof,idof)] += ke(L)

        # ---- loads ----
        for l in self.loads:
            if l["type"] == "point":
                F[2*idx[l["pos"]]] -= l["value"]

            elif l["type"] == "udl":
                w = l["value"]
                for x1, x2 in elements:
                    a = max(x1, l["start"])
                    b = min(x2, l["end"])
                    if b > a:
                        Le = b - a
                        i, j = idx[x1], idx[x2]
                        F[2*i]     -= w * Le / 2
                        F[2*i + 1] -= w * Le**2 / 12
                        F[2*j]     -= w * Le / 2
                        F[2*j + 1] += w * Le**2 / 12

        # ---- supports ----
        fixed = []
        for s in self.supports:
            i = idx[s["pos"]]
            if s["type"] == "fixed":
                fixed += [2*i, 2*i+1]
            else:
                fixed.append(2*i)

        free = sorted(set(range(dof)) - set(fixed))

        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
        R = K @ D - F

        reactions = []
        for s in self.supports:
            i = idx[s["pos"]]
            r = {"Fy": R[2*i]}
            r["M"] = R[2*i+1] if s["type"]=="fixed" else 0.0
            reactions.append({"node": s["pos"], "reaction": r})

        return reactions

    # -----------------------------
    # APP SOLVER
    # -----------------------------
    def solve(self, npts=300):
        reactions = self.solve_reactions()
        x, V, M = compute_sfd_bmd(
            self.beam,
            self.loads,
            reactions,
            n=npts
        )

        return {
            "x": x,
            "shear": V,
            "moment": M,
            "reactions": {
                r["node"]: r["reaction"]["Fy"]
                for r in reactions
            }
        }


# ==================================================
# STATICS → SFD & BMD
# ==================================================
def compute_sfd_bmd(beam, loads, reactions, n=300):
    L = beam["length"]
    x = np.linspace(0, L, n)
    V = np.zeros(n)
    M = np.zeros(n)

    Rf = {r["node"]: r["reaction"]["Fy"] for r in reactions}
    Rm = {r["node"]: r["reaction"].get("M", 0) for r in reactions}
    offset = -Rm.get(0, 0)

    for i, xi in enumerate(x):
        shear = 0
        moment = 0

        for a, R in Rf.items():
            if xi >= a:
                shear += R
                moment += R * (xi - a)

        for l in loads:
            if l["type"] == "point" and xi >= l["pos"]:
                shear -= l["value"]
                moment -= l["value"] * (xi - l["pos"])

            elif l["type"] == "udl" and xi >= l["start"]:
                b = min(xi, l["end"])
                Ld = b - l["start"]
                shear -= l["value"] * Ld
                moment -= l["value"] * Ld * (xi - (l["start"] + b)/2)

        V[i] = shear
        M[i] = moment + offset

    return x, V, M
