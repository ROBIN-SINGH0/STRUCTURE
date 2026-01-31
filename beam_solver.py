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

    def solve(self):
        # -------- nodes ----------
        nodes = set([0, self.length])
        for x in self.supports: nodes.add(x)
        for x in self.internal_hinges: nodes.add(x)
        for x,_ in self.point_loads: nodes.add(x)
        for x1,x2,_ in self.udls: nodes.add(x1); nodes.add(x2)
        for x1,x2,_,_ in self.uvls: nodes.add(x1); nodes.add(x2)

        nodes = sorted(nodes)
        n = len(nodes)
        dof = 2*n

        # -------- elements ----------
        elements = []
        for i in range(n-1):
            elements.append(BeamElement(nodes[i+1]-nodes[i]))

        K = np.zeros((dof,dof))
        F = np.zeros(dof)

        # -------- stiffness ----------
        for i,el in enumerate(elements):
            k = el.stiffness()
            idx = [2*i,2*i+1,2*i+2,2*i+3]
            for a in range(4):
                for b in range(4):
                    K[idx[a],idx[b]] += k[a,b]

        # -------- internal hinge ----------
        for x in self.internal_hinges:
            i = nodes.index(x)
            r = 2*i+1
            K[r,:] = 0
            K[:,r] = 0
            K[r,r] = 1e-9

        # -------- point loads ----------
        for x,P in self.point_loads:
            i = nodes.index(x)
            F[2*i] += P

        # -------- UDL ----------
        for x1,x2,w in self.udls:
            for i in range(n-1):
                a,b = nodes[i], nodes[i+1]
                overlap = max(0, min(b,x2)-max(a,x1))
                if overlap > 0:
                    fe = elements[i].udl_eq(w * overlap/(b-a))
                    idx=[2*i,2*i+1,2*i+2,2*i+3]
                    for j in range(4): F[idx[j]] += fe[j]

        # -------- UVL ----------
        for x1,x2,w1,w2 in self.uvls:
            for i in range(n-1):
                a,b = nodes[i], nodes[i+1]
                overlap = max(0, min(b,x2)-max(a,x1))
                if overlap > 0:
                    r = overlap/(b-a)
                    fe = elements[i].uvl_eq(w1*r, w2*r)
                    idx=[2*i,2*i+1,2*i+2,2*i+3]
                    for j in range(4): F[idx[j]] += fe[j]

        # -------- supports ----------
        fixed=[]
        for x,st in self.supports.items():
            i=nodes.index(x)
            if st=="fixed": fixed+=[2*i,2*i+1]
            elif st in ["hinge","roller"]: fixed+=[2*i]

        free=list(set(range(dof))-set(fixed))

        # -------- solve ----------
        D=np.zeros(dof)
        D[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])

        # -------- reactions ----------
        R=K@D-F
        reactions={}
        for x in self.supports:
            i=nodes.index(x)
            reactions[x]=round(R[2*i],3)

        # -------- SFD + BMD ----------
        results=[]
        for i,el in enumerate(elements):
            f = el.stiffness() @ D[[2*i,2*i+1,2*i+2,2*i+3]]

            V_left  = round(-f[0],3)
            V_right = round(f[2],3)
            M_left  = round(f[1],3)
            M_right = round(-f[3],3)

            if nodes[i] in self.internal_hinges: M_left = 0
            if nodes[i+1] in self.internal_hinges: M_right = 0

            results.append((
                nodes[i], nodes[i+1],
                V_left, V_right,
                M_left, M_right
            ))

        return reactions, results
