import numpy as np

# -----------------------------
# Beam Element
# -----------------------------
class BeamElement:
    def __init__(self, L):
        self.L = L

    def stiffness(self):
        L = self.L
        return (1 / L**3) * np.array([
            [12, 6*L, -12, 6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L, 12, -6*L],
            [6*L, 2*L**2, -6*L, 4*L**2]
        ])

    def point_load_eq(self, a, P):
        L = self.L
        b = L - a
        return np.array([
            -P*b*b*(3*a+b)/L**3,
            -P*a*b*b/L**2,
            -P*a*a*(3*b+a)/L**3,
             P*a*a*b/L**2
        ])


# -----------------------------
# Beam Model
# -----------------------------
class Beam:
    def __init__(self, length):
        self.length = length
        self.supports = {}        # x : type
        self.point_loads = []     # (x, P)

    def add_support(self, x, stype):
        self.supports[x] = stype.lower()

    def add_point_load(self, x, P):
        self.point_loads.append((x, P))

    def solve(self):
        # -------- create nodes ----------
        nodes = set([0, self.length])
        for x in self.supports:
            nodes.add(x)
        for x, _ in self.point_loads:
            nodes.add(x)

        nodes = sorted(nodes)
        n = len(nodes)
        dof = 2 * n

        # -------- create elements ----------
        elements = []
        for i in range(n - 1):
            L = nodes[i+1] - nodes[i]
            elements.append(BeamElement(L))

        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        # -------- assemble stiffness ----------
        for i, el in enumerate(elements):
            k = el.stiffness()
            idx = [2*i, 2*i+1, 2*i+2, 2*i+3]
            for a in range(4):
                for b in range(4):
                    K[idx[a], idx[b]] += k[a, b]

        # -------- apply point loads ----------
        for x, P in self.point_loads:
            i = nodes.index(x)
            if i < n - 1:
                fe = elements[i].point_load_eq(0, P)
                idx = [2*i, 2*i+1, 2*i+2, 2*i+3]
                for j in range(4):
                    F[idx[j]] += fe[j]
            else:
                F[2*i] += P

        # -------- apply supports ----------
        fixed = []
        for x, st in self.supports.items():
            i = nodes.index(x)
            if st == "fixed":
                fixed += [2*i, 2*i+1]
            elif st in ["hinge", "roller"]:
                fixed += [2*i]

        free = list(set(range(dof)) - set(fixed))

        # -------- solve ----------
        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])

        # -------- reactions ----------
        R = K @ D - F

        # -------- bending moment ----------
        BM = []
        for i, el in enumerate(elements):
            k = el.stiffness()
            idx = [2*i, 2*i+1, 2*i+2, 2*i+3]
            d_local = D[idx]
            f_local = k @ d_local

            M_left = f_local[1]
            M_right = -f_local[3]
            BM.append((nodes[i], nodes[i+1], M_left, M_right))

        return nodes, R, BM
