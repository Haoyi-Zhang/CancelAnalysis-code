"""Independent small group oracle; neither producer nor checker is imported."""
from __future__ import annotations
import itertools as it
import json
import sys
from pathlib import Path

def run()->dict:
    # G=Aut(B2), m=4 program objects, n=3 gates, fixed final identity.
    group=[(0,1,2,3),(0,2,1,3)]
    probes={'none':([],[]),'rank':([(0,1,1,2)],[(0,1,1,2)]),
            'first-cut':([(0,1,0,1)],[]),'both-cuts':([(0,1,0,1)],[(0,1,0,1)])}
    count={k:0 for k in probes};local=0;total=0
    def compose(a,b):return tuple(a[b[x]] for x in range(4))
    for chosen in it.product(group,repeat=8):
        prefix=[chosen[:4],chosen[4:]]
        # Every element here is an involution; no general inverse shortcut claimed.
        gates=[prefix[0],tuple(compose(prefix[1][p],prefix[0][p]) for p in range(4)),prefix[1]]
        assert all(compose(gates[2][p],compose(gates[1][p],gates[0][p]))==group[0] for p in range(4))
        total+=1;natural=all(len(set(stage))==1 for stage in gates)
        local+=int(natural)
        for name,cutprobes in probes.items():
            observed=all(len({tuple(q[prefix[i][p][x]] for x in range(4)) for p in range(4)})==1
                         for i in range(2) for q in cutprobes[i])
            count[name]+=int(observed)
    expected={'none':256,'rank':256,'first-cut':32,'both-cuts':4}
    assert count==expected and total==256 and local==4
    return {'objects':4,'gates':3,'automorphisms':2,'fixed_final':'identity',
            'factorizations':total,'locally_natural':local,'observed_natural':count}
if __name__=='__main__':
    out=run();Path(sys.argv[1]).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
