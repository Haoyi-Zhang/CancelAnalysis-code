"""Small exact closure-observation pilot; independent of DAG generator/checker."""
import itertools,json,time,resource
start=time.process_time(); wall=time.monotonic()
N=4; leq=lambda a,b:a&b==a
closures=[]
for f in itertools.product(range(N),repeat=N):
 if all(leq(x,f[x]) and f[f[x]]==f[x] for x in range(N)) and all(not leq(x,y) or leq(f[x],f[y]) for x in range(N) for y in range(N)):
  closures.append(f)
records=[]
for h in (2,3):
 tested=0; strict=0; separating=0
 for q in itertools.product(range(h),repeat=N):
  if not all(not leq(x,y) or q[x]<=q[y] for x in range(N) for y in range(N)):continue
  tested+=1
  s=all(not(leq(x,y) and x!=y) or q[x]!=q[y] for x in range(N) for y in range(N))
  r=len({tuple(q[f[x]] for x in range(N)) for f in closures})==len(closures)
  assert s==r
  strict+=s;separating+=r
 records.append(dict(codomain=h,monotone_probes=tested,strict_probes=strict,closure_separating=separating))
rank=tuple(x.bit_count() for x in range(N)); bit=(0,1,0,1); swap=(0,2,1,3)
assert all(rank[swap[x]]==rank[x] for x in range(N))
assert len({tuple(rank[f[x]] for x in range(N)) for f in closures})==len(closures)
collision=None
for f,g in itertools.combinations(closures,2):
 if all(bit[f[x]]==bit[g[x]] for x in range(N)):
  collision=[list(f),list(g)];break
assert collision
r=dict(domain='Boolean lattice with two atoms',closure_count=len(closures),all_probes=records,rank_probe=list(rank),rank_is_injective=len(set(rank))==N,rank_is_automorphism_rigid=False,bit_probe=list(bit),bit_probe_distinct_closure_collision=collision,cpu_seconds=time.process_time()-start,wall_seconds=time.monotonic()-wall,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
print(json.dumps(r,indent=2))
