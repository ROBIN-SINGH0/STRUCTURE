import numpy as np

# -----------------------------
# Beam Element (Euler–Bernoulli)
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

    def solve(self, npts=20):

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

        # ---------- Elements ----------
        elements = [BeamElement(nodes[i+1]-nodes[i]) for i in range(n-1)]

        K = np.zeros((dof,dof))
        F = np.zeros(dof)

        # ---------- Stiffness ----------
        for i,el in enumerate(elements):
            k = el.stiffness()
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
        for x,st in self.supports.items():
            i = nodes.index(x)
            if st=="fixed":
                fixed += [2*i,2*i+1]
            elif st in ["hinge","roller"]:
                fixed += [2*i]

        free = list(set(range(dof)) - set(fixed))

        # ---------- Solve ----------
        D = np.zeros(dof)
        D[free] = np.linalg.solve(K[np.ix_(free,free)], F[free])

        # ---------- Reactions ----------
        R = K@D - F
        reactions = {x: round(R[2*nodes.index(x)],3) for x in self.supports}

        # ---------- Element forces ----------
        elem_forces = []
        for i,el in enumerate(elements):
            f = el.stiffness() @ D[2*i:2*i+4]
            elem_forces.append(f)

       # ---------- SF & BM (STATICS BASED – FRIEND LOGIC, FIXED) ----------
        x_all, V_all, M_all = [], [], []
        
        # reactions in usable form
        reaction_forces = {}
        for xr, R in reactions.items():
            reaction_forces[xr] = R
        
        # evaluation points along beam
        x_vals = np.linspace(0, self.length, npts * len(elements))
        
            for xg in x_vals:
        
                shear = 0.0
                moment = 0.0
        
            # ---- reactions ----
        for xr, R in reaction_forces.items():
            if xg >= xr:
                shear += R
                moment += R * (xg - xr)
        
            # ---- point loads ----
        for xp, P in self.point_loads:
            if xg >= xp:
                shear += P          # P already negative for downward
                moment += P * (xg - xp)
        
            # ---- UDL ----
        for x1, x2, w in self.udls:
            if xg > x1:
                a = x1
                b = min(xg, x2)
                if b > a:
                    L = b - a
                    shear += w * L
                    moment += w * L * (xg - (a + b) / 2)
        
            # ---- UVL (average load – friend logic) ----
        for x1, x2, w1, w2 in self.uvls:
            if xg > x1:
                a = x1
                b = min(xg, x2)
                if b > a:
                    L = b - a
                    w_avg = (w1 + w2) / 2
                    shear += w_avg * L
                    moment += w_avg * L * (xg - (a + b) / 2)
        
            x_all.append(round(xg, 6))
            V_all.append(round(shear, 3))
            M_all.append(round(moment, 3))


# ---------- FREE END RULE (POST-PROCESS, CORRECT PLACE) ----------
        tol = 1e-6
        free_end = self.length
        load_at_free_end = any(abs(px - free_end) < tol for px, _ in self.point_loads)
        
        for i, xv in enumerate(x_all):
            if abs(xv - free_end) < tol and free_end not in self.supports:
                M_all[i] = 0.0
                if not load_at_free_end:
                    V_all[i] = 0.0
        
        
        # ---------- RETURN (OUTSIDE ALL LOOPS – VERY IMPORTANT) ----------
        return {
            "reactions": reactions,
            "x": x_all,
            "shear": V_all,
            "moment": M_all
        }



        
                # ---------- IMPROVED FREE-END RULE ----------
                tol = 1e-6
                free_end = self.length
        
                # check if point load exists at free end
                load_at_free_end = any(abs(px - free_end) < tol for px,_ in self.point_loads)
        
                for i, xv in enumerate(x_all):
                    if abs(xv - free_end) < tol and free_end not in self.supports:
                        # BM always zero at free end
                        M_all[i] = 0.0
        
                        # SF zero ONLY if no load at free end
                        if not load_at_free_end:
                            V_all[i] = 0.0
        
                return {
                    "reactions": reactions,
                    "x": x_all,
                    "shear": V_all,
                    "moment": M_all
                }
