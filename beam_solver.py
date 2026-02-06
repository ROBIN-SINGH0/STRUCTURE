import numpy as np

class Beam:
    def __init__(self, length):
        self.length = length
        self.supports = {}          # {x: type}
        self.point_loads = []       # (x, P)
        self.udls = []              # (x1, x2, w)

    def add_support(self, x, stype):
        self.supports[x] = stype

    def add_point_load(self, x, P):
        self.point_loads.append((x, P))

    def add_udl(self, x1, x2, w):
        self.udls.append((x1, x2, w))

    # -----------------------------
    # REACTIONS ONLY (IMPROVED, SAME LOGIC)
    # -----------------------------
    def solve_reactions(self):

        # ---- nodes ----
        nodes = [0, self.length]
        for x in self.supports:
            nodes.append(x)
        for x, _ in self.point_loads:
            nodes.append(x)
        for x1, x2, _ in self.udls:
            nodes += [x1, x2]

        nodes = sorted(set(nodes))

        n = len(nodes)
        dof = 2 * n

        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        # ---- local stiffness ----
        def k_local(L):
            return (1 / L**3) * np.array([
                [12, 6*L, -12, 6*L],
                [6*L, 4*L**2, -6*L, 2*L**2],
                [-12, -6*L, 12, -6*L],
                [6*L, 2*L**2, -6*L, 4*L**2]
            ])

        def udl_eq(L, w):
            return np.array([
                -w * L / 2,
                -w * L**2 / 12,
                -w * L / 2,
                 w * L**2 / 12
            ])

        # ---- assemble K ----
        for i in range(n - 1):
            L = nodes[i + 1] - nodes[i]
            k = k_local(L)
            idx = [2*i, 2*i+1, 2*i+2, 2*i+3]
            K[np.ix_(idx, idx)] += k

        # ---- point loads ----
        for x, P in self.point_loads:
            F[2 * nodes.index(x)] += P

        # ---- UDL ----
        for x1, x2, w in self.udls:
            for i in range(n - 1):
                if nodes[i] >= x1 and nodes[i + 1] <= x2:
                    L = nodes[i + 1] - nodes[i]
                    F[2*i:2*i+4] += udl_eq(L, w)

        # ---- boundary conditions ----
        fixed = []
        for x, st in self.supports.items():
            i = nodes.index(x)
            if st == "fixed":
                fixed += [2*i, 2*i + 1]
            else:  # hinge / roller
                fixed += [2*i]

        free = list(set(range(dof)) - set(fixed))

        # ---- solve ----
        D = np.zeros(dof)
        if free:
            D[free] = np.linalg.solve(
                K[np.ix_(free, free)],
                F[free]
            )

        R = K @ D - F

        # ---- reactions ----
        reactions = {}
        for x in self.supports:
            reactions[x] = round(R[2 * nodes.index(x)], 3)

        return reactions
