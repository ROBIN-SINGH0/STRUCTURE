import numpy as np

# -----------------------------
# Beam Element (Euler–Bernoulli)
# -----------------------------
class BeamElement:
    def __init__(self, L):
        self.L = L

    def stiffness(self):
        L = self.L
        return (1 / L**3) * np.array([
            [12,   6*L,  -12,   6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L,   12,  -6*L],
            [6*L, 2*L**2, -6*L, 4*L**2]
        ])

    def udl_eq(self, w):
        L = self.L
        return np.array([
            -w*L/2,
            -w*L**2/12,
            -w*L/2,
             w*L**2/12
        ])

    def uvl_eq(self, w1, w2):
        L = self.L
        return np.array([
            -(7*w1 + 3*w2)*L/20,
            -(w1 + 2*w2)*L**2/60,
            -(3*w1 + 7*w2)*L/20,
             (2*w1 + w2)*L**2/60
        ])


# -----------------------------
# Beam Model
# -----------------------------
class Beam:
    def __init__(self, length):
        self.length = length
        self.supports = {}
        self.internal_hinges = set()
        self.point_loads = []
        self.udls = []
        self.uvls = []

    def add_support(self, x, stype):
        if stype == "internal_hinge":
            self.internal_hinges.add(x)
        else:
            self.supports[x] = stype

    def add_point_load(self, x, P):
        self.point_loads.append((x, P))

    def add_udl(self, x1, x2, w):
        self.udls.append((x1, x2, w))

    def add_uvl(self, x1, x2, w1, w2):
        self.uvls.append((x1, x2, w1, w2))

    # =====================================================
    # SOLVER (BOOK-STYLE POINT LOAD + CORRECT FREE-END LOGIC)
    # =====================================================
    def solve(self, npts=500, smooth_point_load=True, eps_ratio=0.15):

        # ---------- Nodes ----------
        nodes = {0, self.length}
        for x in self.supports: nodes.add(x)
        for x in self.internal_hinges: nodes.add(x)
        for x,_ in self.point_loads: nodes.add(x)
        for x1,x2,_ in self.udls: nodes.update([x1,x2])
        for x1,x2,_,_ in self.uvls: nodes.update([x1,x2])

        nodes = sorted(nodes)
        n = len(nodes)
        dof = 2 * n

        # ---------- Elements ----------
        elements = [BeamElement(nodes[i+1] - nodes[i]) for i in range(n-1)]

        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        # ---------- Stiffness ----------
        for i, el in enumerate(elements):
            k = el.stiffness()
            idx = [2*i, 2*i+1, 2*i+2, 2*i+3]
            K[np.ix_(idx, idx)] += k

        # ---------- Internal Hinges ----------
        for x in self.internal_hinges:
            i = nodes.index(x)
            r = 2*i + 1
            K[r, :] = 0
            K[:, r] = 0
            K[r, r] = 1e-9

        # ---------- POINT LOADS (SMOOTH / EXACT) ----------
        eps = eps_ratio * self.length

        for x, P in self.point_loads:
            if smooth_point_load:
                x1 = max(0.0, x - eps/2)
                x2 = min(self.length, x + eps/2)
                w = P / (x2 - x1)

                for i in range(n-1):
                    a, b = nodes[i], nodes[i+1]
                    ov = max(0, min(b, x2) - max(a, x1))
                    if ov > 0:
                        fe = elements[i].udl_eq(w * ov / (b - a))
                        F[2*i:2*i+4] += fe
            else:
                F[2 * nodes.index(x)] += P

        # ---------- UDL ----------
        for x1, x2, w in self.udls:
            for i in range(n-1):
                a, b = nodes[i], nodes[i+1]
                ov = max(0, min(b, x2) - max(a, x1))
                if ov > 0:
                    fe = elements[i].udl_eq(w * ov / (b - a))
                    F[2*i:2*i+4] += fe

        # ---------- UVL ----------
        for x1, x2, w1, w2 in self.uvls:
            for i in range(n-1):
                a, b = nodes[i], nodes[i+1]
                ov = max(0, min(b, x2) - max(a, x1))
                if ov > 0:
                    r = ov / (b - a)
                    fe = elements[i].uvl_eq(w1*r, w2*r)
                    F[2*i:2*i+4] += fe

        # ---------- Supports ----------
        fixed = []
        for x, st in self.supports.items():
            i = nodes.index(x)
            if st == "fixed":
                fixed += [2*i, 2*i+1]
            elif st in ["hinge", "roller"]:
                fixed += [2*i]

        free = list(set(range(dof)) - set(fixed))

        # ---------- Solve ----------
        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])

        # ---------- Reactions ----------
        R = K @ D - F
        reactions = {x: -R[2*nodes.index(x)] for x in self.supports}

        # ---------- Element Forces ----------
        elem_forces = []
        for i, el in enumerate(elements):
            elem_forces.append(el.stiffness() @ D[2*i:2*i+4])

        # ---------- SF & BM AT EVERY POINT ----------
        x_all, V_all, M_all = [], [], []

        for i, el in enumerate(elements):
            L = el.L
            f = elem_forces[i]

            V1, M1 = -f[0],  f[1]
            V2, M2 =  f[2], -f[3]

            for j in range(npts+1):
                xloc = j * L / npts
                V = V1 + (V2 - V1) * (xloc / L)
                M = M1*(1 - xloc/L) + M2*(xloc/L) + V1*xloc*(1 - xloc/L)

                x_all.append(nodes[i] + xloc)
                V_all.append(V)
                M_all.append(M)

        # ---------- FREE-END RULE (FIXED) ----------
        tol = 1e-6
        free_end = self.length

        for i, xv in enumerate(x_all):
            if abs(xv - free_end) < tol and free_end not in self.supports:
                # Bending moment is always zero at free end
                M_all[i] = 0.0
                # DO NOT force shear to zero if point load exists

        return {
            "reactions": reactions,
            "x": x_all,
            "shear": V_all,
            "moment": M_all
        }
