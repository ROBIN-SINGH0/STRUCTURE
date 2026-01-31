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

    def udl_eq(self, w):
        L = self.L
        return np.array([
            -w*L/2,
            -w*L**2/12,
            -w*L/2,
             w*L**2/12
        ])


# -----------------------------
# Beam Model
# -----------------------------
class Beam:
    def __init__(self, length):
        self.length = length
        self.supports = {}          # x : type
        self.point_loads = []       # (x, P)
        self.udls = []              # (x1, x2, w)

    def add_support(self, x, stype):
        self.supports[x] = stype.lower()

    def add_point_load(self, x, P):
        self.point_loads.append((x, P))

    def add_udl(self, x1, x2, w):
        self.udls.append((x1, x2, w))

    def solve(self):
        # -------- create nodes ----------
        nodes = set([0, self.length])
        for x in self.supports:
            nodes.add(x)
        for x, _ in self.point_loads:
            nodes.add(x)
        for x1, x2, _ in self.udls:
            nodes.add(x1)
            nodes.add(x2)

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

        # -------- apply UDL (PARTIAL UDL WORKS HERE) ----------
        for x1, x2, w in self.udls:
            for i in range(n - 1):
                a = nodes[i]
                b = nodes[i+1]

                if a >= x1 and b <= x2:
                    fe = elements[i].udl_eq(w)
                    idx = [2*i, 2*i+1, 2*i+2, 2*i+3]
                    for j in range(4):
                        F[idx[j]] += fe[j]

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
        R_full = K @ D - F

        reactions = {}
        for x in self.supports:
            i = nodes.index(x)
            Ry = R_full[2*i]
            if abs(Ry) < 1e-6:
                Ry = 0
            reactions[x] = round(Ry, 3)

        # -------- bending moment ----------
        BM = []
        for i, el in enumerate(elements):
            k = el.stiffness()
            idx = [2*i, 2*i+1, 2*i+2, 2*i+3]
            f_local = k @ D[idx]

            M_left = f_local[1]
            M_right = -f_local[3]

            if abs(M_left) < 1e-6:
                M_left = 0
            if abs(M_right) < 1e-6:
                M_right = 0

            BM.append((
                nodes[i],
                nodes[i+1],
                round(M_left, 3),
                round(M_right, 3)
            ))

        return reactions, BM
