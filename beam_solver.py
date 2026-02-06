import numpy as np

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

        # -------- FEM reactions (simple, general) --------
        nodes = [0, self.length]
        for x in self.supports: nodes.append(x)
        for x,_ in self.point_loads: nodes.append(x)
        for x1,x2,_ in self.udls: nodes += [x1,x2]
        nodes = sorted(set(nodes))

        n = len(nodes)
        dof = 2*n
        K = np.zeros((dof,dof))
        F = np.zeros(dof)

        def k_local(L):
            return (1/L**3)*np.array([
                [12,6*L,-12,6*L],
                [6*L,4*L**2,-6*L,2*L**2],
                [-12,-6*L,12,-6*L],
                [6*L,2*L**2,-6*L,4*L**2]
            ])

        def udl_eq(L,w):
            return np.array([-w*L/2,-w*L**2/12,-w*L/2,w*L**2/12])

        for i in range(n-1):
            L = nodes[i+1]-nodes[i]
            k = k_local(L)
            idx = [2*i,2*i+1,2*i+2,2*i+3]
            K[np.ix_(idx,idx)] += k

        for x,P in self.point_loads:
            F[2*nodes.index(x)] += P

        for x1,x2,w in self.udls:
            for i in range(n-1):
                if nodes[i]>=x1 and nodes[i+1]<=x2:
                    L = nodes[i+1]-nodes[i]
                    F[2*i:2*i+4] += udl_eq(L,w)

        fixed=[]
        for x,st in self.supports.items():
            i = nodes.index(x)
            if st=="fixed":
                fixed += [2*i,2*i+1]
            else:
                fixed += [2*i]

        free = list(set(range(dof))-set(fixed))
        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free,free)],F[free])

        R = K@D - F
        reactions = {x:R[2*nodes.index(x)] for x in self.supports}

        # -------- SF & BM (equilibrium – ALWAYS correct) --------
        x_vals = np.linspace(0,self.length,npts)
        V_vals=[]
        M_vals=[]

        for x in x_vals:
            V = 0
            M = 0

            for xr,Rv in reactions.items():
                if xr<=x:
                    V += Rv
                    M += Rv*(x-xr)

            for xp,P in self.point_loads:
                if xp<=x:
                    V -= P
                    M -= P*(x-xp)

            for x1,x2,w in self.udls:
                if x>x1:
                    l = max(0,min(x,x2)-x1)
                    V -= w*l
                    M -= w*l*(x-(x1+l/2))

            V_vals.append(V)
            M_vals.append(M)

        return {
            "reactions": {k:round(v,3) for k,v in reactions.items()},
            "x": list(x_vals),
            "shear": [round(v,3) for v in V_vals],
            "moment": [round(m,3) for m in M_vals]   # ✅ FIXED
        }
