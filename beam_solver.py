import numpy as np

class Beam:
    def __init__(self, length):
        self.length = length
        self.supports = {}              # {x: type}
        self.point_loads = []           # (x, P)
        self.udls = []                  # (x1, x2, w)
        self.uvls = []                  # (x1, x2, w1, w2)

    def add_support(self, x, stype):
        self.supports[x] = stype

    def add_point_load(self, x, P):
        self.point_loads.append((x, P))

    def add_udl(self, x1, x2, w):
        self.udls.append((x1, x2, w))

    def add_uvl(self, x1, x2, w1, w2):
        self.uvls.append((x1, x2, w1, w2))

    # -------------------------------------------------
    # REACTIONS – internal hinge + UVL (IMPROVED)
    # -------------------------------------------------
    def solve_reactions(self):

        # ---- nodes ----
        nodes = [0, self.length]
        for x in self.supports:
            nodes.append(x)
        for x, _ in self.point_loads:
            nodes.append(x)
        for x1, x2, _ in self.udls:
            nodes += [x1, x2]
        for x1, x2, _, _ in self.uvls:
            nodes += [x1, x2]

        nodes = sorted(set(nodes))
        n = len(nodes)
        dof = 2 * n

        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        # ---- stiffness ----
        def k_local(L):
            return (1 / L**3) * np.array([
                [12, 6*L, -12, 6*L],
                [6*L, 4*L**2, -6*L, 2*L**2],
                [-12, -6*L, 12, -6*L],
                [6*L, 2*L**2, -6*L, 4*L**2]
            ])

        def udl_eq(L, w):
            return np.array([
                -w*L/2,
                -w*L**2/12,
                -w*L/2,
                 w*L**2/12
            ])

        def uvl_eq(L, w1, w2):
            return np.array([
                -(L*(2*w1+w2))/6,
                -(L**2*(3*w1+2*w2))/60,
                -(L*(w1+2*w2))/6,
                 (L**2*(2*w1+3*w2))/60
            ])

        # ---- assemble K ----
        for i in range(n-1):
            L = nodes[i+1] - nodes[i]
            idx = [2*i, 2*i+1, 2*i+2, 2*i+3]
            K[np.ix_(idx, idx)] += k_local(L)

        # ---- loads ----
        for x, P in self.point_loads:
            F[2 * nodes.index(x)] += P

        for x1, x2, w in self.udls:
            for i in range(n-1):
                if nodes[i] >= x1 and nodes[i+1] <= x2:
                    L = nodes[i+1] - nodes[i]
                    F[2*i:2*i+4] += udl_eq(L, w)

        for x1, x2, w1, w2 in self.uvls:
            for i in range(n-1):
                if nodes[i] >= x1 and nodes[i+1] <= x2:
                    L = nodes[i+1] - nodes[i]
                    F[2*i:2*i+4] += uvl_eq(L, w1, w2)

        # ---- boundary conditions ----
        fixed_dofs = []

        for x, st in self.supports.items():
            i = nodes.index(x)

            if st == "fixed":
                fixed_dofs += [2*i, 2*i+1]

            elif st in ["hinge", "roller"]:
                fixed_dofs += [2*i]

            elif st == "internal_hinge":
                fixed_dofs += [2*i]      # rotation FREE → no moment reaction

        free = list(set(range(dof)) - set(fixed_dofs))

        # ---- solve ----
        D = np.zeros(dof)
        if free:
            D[free] = np.linalg.solve(
                K[np.ix_(free, free)],
                F[free]
            )

        R = K @ D - F

        # ---- reactions ONLY AT SUPPORTS ----
        reactions = {}

        for x, st in self.supports.items():
            i = nodes.index(x)
            reactions[x] = {"V": round(R[2*i], 3)}

            if st == "fixed":
                reactions[x]["M"] = round(R[2*i+1], 3)

        return reactions
