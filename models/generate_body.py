import numpy as np, struct, sys, time
from skimage.measure import marching_cubes
import pyfqmr
t0=time.time()
H=0.005
xs=np.arange(-0.47,0.47+1e-9,H,dtype=np.float32);ys=np.arange(-0.01,1.83+1e-9,H,dtype=np.float32);zs=np.arange(-0.18,0.2+1e-9,H,dtype=np.float32)
X,Y,Z=np.meshgrid(xs,ys,zs,indexing="ij")
P=(X,Y,Z)
def ell(p,c,r):
    x=(p[0]-c[0])/r[0];y=(p[1]-c[1])/r[1];z=(p[2]-c[2])/r[2]
    k0=np.sqrt(x*x+y*y+z*z);k1=np.sqrt((x/r[0])**2+(y/r[1])**2+(z/r[2])**2)
    return k0*(k0-1.0)/np.maximum(k1,1e-6)
def rc(p,a,b,r1,r2):
    a=np.array(a,np.float32);b=np.array(b,np.float32);ba=b-a;bb=float(ba@ba)
    pa=(p[0]-a[0],p[1]-a[1],p[2]-a[2])
    h=np.clip((pa[0]*ba[0]+pa[1]*ba[1]+pa[2]*ba[2])/bb,0,1)
    dx=pa[0]-ba[0]*h;dy=pa[1]-ba[1]*h;dz=pa[2]-ba[2]*h
    return np.sqrt(dx*dx+dy*dy+dz*dz)-(r1+(r2-r1)*h)
def belly(p,a,b,re,rm,off):
    a=np.array(a)+off;b=np.array(b)+off;m=(a+b)/2
    return smin(rc(p,a,m,re,rm),rc(p,m,b,rm,re),0.035)
def smin(a,b,k):
    h=np.maximum(k-np.abs(a-b),0)/k
    return np.minimum(a,b)-h*h*k*0.25
L=lambda a,b,t:np.array(a)*(1-t)+np.array(b)*t
prims=[]  # (label, k, fn)
def core(k,fn):prims.append((None,k,fn))
def mus(lbl,k,fn):prims.append((lbl,k,fn))
core(0.0,lambda p:ell(p,(0,1.705,0.012),(0.08,0.106,0.095)))                       # head
mus("neck",0.05,lambda p:rc(p,(0,1.49,-0.014),(0,1.64,0.0),0.082,0.06))                 # neck
core(0.06,lambda p:ell(p,(0,1.29,-0.006),(0.168,0.205,0.116)))                     # ribcage
core(0.06,lambda p:ell(p,(0,1.075,0.0),(0.128,0.16,0.098)))                        # abdomen
core(0.06,lambda p:ell(p,(0,0.93,-0.006),(0.158,0.105,0.108)))                     # pelvis
for s in (-1,1):
    S=(s*0.218,1.42,0.0);E=(s*0.31,1.125,0.0);W=(s*0.35,0.87,0.028)
    Hh=(s*0.098,0.93,0.0);K=(s*0.114,0.51,0.014);A=(s*0.12,0.085,-0.012)
    core(0.035,lambda p,S=S:rc(p,(S[0]*0.15,1.47,0.02),(S[0]*0.92,1.455,0.0),0.04,0.04))   # collarbone/shoulder girdle
    core(0.03,lambda p,S=S,E=E:rc(p,S,E,0.05,0.037))
    core(0.03,lambda p,E=E,W=W:rc(p,E,W,0.042,0.029))
    core(0.02,lambda p,W=W,s=s:ell(p,(W[0]+s*0.004,W[1]-0.072,W[2]),(0.03,0.056,0.018)))
    core(0.05,lambda p,Hh=Hh,K=K:rc(p,Hh,K,0.085,0.052))
    core(0.035,lambda p,K=K,A=A:rc(p,K,A,0.055,0.032))
    core(0.025,lambda p,s=s:ell(p,(s*0.122,0.035,0.05),(0.046,0.032,0.11)))
    mus("adductors",0.045,lambda p,Hh=Hh,K=K,s=s:ell(p,tuple(L(Hh,K,0.32)+np.array([-s*0.038,0,-0.005])),(0.048,0.13,0.055)))
    mus("abductors",0.04,lambda p,s=s:ell(p,(s*0.142,0.955,-0.018),(0.05,0.07,0.055)))
    mus("hipflexors",0.03,lambda p,s=s:ell(p,(s*0.085,0.935,0.07),(0.04,0.06,0.03)))
    mus("shins",0.025,lambda p,K=K,A=A,s=s:belly(p,L(K,A,0.1),L(K,A,0.72),0.018,0.03,np.array([s*0.012,0,0.03])))
    # muscles
    mus("chest",0.035,lambda p,s=s:ell(p,(s*0.085,1.345,0.074),(0.112,0.082,0.056)))
    mus("shoulders",0.03,lambda p,s=s:ell(p,(s*0.232,1.405,0.0),(0.08,0.09,0.082)))
    mus("traps",0.035,lambda p,s=s:ell(p,(s*0.068,1.478,-0.036),(0.088,0.056,0.056)))
    mus("lats",0.045,lambda p,s=s:ell(p,(s*0.148,1.24,-0.042),(0.07,0.16,0.05)))
    mus("obliques",0.035,lambda p,s=s:ell(p,(s*0.12,1.05,0.034),(0.046,0.1,0.056)))
    for y,z in ((1.19,0.088),(1.11,0.092),(1.03,0.09)):
        mus("abs",0.02,lambda p,s=s,y=y,z=z:ell(p,(s*0.037,y,z-0.006),(0.036,0.036,0.018)))
    mus("lowerback",0.022,lambda p,s=s:ell(p,(s*0.04,1.02,-0.074),(0.035,0.1,0.034)))
    mus("glutes",0.04,lambda p,s=s:ell(p,(s*0.078,0.885,-0.064),(0.09,0.097,0.078)))
    mus("biceps",0.022,lambda p,S=S,E=E:belly(p,L(S,E,0.2),L(S,E,0.86),0.022,0.047,np.array([0,0,0.027])))
    mus("triceps",0.024,lambda p,S=S,E=E,s=s:belly(p,L(S,E,0.1),L(S,E,0.86),0.024,0.05,np.array([s*0.006,0,-0.029])))
    mus("forearms",0.022,lambda p,E=E,W=W,s=s:belly(p,L(E,W,-0.02),L(E,W,0.78),0.026,0.052,np.array([s*0.004,0,0.008])))
    mus("quads",0.035,lambda p,Hh=Hh,K=K:belly(p,L(Hh,K,0.06),L(Hh,K,0.93),0.04,0.08,np.array([0,0,0.038])))
    mus("quads",0.025,lambda p,Hh=Hh,K=K,s=s:ell(p,tuple(L(Hh,K,0.83)+np.array([-s*0.035,0,0.03])),(0.037,0.054,0.036)))   # teardrop
    mus("hamstrings",0.035,lambda p,Hh=Hh,K=K:belly(p,L(Hh,K,0.14),L(Hh,K,0.93),0.036,0.07,np.array([0,0,-0.04])))
    mus("calves",0.025,lambda p,K=K,A=A:belly(p,L(K,A,0.04),L(K,A,0.58),0.032,0.068,np.array([0,0,-0.034])))
mus("upperback",0.035,lambda p:rc(p,(0,1.4,-0.07),(0,1.2,-0.09),0.07,0.014))
D=None
for lbl,k,fn in prims:
    d=fn(P).astype(np.float32)
    D=d if D is None else (smin(D,d,k) if k>0 else np.minimum(D,d))
print("sdf",round(time.time()-t0,1),"s",D.shape)
v,f,n,_=marching_cubes(D,0.0,spacing=(H,H,H))
v=v+np.array([xs[0],ys[0],zs[0]],np.float32)
print("mc verts",len(v),"faces",len(f))
# enforce left/right symmetry later via simplification is fine
s=pyfqmr.Simplify();s.setMesh(v,f);s.simplify_mesh(target_count=int(sys.argv[1]) if len(sys.argv)>1 else 44000,aggressiveness=5,preserve_border=True,verbose=0)
v,f,_=s.getMesh()
v=v.astype(np.float32);f=f.astype(np.int64)
print("simplified verts",len(v),"faces",len(f))
# labels: nearest muscle primitive by its own (un-blended) distance
names=["chest","shoulders","biceps","triceps","forearms","abs","quads","hamstrings","glutes","calves","lats","traps","lowerback","neck","obliques","upperback","adductors","abductors","hipflexors","shins","frontdelts","sidedelts","reardelts"]
pv=(v[:,0],v[:,1],v[:,2])
best=np.full(len(v),9.0,np.float32);lab=np.zeros(len(v),np.uint8)
second=np.full(len(v),9.0,np.float32)
per={}
for lbl,k,fn in prims:
    if lbl is None:continue
    d=fn(pv).astype(np.float32)
    per[lbl]=np.minimum(per.get(lbl,np.full(len(v),9.0,np.float32)),d)
for i,name in enumerate(names):
    if name not in per: continue
    d=per[name];m=d<best
    second=np.where(m,best,np.minimum(second,d));lab=np.where(m,i+1,lab).astype(np.uint8);best=np.where(m,d,best)
def ss(a,b,x):t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
w=ss(0.03,0.004,best)*(0.55+0.45*ss(0.0,0.012,second-best))            # fade at outer edges and at borders between muscles
lab=np.where(w>0.03,lab,0).astype(np.uint8)
# split shoulders into front / side / rear heads using position relative to each delt centre
sh=lab==2
dz=v[:,2]-0.0
front=sh&(dz>0.028);rear=sh&(dz<-0.028);side=sh&~front&~rear
lab=lab.copy();lab[front]=names.index("frontdelts")+1;lab[rear]=names.index("reardelts")+1;lab[side]=names.index("sidedelts")+1
wq=np.clip(np.round(w*255),0,255).astype(np.uint8)
mn=v.min(0);mx=v.max(0);sc=(mx-mn)
q=np.clip(np.round((v-mn)/sc*65535),0,65535).astype(np.uint16)
assert len(v)<65536
with open(sys.argv[2] if len(sys.argv)>2 else "body.bin","wb") as fh:
    fh.write(b"PDB1");fh.write(struct.pack("<II",len(v),len(f)));fh.write(struct.pack("<6f",*mn,*sc))
    fh.write(q.tobytes());fh.write(lab.tobytes());fh.write(wq.tobytes())
    if len(v)%2: fh.write(b"\0\0")   # keep alignment
    pad=(4+8+24+len(v)*6+len(v)*2+(2 if len(v)%2 else 0))%2
    fh.write(f.astype(np.uint16).tobytes())
print("labels:",{names[i]:int((lab==i+1).sum()) for i in range(len(names))})
print("done",round(time.time()-t0,1),"s")
