import numpy as np

# ==========================================
# Beam Element (Euler–Bernoulli)
# ==========================================
class BeamElement:
    def __init__(self, L):
        self.L = L

    def stiffness(self):
        L = self.L
        return (1/L**3) * np.array([
            [12, 6*L, -12, 6*L],
            [6*L, 4*L**2, -6*L, 2*L**2],
            [-12, -6*L, 12, -6*L],
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
            -(7*w1+3*w2)*L/20,
            -(w1+2*w2)*L**2/60,
            -(3*w1+7*w2)*L/20,
             (2*w1+w2)*L**2/60
        ])


# ==========================================
# Beam Model (GENERAL)
# ==========================================
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

    def solve(self, npts=200):

        # ---------- Nodes ----------
        nodes = {0, self.length}
        for x in self.supports: nodes.add(x)
        for x in self.internal_hinges: nodes.add(x)
        for x,_ in self.point_loads: nodes.add(x)
        for x1,x2,_ in self.udls: nodes.update([x1,x2])
        for x1,x2,_,_ in self.uvls: nodes.update([x1,x2])
        nodes = sorted(nodes)

        n = len(nodes)
        dof = 2*n
        elements = [BeamElement(nodes[i+1]-nodes[i]) for i in range(n-1)]

        K = np.zeros((dof,dof))
        F = np.zeros(dof)

        # ---------- Stiffness ----------
        for i,e in enumerate(elements):
            k = e.stiffness()
            idx = [2*i,2*i+1,2*i+2,2*i+3]
            K[np.ix_(idx,idx)] += k

        # ---------- Internal hinges ----------
        for x in self.internal_hinges:
            i = nodes.index(x)
            r = 2*i + 1
            K[r,:] = 0
            K[:,r] = 0
            K[r,r] = 1e-9

        # ---------- Loads ----------
        for x,P in self.point_loads:
            F[2*nodes.index(x)] += P

        for x1,x2,w in self.udls:
            for i in range(n-1):
                a,b = nodes[i], nodes[i+1]
                ov = max(0, min(b,x2)-max(a,x1))
                if ov > 0:
                    fe = elements[i].udl_eq(w*ov/(b-a))
                    F[2*i:2*i+4] += fe

        for x1,x2,w1,w2 in self.uvls:
            for i in range(n-1):
                a,b = nodes[i], nodes[i+1]
                ov = max(0, min(b,x2)-max(a,x1))
                if ov > 0:
                    r = ov/(b-a)
                    fe = elements[i].uvl_eq(w1*r, w2*r)
                    F[2*i:2*i+4] += fe

        # ---------- Supports ----------
        fixed=[]
        for x,t in self.supports.items():
            i = nodes.index(x)
            if t=="fixed":
                fixed += [2*i,2*i+1]
            elif t in ["hinge","roller"]:
                fixed += [2*i]

        free = list(set(range(dof)) - set(fixed))

        # ---------- Solve ----------
        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free,free)], F[free])

        R = K@D - F

        # ---------- SFD & BMD ----------
        x_all,V_all,M_all = [],[],[]

        for i,e in enumerate(elements):
            L = e.L
            f = e.stiffness() @ D[2*i:2*i+4]
            V1,M1 = -f[0], f[1]
            V2,M2 = f[2], -f[3]

            for j in range(npts+1):
                xloc = j*L/npts
                V = V1 + (V2-V1)*(xloc/L)
                M = M1*(1-xloc/L) + M2*(xloc/L) + V1*xloc*(1-xloc/L)
                x_all.append(nodes[i]+xloc)
                V_all.append(V)
                M_all.append(M)

        # ---------- UNIVERSAL BOUNDARY FIX ----------
        tol = 1e-6

        # Free end
        free_end = self.length
        P_free = sum(P for x,P in self.point_loads if abs(x-free_end)<tol)

        for i,x in enumerate(x_all):
            if abs(x-free_end)<tol and free_end not in self.supports:
                M_all[i] = 0.0
                V_all[i] = P_free if abs(P_free)>tol else 0.0

        # Fixed end
        if 0 in self.supports and self.supports[0]=="fixed":
            i0 = nodes.index(0)
            for i,x in enumerate(x_all):
                if abs(x)<tol:
                    V_all[i] = R[2*i0]
                    M_all[i] = R[2*i0+1]
return {
    "reactions": reactions,
    "x": x_all,
    "shear": [round(v,3) for v in V_all],
    "moment": [round(m,3) for m in M_all]
}
