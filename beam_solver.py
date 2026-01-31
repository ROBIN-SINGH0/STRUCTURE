import numpy as np

# -----------------------------
# Beam Element
# -----------------------------
class BeamElement:
    def __init__(self, E, I, L):
        self.E = E
        self.I = I
        self.L = L

    def stiffness(self):
        L = self.L
        return (self.E*self.I/L**3) * np.array([
            [12, 6*L, -12, 6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L, 12, -6*L],
            [6*L, 2*L**2, -6*L, 4*L**2]
        ])

    # constant UDL
    def udl_eq(self, w):
        L = self.L
        return np.array([
            -w*L/2,
            -w*L**2/12,
            -w*L/2,
             w*L**2/12
        ])

    # triangular / trapezoidal load
    def trap_udl_eq(self, w0, wL):
        L = self.L
        return np.array([
            -(7*w0+3*wL)*L/20,
            -(w0+2*wL)*L**2/60,
            -(3*w0+7*wL)*L/20,
             (2*w0+wL)*L**2/60
        ])

    # point load inside element
    def point_inside(self, a, P):
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
    def __init__(self, length, mesh):
        self.length = length
        self.mesh = mesh
        self.dx = length / mesh
        self.nodes = [i*self.dx for i in range(mesh+1)]

        self.elements = []
        self.loads = []
        self.supports = {}

    def add_element(self, E, I):
        self.elements.append(BeamElement(E, I, self.dx))

    # -------- loads ----------
    def add_point_load(self, x, P):
        self.loads.append(("P", x, P))

    def add_udl(self, x1, x2, w):
        self.loads.append(("UDL", x1, x2, w))

    def add_trapezoidal_load(self, x1, x2, w0, wL):
        self.loads.append(("TRAP", x1, x2, w0, wL))

    def add_moment(self, x, M):
        self.loads.append(("M", x, M))

    # -------- supports ----------
    def add_support(self, x, stype):
        self.supports[x] = stype.lower()

    # -------- solver ----------
    def solve(self):
        n = len(self.nodes)
        dof = 2*n
        K = np.zeros((dof, dof))
        F = np.zeros(dof)

        # assemble stiffness
        for i, el in enumerate(self.elements):
            k = el.stiffness()
            idx = [2*i,2*i+1,2*i+2,2*i+3]
            for a in range(4):
                for b in range(4):
                    K[idx[a], idx[b]] += k[a,b]

        # apply loads
        for L in self.loads:

            if L[0] == "P":
                x, P = L[1], L[2]
                i = int(x/self.dx)
                a = x - i*self.dx
                fe = self.elements[i].point_inside(a, P)
                idx = [2*i,2*i+1,2*i+2,2*i+3]
                for j in range(4):
                    F[idx[j]] += fe[j]

            elif L[0] == "UDL":
                x1,x2,w = L[1:]
                i1,i2 = int(x1/self.dx), int(x2/self.dx)
                for i in range(i1,i2):
                    fe = self.elements[i].udl_eq(w)
                    idx = [2*i,2*i+1,2*i+2,2*i+3]
                    for j in range(4):
                        F[idx[j]] += fe[j]

            elif L[0] == "TRAP":
                x1,x2,w0,wL = L[1:]
                i1,i2 = int(x1/self.dx), int(x2/self.dx)
                for i in range(i1,i2):
                    fe = self.elements[i].trap_udl_eq(w0,wL)
                    idx = [2*i,2*i+1,2*i+2,2*i+3]
                    for j in range(4):
                        F[idx[j]] += fe[j]

            elif L[0] == "M":
                x,M = L[1],L[2]
                n = int(x/self.dx)
                F[2*n+1] += M

        # supports → DOF fixing
        fixed = []
        for x,st in self.supports.items():
            n = int(x/self.dx)
            if st == "fixed":
                fixed += [2*n,2*n+1]
            elif st in ["hinge","roller"]:
                fixed += [2*n]

        free = list(set(range(dof)) - set(fixed))

        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free,free)], F[free])
        R = K@D - F
        return D, R 