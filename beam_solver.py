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


# -----------------------------
# Beam Model
# -----------------------------
class Beam:
    def __init__(self, length):
        self.length = length
        self.supports = {}
        self.point_loads = []
        self.udls = []

    def add_support(self, x, stype):
        self.supports[x] = stype

    def add_point_load(self, x, P):
        self.point_loads.append((x, P))

    def add_udl(self, x1, x2, w):
        self.udls.append((x1, x2, w))

    def solve(self, npts=300):

        # ---------- FEM reactions ----------
        nodes = {0, self.length}
        for x in self.supports: nodes.add(x)
        for x,_ in self.point_loads: nodes.add(x)
        for x1,x2,_ in self.udls: nodes.update([x1,x2])

        nodes = sorted(nodes)
        n = len(nodes)
        dof = 2*n

        elements = [BeamElement(nodes[i+1]-nodes[i]) for i in range(n-1)]

        K = np.zeros((dof,dof))
        F = np.zeros(dof)

        for i,el in enumerate(elements):
            k = el.stiffness()
            idx = [2*i,2*i+1,2*i+2,2*i+3]
            K[np.ix_(idx,idx)] += k

        for x,P in self.point_loads:
            F[2*nodes.index(x)] += P

        for x1,x2,w in self.udls:
            for i in range(n-1):
                a,b = nodes[i],nodes[i+1]
                if a>=x1 and b<=x2:
                    F[2*i:2*i+4] += elements[i].udl_eq(w)

        fixed=[]
        for x,st in self.supports.items():
            i = nodes.index(x)
            if st=="fixed":
                fixed += [2*i,2*i+1]
            else:
                fixed += [2*i]

        free = list(set(range(dof)) - set(fixed))
        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free,free)], F[free])

        R = K@D - F
        reactions = {x: R[2*nodes.index(x)] for x in self.supports}

        # ---------- SHEAR FORCE (CORRECT FOR ALL) ----------
        x_vals = np.linspace(0, self.length, npts)
        V_vals = []

        for x in x_vals:
            V = 0

            # reactions
            for xr, Rv in reactions.items():
                if xr <= x:
                    V += Rv

            # point loads
            for xp,P in self.point_loads:
                if xp <= x:
                    V -= P

            # udl
            for x1,x2,w in self.udls:
                if x > x1:
                    V -= w * max(0, min(x,x2)-x1)

            V_vals.append(V)

        return {
            "reactions": {k: round(v,3) for k,v in reactions.items()},
            "x": list(x_vals),
            "shear": [round(v,3) for v in V_vals]
        }
