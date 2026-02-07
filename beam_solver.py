import numpy as np

# =================================
# Beam Element (Euler–Bernoulli)
# =================================
class BeamElement:
    def __init__(self, L, E, I):
        self.L = L
        self.E = E
        self.I = I

    def stiffness(self):
        L = self.L
        EI = self.E * self.I
        return EI / L**3 * np.array([
            [12,   6*L,  -12,   6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L,   12,  -6*L],
            [6*L, 2*L**2, -6*L, 4*L**2]
        ])


# =================================
# FEM Solver (Reactions Only)
# =================================
class Beam:
    def __init__(self, length, n_elem=10, E=2e11, I=8e-6):
        self.L = length
        self.n = n_elem
        self.E = E
        self.I = I
        self.le = length / n_elem

        self.loads = []
        self.supports = {}

        self.ndof = 2 * (n_elem + 1)
        self.K = np.zeros((self.ndof, self.ndof))
        self.F = np.zeros(self.ndof)

    def add_support(self, x, stype):
        node = int(x / self.le)
        self.supports[node] = stype

    def add_point_load(self, P, x):
        node = int(x / self.le)
        self.loads.append(("point", P, x))
        self.F[2 * node] -= P

    def assemble(self):
        for i in range(self.n):
            elem = BeamElement(self.le, self.E, self.I)
            k = elem.stiffness()

            dof = [2*i, 2*i+1, 2*i+2, 2*i+3]
            for a in range(4):
                for b in range(4):
                    self.K[dof[a], dof[b]] += k[a, b]

    def solve_reactions(self):
        self.assemble()

        fixed = []
        for node, stype in self.supports.items():
            if stype == "fixed":
                fixed += [2*node, 2*node+1]
            else:  # pinned / roller
                fixed += [2*node]

        all_dof = np.arange(self.ndof)
        free = np.setdiff1d(all_dof, fixed)

        Kff = self.K[np.ix_(free, free)]
        Ff = self.F[free]

        Uf = np.linalg.solve(Kff, Ff)

        U = np.zeros(self.ndof)
        U[free] = Uf

        R = self.K @ U - self.F

        reactions = {}
        for node in self.supports:
            reactions[node * self.le] = R[2 * node]

        return reactions
