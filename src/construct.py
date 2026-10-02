"""Deterministic, self-contained inputs and independent producer certificates.

This module does not import checker.py. The checker does not import this module.
Case domains are concrete finite orders, not calls to an external analyzer.
"""
from __future__ import annotations
import itertools as it
import json
from pathlib import Path


def boolean(d: int) -> dict:
    n=1 << d
    return {'name':f'boolean-{d}', 'labels':[str(i) for i in range(n)],
            'leq':[[int((a&b)==a) for b in range(n)] for a in range(n)]}


def boxes() -> dict:
    values=list(it.product(range(3), repeat=2))
    return {'name':'anchored-boxes', 'labels':[str(x) for x in values],
            'leq':[[int(a[0]<=b[0] and a[1]<=b[1]) for b in values] for a in values]}


def category(bits: int) -> dict:
    m=1<<bits
    arrows=[(a,b) for a in range(m) for b in range(m) if a&b==a]
    ids={x:i for i,x in enumerate(arrows)}
    # Explicit path category of skip insertion modulo commuting insertions.
    return {'programs':[['entry']+[f'skip-{j}' for j in range(bits) if i>>j&1]+['return'] for i in range(m)],
            'arrows':[list(x) for x in arrows],
            'identities':[ids[(i,i)] for i in range(m)],
            'generators':[i for i,(a,b) in enumerate(arrows) if (b^a).bit_count()==1],
            'composition':[[ids[(arrows[b][0],arrows[a][1])] if arrows[b][1]==arrows[a][0] else None for b in range(len(arrows))] for a in range(len(arrows))]}


def lattice_join(domain:dict, a:int, b:int) -> int:
    order=domain['leq']; n=len(order)
    return next(z for z in range(n) if order[a][z] and order[b][z] and all(not(order[a][w] and order[b][w]) or order[z][w] for w in range(n)))


def involution(domain:dict) -> list[int]:
    n=len(domain['labels'])
    if domain['name']=='anchored-boxes': return [(x%3)*3+x//3 for x in range(n)]
    return [(x&~3)|((x&1)<<1)|((x&2)>>1) for x in range(n)]


def simple(domain:dict, topology:str, variant:str, bits:int=2, length:int=6) -> dict:
    n=len(domain['labels']); cat=category(bits); m=len(cat['programs'])
    if topology=='diamond':
        inc=[[0],[0],[1,2],[3]]
    else: inc=[[i] for i in range(2 if topology=='short' else length)]
    base=[]
    for parents in inc:
        base.append([a[0] if len(a)==1 else lattice_join(domain,*a) for a in it.product(range(n),repeat=len(parents))])
    swap=involution(domain); identity=list(range(n))
    gauges=[[identity[:] for _ in range(m)] for _ in range(len(inc)+1)]
    # One internal coordinate change, compensated at every consumer.
    if variant=='gauge':
        for p in range(m):
            if p&1:gauges[1][p]=swap[:]
    nodes=[]
    for i,parents in enumerate(inc):
        tabs=[]
        for p in range(m):
            tab=[]
            for xs in it.product(range(n),repeat=len(parents)):
                transformed=[gauges[w][p][x] for w,x in zip(parents,xs)]
                k=0
                for x in transformed:k=k*n+x
                y=gauges[i+1][p][base[i][k]]
                if variant=='visible' and i==len(inc)-1 and p&1:y=swap[y]
                if variant=='erased' and i==0 and p&1:y=n-1
                if variant=='erased' and i==len(inc)-1:y=n-1
                tab.append(y)
            tabs.append(tab)
        nodes.append({'inputs':parents,'domain':0,'tables':tabs})
    transports=[[identity[:] for _ in cat['arrows']] for _ in range(len(nodes)+1)]
    if domain['name']=='boolean-2':probes=[[int(x&1!=0) for x in range(n)]]
    elif domain['name']=='boolean-3':probes=[[(x&mask).bit_count() for x in range(n)] for mask in [3,5]]
    elif domain['name']=='anchored-boxes':probes=[[int(x//3>=1) for x in range(n)]]
    else:
        d=(n.bit_length()-1)
        masks=[sum(1<<j for j in range(d) if j>>b&1) for b in range((d-1).bit_length())]
        probes=[[(x&mask).bit_count() for x in range(n)] for mask in masks]
    return {'case':f"{domain['name']}-{topology}-{variant}"+('' if bits==2 and length==6 else f'-{bits}-{length}'),
            'category':cat,'domains':[domain], 'inputs':[0], 'nodes':nodes,'outputs':[len(nodes)],
            'transports':transports, 'probes':[{'wire':w,'tables':probes} for w in range(1,len(nodes))]}


def correlated() -> dict:
    cat=category(1); n=2
    return {'case':'correlated-inputs','category':cat,'domains':[boolean(1)],'inputs':[0],
            'nodes':[{'inputs':[0,0],'domain':0,'tables':[[0,0,0,1],[0,0,1,1]]}],
            'outputs':[1], 'transports':[[[0,1] for _ in cat['arrows']] for _ in range(2)],
            'probes':[{'wire':1,'tables':[[0,1]]}]}


def renamed() -> dict:
    c=simple(boolean(2),'short','natural',bits=2)
    c['case']='nonidentity-transport'
    s=involution(c['domains'][0]); identity=list(range(4))
    c['transports']=[[s[:] if (a^b)&1 else identity[:] for a,b in c['category']['arrows']] for _ in c['transports']]
    # Scalar probes in this schema have identity transport; omit non-natural ones.
    c['probes']=[]
    return c


def closure_case(domain:dict,variant:str,observation:str)->dict:
    """Sound nested closure stages: the second stage is constant top."""
    n=len(domain['labels']);rel=domain['leq'];cat=category(2)
    a=0; b=1 if domain['name']=='anchored-boxes' else 2
    large=[b if rel[x][b] else n-1 for x in range(n)]
    small=[a if rel[x][a] else b if rel[x][b] else n-1 for x in range(n)]
    if domain['name']=='anchored-boxes':
        rank=[x//3+x%3 for x in range(n)]
        flat=[int(x//3>=1) for x in range(n)]
    else:
        rank=[x.bit_count() for x in range(n)]
        flat=[int(x&1!=0) for x in range(n)]
    return {'case':f"closure-{domain['name']}-{variant}-{observation}",
        'category':cat,'domains':[domain],'inputs':[0],
        'nodes':[{'inputs':[0],'domain':0,'tables':[large[:] if variant=='mutated' and p&1 else small[:] for p in range(4)]},
                 {'inputs':[1],'domain':0,'tables':[[n-1]*n for _ in range(4)]}],
        'outputs':[2], 'transports':[[list(range(n)) for _ in cat['arrows']] for _ in range(3)],
        'probes':[{'wire':1,'tables':[rank if observation=='rank' else flat]}]}



def closure_forest_case(domain:dict,variant:str)->dict:
    """A two-branch nested closure forest with a masked root mutation."""
    n=len(domain['labels']);rel=domain['leq'];cat=category(2)
    a=0; b=1 if domain['name']=='anchored-boxes' else 2
    large=[b if rel[x][b] else n-1 for x in range(n)]
    small=[a if rel[x][a] else b if rel[x][b] else n-1 for x in range(n)]
    top=[n-1]*n
    if domain['name']=='anchored-boxes':rank=[x//3+x%3 for x in range(n)]
    else:rank=[x.bit_count() for x in range(n)]
    root=[large[:] if variant=='mutated' and p&1 else small[:] for p in range(4)]
    return {'case':f"closure-forest-{domain['name']}-{variant}",
        'category':cat,'domains':[domain],'inputs':[0],
        'nodes':[{'inputs':[0],'domain':0,'tables':root},
                 {'inputs':[1],'domain':0,'tables':[top[:] for _ in range(4)]},
                 {'inputs':[1],'domain':0,'tables':[large[:] for _ in range(4)]}],
        'outputs':[2,3],
        'transports':[[list(range(n)) for _ in cat['arrows']] for _ in range(4)],
        'probes':[{'wire':1,'tables':[rank]}]}

def non_nested()->dict:
    c=closure_case(boolean(2),'natural','rank');c['case']='non-nested-closure-control'
    e=[x|1 for x in range(4)]
    c['nodes'][0]['tables']=[e[:] for _ in range(4)]
    c['nodes'][1]['tables']=[e[:] if p&1 else list(range(4)) for p in range(4)]
    return c


def nonbijective(variant:str)->dict:
    """Rank-natural noninvertible transport and a source-idempotence control."""
    cat=category(1);e=[0,1,1,3];identity=list(range(4));top=[3]*4
    if variant=='natural':source=identity;target=[0,1,3,3]
    elif variant=='visible':source=[0,3,2,3];target=identity
    else:source=[1,3,3,3];target=[2,3,2,3]
    return {'case':'nonbijective-'+variant,'category':cat,'domains':[boolean(2)],'inputs':[0],
        'nodes':[{'inputs':[0],'domain':0,'tables':[source,target]},
                 {'inputs':[1],'domain':0,'tables':[top,top]}],
        'outputs':[2], 'transports':[[identity[:],e[:],identity[:]] for _ in range(3)],
        'probes':[{'wire':1,'tables':[[0,1,1,2]]}]}


def producer_certificate(c:dict) -> dict:
    """Direct table expression evaluation; no category/proof assumptions trusted."""
    sizes=[len(d['labels']) for d in c['domains']]
    wd=c['inputs']+[v['domain'] for v in c['nodes']]
    def at(node,p,xs):
        idx=0
        for w,x in zip(node['inputs'],xs):idx=idx*sizes[wd[w]]+x
        return node['tables'][p][idx]
    local=[]; gl=[]
    for ai,(p,q) in enumerate(c['category']['arrows']):
        for vi,v in enumerate(c['nodes']):
            for xs in it.product(*(range(sizes[wd[w]]) for w in v['inputs'])):
                a=c['transports'][len(c['inputs'])+vi][ai][at(v,p,xs)]
                b=at(v,q,[c['transports'][w][ai][x] for w,x in zip(v['inputs'],xs)])
                if a!=b:local.append([ai,vi,list(xs),a,b])
        for xs in it.product(*(range(sizes[d]) for d in c['inputs'])):
            runs=[]
            for obj,initial in [(p,list(xs)),(q,[c['transports'][w][ai][x] for w,x in enumerate(xs)])]:
                state=initial[:]
                for v in c['nodes']:state.append(at(v,obj,[state[w] for w in v['inputs']]))
                runs.append(state)
            left=[c['transports'][w][ai][runs[0][w]] for w in c['outputs']]
            right=[runs[1][w] for w in c['outputs']]
            if left!=right:gl.append([ai,list(xs),left,right])
    gen=set(c['category']['generators'])
    first=next((w for w in local if w[0] in gen),None)
    return {'case':c['case'],'locally_natural':not local,'globally_natural':not gl,
            'local_failures':len(local),'global_failures':len(gl),'least_generator_witness':first}


def generate(destination:Path) -> list[dict]:
    destination.mkdir(parents=True,exist_ok=True)
    cases=[simple(d,t,v) for d in [boolean(2),boolean(3),boxes()] for t in ['short','chain','diamond'] for v in ['natural','gauge','erased','visible']]
    cases += [correlated(),renamed()]
    cases += [closure_case(d,v,o) for d in [boolean(2),boolean(3),boxes()] for v in ['natural','mutated'] for o in ['rank','flat']]
    cases += [closure_forest_case(d,v) for d in [boolean(2),boolean(3),boxes()] for v in ['natural','mutated']]
    cases += [non_nested()]
    cases += [nonbijective(v) for v in ['natural','visible','nonidempotent']]
    cases += [simple(boolean(d),'chain','gauge',bits=b,length=n) for d,b,n in [(2,1,2),(3,2,10),(5,3,20)]]
    for c in cases:
        (destination/(c['case']+'.json')).write_text(json.dumps(c,sort_keys=True,separators=(',',':'))+'\n')
    certificates=[producer_certificate(c) for c in cases]
    (destination/'certificates.json').write_text(json.dumps(certificates,indent=2,sort_keys=True)+'\n')
    return cases

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('destination',type=Path)
    print(json.dumps({'cases':len(generate(p.parse_args().destination))}))
