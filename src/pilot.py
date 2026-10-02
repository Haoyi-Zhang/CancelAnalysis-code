"""Bounded exact pilot; no imports from any eventual implementation."""
import itertools, json, resource, time
start=time.process_time(); wall=time.monotonic()
order=lambda x,y:(x & y)==x
n=4
maps=[p for p in itertools.permutations(range(n)) if all(not order(x,y) or order(p[x],p[y]) for x in range(n) for y in range(n))]
idmap=tuple(range(n)); swap=next(p for p in maps if p!=idmap)
compose=lambda a,b:tuple(a[b[x]] for x in range(n))
fixed=[]
for p,q in itertools.product(maps,repeat=2):
 ip=tuple(p.index(x) for x in range(n)); iq=tuple(q.index(x) for x in range(n))
 assert compose(ip,p)==compose(iq,q)==idmap
 fixed.append({'left_prefix':p,'right_prefix':q,'locally_natural':p==q})
probe=(0,1,0,1)
stab=[g for g in maps if tuple(probe[g[x]] for x in range(n))==probe]
assert len(stab)==1 and len(set(probe))<n
# A monotone non-injective observation cannot reflect arbitrary monotone maps.
# Constant maps into two points with the same observation form a counterexample.
a,b=next((a,b) for a in range(n) for b in range(a+1,n) if probe[a]==probe[b])
# Three-point conventional interval lattice is not distributive.
intervals=[frozenset()]+[frozenset(range(a,b+1)) for a in range(3) for b in range(a,3)]
meet=lambda a,b:a&b
join=lambda a,b: frozenset(range(min(a|b),max(a|b)+1)) if a|b else frozenset()
x,y,z=frozenset([1]),frozenset([0]),frozenset([2])
assert meet(x,join(y,z))!=join(meet(x,y),meet(x,z))
out={'pilot':'finite rigidity and cancellation falsification','workers':1,'lattice_elements':4,'automorphisms':maps,'fixed_output_factorizations':len(fixed),'locally_natural_factorizations':sum(c['locally_natural'] for c in fixed),'minimal_generator_witness':{'arrow':[0,1],'node':0,'input':1,'left':1,'right':swap[1]},'noninjective_probe':probe,'probe_stabilizer_size':len(stab),'unrestricted_monotone_counterexample_pair':[a,b],'full_interval_distributivity_counterexample':{'x':list(x),'y':list(y),'z':list(z),'left':list(meet(x,join(y,z))),'right':list(join(meet(x,y),meet(x,z)))},'cpu_seconds':time.process_time()-start,'wall_seconds':time.monotonic()-wall,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
print(json.dumps(out,indent=2))
