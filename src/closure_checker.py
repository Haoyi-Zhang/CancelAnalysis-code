"""Independent exhaustive closure/observation verifier.

The input producer enumerates Moore families. This verifier instead enumerates
all extensive function tables, and separately filters closure axioms. It imports
neither the producer nor the DAG checker. All scalar observations into the
height-sized chain are generated in a linear extension of the order.
"""
from __future__ import annotations
import argparse
import itertools
import json
import time
from pathlib import Path


def verify(record:dict,seconds:float=105.0)->dict:
    deadline=time.monotonic()+seconds
    d=record['domain'];rel=d['leq'];n=len(rel)
    if not(1<=n<=9 and all(len(row)==n for row in rel)):raise ValueError('ORDER_BOUND')
    if not all(rel[x][x] for x in range(n)):raise ValueError('REFLEXIVITY')
    if not all(x==y or not(rel[x][y] and rel[y][x]) for x in range(n) for y in range(n)):raise ValueError('ANTISYMMETRY')
    if not all(not(rel[x][y] and rel[y][z]) or rel[x][z] for x,y,z in itertools.product(range(n),repeat=3)):raise ValueError('TRANSITIVITY')
    comparable=[(x,y) for x in range(n) for y in range(n) if rel[x][y] and x!=y]
    choices=[[y for y in range(n) if rel[x][y]] for x in range(n)]
    closures=[];trials=0
    for f in itertools.product(*choices):
        trials+=1
        if all(f[f[x]]==f[x] for x in range(n)) and all(rel[f[x]][f[y]] for x,y in comparable):
            closures.append(f)
        if trials%4096==0 and time.monotonic()>deadline:raise TimeoutError('CLOSURE_DEADLINE')
    if sorted(closures)!=sorted(tuple(f) for f in record['closures']):raise ValueError('CLOSURE_FAMILY_MISMATCH')
    rank=[0]*n
    for _ in range(n):
        previous=rank[:]
        for x,y in comparable:rank[y]=max(rank[y],previous[x]+1)
    if rank!=record['rank']:raise ValueError('RANK_MISMATCH')
    height=max(rank)+1
    order=sorted(range(n),key=lambda y:sum(rel[x][y] for x in range(n)))
    predecessors={y:[x for x in range(n) if x!=y and rel[x][y]] for y in range(n)}
    def observers(pos:int,values:list[int]):
        if pos==n:
            yield tuple(values);return
        x=order[pos]
        floor=max([values[y] for y in predecessors[x]]+[0])
        for v in range(floor,height):
            values[x]=v
            yield from observers(pos+1,values)
    obs_count=0;strict_count=0;separating_count=0;scalar_profile_comparisons=0
    for q in observers(0,[0]*n):
        obs_count+=1
        strict=all(q[x]<q[y] for x,y in comparable)
        seen=set();separating=True
        for f in closures:
            sig=tuple(q[f[x]] for x in range(n));scalar_profile_comparisons+=1
            if sig in seen:
                separating=False;break
            seen.add(sig)
        if strict!=separating:raise ValueError('CLOSURE_OBSERVER_CRITERION')
        strict_count+=strict;separating_count+=separating
        if obs_count%512==0 and time.monotonic()>deadline:raise TimeoutError('OBSERVER_DEADLINE')
    # Directly test the constructive repair of equal-rank local defects.
    defects=0;repaired=0;nested=0
    for c,d2 in itertools.product(closures,repeat=2):
        if all(rel[c[x]][d2[x]] for x in range(n)):
            nested+=1
            if not all(d2[c[x]]==d2[x] and c[d2[x]]==d2[x] for x in range(n)):
                raise ValueError('ABSORPTION')
        for x in range(n):
            if c[x]!=d2[x]:
                defects+=1
                if rank[c[x]]==rank[d2[x]]:
                    repaired+=1
                    if rank[c[c[x]]]==rank[d2[c[x]]]:raise ValueError('WITNESS_TRANSFER')
    if time.monotonic()>deadline:raise TimeoutError('PAIR_DEADLINE')
    levels=[[x for x in range(n) if rank[x]==k] for k in range(height)]
    autos=[]
    for images in itertools.product(*(list(itertools.permutations(level)) for level in levels)):
        p=list(range(n))
        for level,image in zip(levels,images):
            for x,y in zip(level,image):p[x]=y
        if all(rel[x][y]==rel[p[x]][p[y]] for x in range(n) for y in range(n)):autos.append(p)
    if not all(rank[p[x]]==rank[x] for p in autos for x in range(n)):raise ValueError('RANK_INVARIANCE')
    profiles=[{'closure':list(f),'rank_profile':[rank[f[x]] for x in range(n)],
               'fixed_points':[x for x in range(n) if f[x]==x]} for f in sorted(closures)]
    if len({tuple(r['rank_profile']) for r in profiles})!=len(closures):raise ValueError('RANK_COLLISION')
    # The larger observer alphabets are not enumerated: the theorem, not the run,
    # supplies those cases. The finite run enumerates exactly height-sized ones.
    return {'domain':record['domain']['name'],'states':n,'height':height,'closure_count':len(closures),
            'extensive_function_tables_examined':trials,'monotone_scalar_observers':obs_count,
            'strict_observers':strict_count,'closure_separating_observers':separating_count,
            'profile_comparisons':scalar_profile_comparisons,'nested_closure_pairs':nested,
            'ordered_pair_input_defects':defects,'equal_rank_defects_repaired':repaired,
            'automorphism_count':len(autos),'rank_stabilizer_size':len(autos),
            'rank_is_injective':len(set(rank))==n,'profiles':profiles}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--domain',type=int,choices=range(3));a=p.parse_args()
    if a.input.stat().st_size>4*1024*1024:raise ValueError('BYTE_LIMIT')
    records=json.loads(a.input.read_text())
    if len(records)!=3:raise ValueError('DOMAIN_COUNT')
    results=[verify(records[a.domain])] if a.domain is not None else [verify(r) for r in records]
    a.output.write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    print(json.dumps([{k:r[k] for k in ['domain','closure_count','monotone_scalar_observers','equal_rank_defects_repaired']} for r in results]))
if __name__=='__main__':main()
