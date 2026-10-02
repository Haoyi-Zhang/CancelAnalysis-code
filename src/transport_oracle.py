"""Exhaustive B2 oracle for asymmetric cancellation, independent of all other sources."""
from __future__ import annotations
import itertools as it
import json
import sys
from pathlib import Path

def run()->dict:
    r=[[int(a&b==a) for b in range(4)] for a in range(4)]
    universe=list(it.product(range(4),repeat=4));rank=(0,1,1,2)
    def monotone(f):return all(not r[x][y] or r[f[x]][f[y]] for x in range(4) for y in range(4))
    def extensive(f):return all(r[x][f[x]] for x in range(4))
    def idempotent(f):return all(f[f[x]]==f[x] for x in range(4))
    mono=[f for f in universe if monotone(f)]
    sources=[f for f in universe if extensive(f) and idempotent(f)]
    targets=[f for f in mono if extensive(f)]
    cases=defects=hidden=equal_profiles=0
    for a,c,d in it.product(mono,sources,targets):
        lhs=[a[c[x]] for x in range(4)];rhs=[d[a[x]] for x in range(4)]
        observed=[rank[x] for x in lhs]==[rank[x] for x in rhs]
        if observed:equal_profiles+=1;assert lhs==rhs
        for x in range(4):
            cases+=1
            if lhs[x]!=rhs[x]:
                defects+=1
                if rank[lhs[x]]==rank[rhs[x]]:
                    hidden+=1;assert rank[lhs[c[x]]]!=rank[rhs[c[x]]]
    controls=[('source_idempotence',(0,1,1,3),(1,3,3,3),(2,3,2,3)),
              ('source_extensivity',(0,1,2,3),(0,1,1,3),(0,1,2,3)),
              ('transport_monotonicity',(0,0,1,2),(0,1,3,3),(0,1,2,3)),
              ('target_extensivity',(0,0,0,1),(0,1,2,3),(0,2,0,2)),
              ('target_monotonicity',(0,0,0,1),(3,3,3,3),(2,1,2,3))]
    validated=[]
    for drop,a,c,d in controls:
        hyp={'source_idempotence':idempotent(c),'source_extensivity':extensive(c),
             'transport_monotonicity':monotone(a),'target_extensivity':extensive(d),
             'target_monotonicity':monotone(d)}
        assert not hyp[drop] and all(v for k,v in hyp.items() if k!=drop)
        lhs=[a[c[x]] for x in range(4)];rhs=[d[a[x]] for x in range(4)]
        assert lhs!=rhs and [rank[x] for x in lhs]==[rank[x] for x in rhs]
        validated.append({'omitted':drop,'transport':a,'source':c,'target':d,'left':lhs,'right':rhs,
                          'equal_observed_profile':[rank[x] for x in lhs]})
    return {'monotone_transports':len(mono),'extensive_idempotent_sources':len(sources),
            'monotone_extensive_targets':len(targets),'map_triples':len(mono)*len(sources)*len(targets),
            'point_squares':cases,'defects':defects,'equal_rank_defects_repaired':hidden,
            'equal_observed_profiles':equal_profiles,'controls':validated}
if __name__=='__main__':
    r=run();Path(sys.argv[1]).write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='controls'},sort_keys=True))
