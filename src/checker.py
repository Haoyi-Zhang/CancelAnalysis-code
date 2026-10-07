"""Independent bounded extensional verifier for finite typed analyzer DAGs.

No import from the case producer or optimizer. Only standard-library dependencies.
All advertised results are re-evaluated; a producer's expected verdict is not an axiom.
"""
from __future__ import annotations
import argparse
import itertools
import json
import math
import time
from pathlib import Path
from typing import Any

MAX_BYTES=4*1024*1024
MAX_DIAGRAMS=100_000

class Invalid(ValueError):
    pass

class Budget:
    def __init__(self,seconds:float=110.0):self.end=time.monotonic()+seconds
    def check(self):
        if time.monotonic()>self.end:raise Invalid('TIME_LIMIT')

def require(condition:bool,code:str):
    if not condition:raise Invalid(code)

def integer(x:Any,low:int,high:int)->bool:
    return type(x) is int and low<=x<high

def unique_pairs(pairs:list[tuple[str,Any]])->dict:
    result={}
    for k,v in pairs:
        if k in result:raise Invalid('DUPLICATE_KEY')
        result[k]=v
    return result

def load(path:Path)->dict:
    with path.open('rb') as f:data=f.read(MAX_BYTES+1)
    require(len(data)<=MAX_BYTES,'BYTE_LIMIT')
    try:
        obj=json.loads(data,object_pairs_hook=unique_pairs,parse_constant=lambda _:(_ for _ in ()).throw(Invalid('NONFINITE_JSON')))
    except (UnicodeError,json.JSONDecodeError,RecursionError) as e:raise Invalid('JSON_SYNTAX') from e
    require(type(obj)is dict,'OBJECT_REQUIRED')
    return obj

def checked_order(d:dict,budget:Budget)->tuple:
    require(type(d)is dict and set(d)=={'name','labels','leq'},'DOMAIN_FIELDS')
    labels=d['labels'];rel=d['leq']
    require(type(d['name']) is str and 0<len(d['name'])<=100,'DOMAIN_NAME')
    require(type(labels)is list and all(type(x)is str and 0<len(x)<=100 for x in labels),'LABEL_TYPE')
    n=len(labels)
    require(1<=n<=32 and len(set(labels))==n,'DOMAIN_SIZE_OR_LABELS')
    require(type(rel)is list and len(rel)==n and all(type(row)is list and len(row)==n and all(type(z)is int and z in (0,1) for z in row) for row in rel),'ORDER_SHAPE')
    for a in range(n):
        require(rel[a][a]==1,'REFLEXIVITY')
        for b in range(n):
            require(a==b or not(rel[a][b] and rel[b][a]),'ANTISYMMETRY')
            for c in range(n):require(not(rel[a][b] and rel[b][c]) or rel[a][c],'TRANSITIVITY')
        budget.check()
    meet=[[0]*n for _ in range(n)];join=[[0]*n for _ in range(n)]
    for a in range(n):
        for b in range(n):
            lower=[x for x in range(n) if rel[x][a] and rel[x][b]]
            upper=[x for x in range(n) if rel[a][x] and rel[b][x]]
            lo=[x for x in lower if all(rel[y][x] for y in lower)]
            hi=[x for x in upper if all(rel[x][y] for y in upper)]
            require(len(lo)==len(hi)==1,'NOT_A_LATTICE')
            meet[a][b]=lo[0];join[a][b]=hi[0]
    for a,b,c in itertools.product(range(n),repeat=3):
        require(meet[a][join[b][c]]==join[meet[a][b]][meet[a][c]],'NONDISTRIBUTIVE')
    return n,rel,meet,join

def verified_category(cat:dict,budget:Budget)->tuple:
    require(type(cat)is dict,'CATEGORY_OBJECT')
    require(set(cat)=={'programs','arrows','identities','generators','composition'},'CATEGORY_FIELDS')
    programs=cat['programs'];arrows=cat['arrows'];ids=cat['identities'];gens=cat['generators'];comp=cat['composition']
    m=len(programs);h=len(arrows)
    require(1<=m<=16 and 1<=h<=64,'CATEGORY_LIMIT')
    for p in programs:
        require(type(p)is list and 2<=len(p)<=18 and p[0]=='entry' and p[-1]=='return' and all(type(x)is str and x.startswith('skip-') and x[5:].isdigit() for x in p[1:-1]),'PROGRAM_VOCABULARY')
        require(len(set(p))==len(p),'PROGRAM_DUPLICATION')
    require(all(type(a)is list and len(a)==2 and all(integer(x,0,m) for x in a) for a in arrows),'ARROW_TYPE')
    require(len(ids)==m and all(integer(x,0,h) and arrows[x]==[i,i] for i,x in enumerate(ids)),'IDENTITY_TYPE')
    require(type(gens)is list and len(gens)==len(set(gens)) and all(integer(x,0,h) and x not in ids for x in gens),'GENERATORS')
    require(len(comp)==h and all(type(row)is list and len(row)==h for row in comp),'COMPOSITION_SHAPE')
    for a in range(h):
        # All bundled program morphisms are skip insertion; deletion/renaming are not parsed.
        p,q=arrows[a]
        source=programs[p][1:-1];target=programs[q][1:-1]
        # Insertion preserves the order of existing labels, not merely membership.
        require([x for x in target if x in set(source)]==source,'NOT_SKIP_INSERTION')
        require(comp[ids[q]][a]==a and comp[a][ids[p]]==a,'UNIT_LAW')
        for b in range(h):
            c=comp[a][b]
            if arrows[b][1]!=arrows[a][0]:require(c is None,'ILL_TYPED_COMPOSITION')
            else:require(integer(c,0,h) and arrows[c]==[arrows[b][0],arrows[a][1]],'COMPOSITION_TYPE')
        budget.check()
    for a,b,c in itertools.product(range(h),repeat=3):
        if comp[a][b] is not None and comp[b][c] is not None:
            require(comp[comp[a][b]][c]==comp[a][comp[b][c]],'ASSOCIATIVITY')
    # Shortest generator words. Closure, not an assumption about a presentation.
    words={a:[] for a in ids};frontier=list(ids)
    while frontier:
        a=frontier.pop(0)
        for g in sorted(gens):
            c=comp[g][a]
            if c is not None and c not in words:
                words[c]=words[a]+[g];frontier.append(c)
        budget.check()
    require(len(words)==h,'GENERATORS_NOT_SURJECTIVE')
    return m,h,arrows,ids,gens,comp,words

def audit(c:dict,seconds:float=110.0)->dict:
    budget=Budget(seconds)
    require(type(c)is dict,'CASE_OBJECT')
    require(set(c)=={'case','category','domains','inputs','nodes','outputs','transports','probes'},'CASE_FIELDS')
    require(type(c['case'])is str and 0<len(c['case'])<=100,'CASE_NAME')
    require(type(c['domains'])is list and 1<=len(c['domains'])<=8,'DOMAIN_COUNT')
    ds=[checked_order(d,budget) for d in c['domains']]
    m,h,arrows,ids,gens,comp,words=verified_category(c['category'],budget)
    inputs=c['inputs'];nodes=c['nodes'];outputs=c['outputs'];trans=c['transports']
    require(type(inputs)is list and 1<=len(inputs)<=3 and all(integer(d,0,len(ds)) for d in inputs),'INPUT_TYPE')
    require(type(nodes)is list and 1<=len(nodes)<=20,'NODE_COUNT')
    wd=inputs[:];sizes=[ds[d][0] for d in wd];entries=0
    tuples=[]
    for ni,v in enumerate(nodes):
        require(type(v)is dict and set(v)=={'inputs','domain','tables'},'NODE_FIELDS')
        require(type(v['inputs'])is list and 1<=len(v['inputs'])<=3 and all(integer(w,0,len(wd)) for w in v['inputs']),'CYCLIC_OR_UNTYPED_NODE')
        require(integer(v['domain'],0,len(ds)),'NODE_DOMAIN')
        n=ds[v['domain']][0];arity_sizes=[sizes[w] for w in v['inputs']]
        volume=math.prod(arity_sizes);entries+=volume*m
        require(entries<=100_000,'TABLE_ENTRY_LIMIT')
        tab=v['tables']
        require(type(tab)is list and len(tab)==m and all(type(row)is list and len(row)==volume and all(integer(x,0,n) for x in row) for row in tab),'NODE_TABLE')
        points=list(itertools.product(*(range(s) for s in arity_sizes)));tuples.append(points)
        index={x:i for i,x in enumerate(points)}
        # Checking every coordinate increase is complete for the product order.
        outrel=ds[v['domain']][1]
        for p in range(m):
            for xi,xs in enumerate(points):
                for k,w in enumerate(v['inputs']):
                    rel=ds[wd[w]][1]
                    for y in range(sizes[w]):
                        if rel[xs[k]][y]:
                            ys=xs[:k]+(y,)+xs[k+1:]
                            require(outrel[tab[p][xi]][tab[p][index[ys]]],'NONMONOTONE_OPERATOR')
                if xi%128==0:budget.check()
        wd.append(v['domain']);sizes.append(n)
    wcount=len(wd)
    require(type(outputs)is list and 1<=len(outputs)<=wcount and len(outputs)==len(set(outputs)) and all(integer(w,0,wcount) for w in outputs),'OUTPUT_TYPE')
    require(type(trans)is list and len(trans)==wcount,'TRANSPORT_WIRES')
    for w,ts in enumerate(trans):
        n=sizes[w];rel=ds[wd[w]][1]
        require(type(ts)is list and len(ts)==h and all(type(row)is list and len(row)==n and all(integer(x,0,n) for x in row) for row in ts),'TRANSPORT_SHAPE')
        for a in ids:require(ts[a]==list(range(n)),'FUNCTOR_IDENTITY')
        for a in range(h):
            require(all(not rel[x][y] or rel[ts[a][x]][ts[a][y]] for x in range(n) for y in range(n)),'NONMONOTONE_TRANSPORT')
            for b in range(h):
                if comp[a][b]is not None:
                    require(ts[comp[a][b]]==[ts[a][ts[b][x]] for x in range(n)],'FUNCTOR_COMPOSITION')
        budget.check()
    points=list(itertools.product(*(range(sizes[w]) for w in range(len(inputs)))))
    require(type(c['probes'])is list and len(c['probes'])<=20,'PROBE_COUNT')
    for probe in c['probes']:
        require(type(probe)is dict and set(probe)=={'wire','tables'} and integer(probe['wire'],0,wcount),'PROBE_FIELDS')
        require(type(probe['tables'])is list and len(probe['tables'])<=6,'PROBE_TABLE_COUNT')
    scalar_count=sum(len(probe['tables']) for probe in c['probes'])
    diagrams=h*(sum(len(t) for t in tuples)+(scalar_count+1)*len(points))
    require(diagrams<=MAX_DIAGRAMS,'DIAGRAM_LIMIT')
    def lookup(v,p,xs):
        idx=0
        for w,x in zip(v['inputs'],xs):idx=idx*sizes[w]+x
        return v['tables'][p][idx]
    runs={};coverage=[set() for _ in nodes]
    for p in range(m):
        for xs in points:
            vals=list(xs)
            for vi,v in enumerate(nodes):
                args=tuple(vals[w] for w in v['inputs'])
                if p==0:coverage[vi].add(args)
                vals.append(lookup(v,p,args))
            runs[p,xs]=vals
        budget.check()
    local_failures=0;global_failures=0;first=None
    for ai,(p,q) in enumerate(arrows):
        for vi,v in enumerate(nodes):
            out=len(inputs)+vi
            for xs in tuples[vi]:
                left=trans[out][ai][lookup(v,p,xs)]
                right=lookup(v,q,tuple(trans[w][ai][x] for w,x in zip(v['inputs'],xs)))
                if left!=right:
                    local_failures+=1
                    if first is None and ai in gens:
                        first=[ai,vi,list(xs),left,right]
        for xs in points:
            tx=tuple(trans[w][ai][x] for w,x in enumerate(xs))
            r,s=runs[p,xs],runs[q,tx]
            left=[trans[w][ai][r[w]] for w in outputs];right=[s[w] for w in outputs]
            if left!=right:global_failures+=1
        budget.check()
    # Scalar observation tables use a constant chain codomain and identity transport.
    probe_failures=0;probe_checks=0
    require(type(c['probes'])is list and len(c['probes'])<=20,'PROBE_COUNT')
    for probe in c['probes']:
        require(set(probe)=={'wire','tables'} and integer(probe['wire'],0,wcount),'PROBE_FIELDS')
        w=probe['wire'];n=sizes[w];rel=ds[wd[w]][1]
        require(type(probe['tables'])is list and len(probe['tables'])<=6,'PROBE_TABLE_COUNT')
        for table in probe['tables']:
            require(type(table)is list and len(table)==n and all(integer(x,0,33) for x in table),'PROBE_TABLE')
            require(all(not rel[x][y] or table[x]<=table[y] for x in range(n) for y in range(n)),'NONMONOTONE_PROBE')
            require(all(table[trans[w][a][x]]==table[x] for a in range(h) for x in range(n)),'NONNATURAL_PROBE')
            for a,(p,q) in enumerate(arrows):
                for xs in points:
                    tx=tuple(trans[i][a][x] for i,x in enumerate(xs))
                    probe_checks+=1
                    if table[runs[p,xs][w]]!=table[runs[q,tx][w]]:probe_failures+=1
        budget.check()
    # Identity squares cannot fail; generator completeness supplies a one-letter witness.
    require(not local_failures or first is not None,'GENERATOR_COMPLETENESS_INTERNAL_ERROR')
    special=specialization(c,ds,wd)
    return {'case':c['case'],**special,'locally_natural':not local_failures,'globally_natural':not global_failures,
            'local_failures':local_failures,'global_failures':global_failures,'least_generator_witness':first,
            'objects':m,'arrows':h,'generators':len(gens),'nodes':len(nodes),'max_domain':max(sizes),
            'local_diagrams':h*sum(len(t) for t in tuples),'global_diagrams':h*len(points),
            'generator_diagrams':len(gens)*sum(len(t) for t in tuples),'table_entries':entries,
            'probe_checks':probe_checks,'probe_failures':probe_failures,'total_diagrams':diagrams,
            'input_coverage_at_object_zero':[[len(s),len(t)] for s,t in zip(coverage,tuples)]}

def specialization(c:dict,ds:list,wd:list)->dict:
    """Validate subclass hypotheses from tables, never from a case label."""
    nodes=c['nodes'];m=len(c['category']['programs'])
    same_domain=(len(c['inputs'])==1 and len(set(wd))==1)
    unary_forest=(same_domain and all(len(v['inputs'])==1 for v in nodes))
    chain=(unary_forest and all(v['inputs']==[i] for i,v in enumerate(nodes))
           and c['outputs']==[len(nodes)])
    result={'unary_pipeline':chain,'unary_forest':unary_forest,
            'nested_closure_pipeline':False,'nested_closure_forest':False,
            'all_gates_order_isomorphisms':False,'all_gates_closures':False,
            'all_internal_probes_strict':False,'constant_transport':False}
    if not unary_forest:return result
    n,rel,_,_=ds[wd[0]]
    # A monotone finite bijection of a finite poset to itself has monotone inverse.
    iso=all(len(set(t))==n for v in nodes for t in v['tables'])
    closures=all(all(rel[x][t[x]] and t[t[x]]==t[x] for x in range(n))
                 for v in nodes for t in v['tables'])
    shared=all(w==c['transports'][0] for w in c['transports'])
    # Every non-input parent is the output wire 1+j of an earlier node j.
    nested=closures
    for i,v in enumerate(nodes):
        parent=v['inputs'][0]
        if parent==0:continue
        parent_node=parent-1
        if not (0<=parent_node<i):nested=False;break
        if not all(rel[nodes[parent_node]['tables'][obj][x]][v['tables'][obj][x]]
                   for obj in range(m) for x in range(n)):
            nested=False;break
    used={v['inputs'][0] for v in nodes}
    sinks={1+i for i in range(len(nodes)) if 1+i not in used}
    outputs_cover_sinks=sinks.issubset(set(c['outputs']))
    strict=True
    for wire in range(1,len(nodes)+1):
        if wire in c['outputs']:continue
        tabs=[t for probe in c['probes'] if probe['wire']==wire for t in probe['tables']]
        if any(rel[x][y] and x!=y and not any(t[x]!=t[y] for t in tabs)
               for x in range(n) for y in range(n)):strict=False
    forest=bool(nested and shared and outputs_cover_sinks)
    result.update(nested_closure_pipeline=bool(chain and nested and shared),
                  nested_closure_forest=forest,
                  all_gates_order_isomorphisms=iso,all_gates_closures=closures,
                  all_internal_probes_strict=strict,
                  constant_transport=all(t==list(range(n)) for w in c['transports'] for t in w))
    return result


def certificate(c:dict,claimed:dict)->dict:
    actual=audit(c)
    keys=['case','locally_natural','globally_natural','local_failures','global_failures','least_generator_witness']
    require(type(claimed)is dict and set(claimed)==set(keys),'CERTIFICATE_FIELDS')
    for k in keys:require(json.dumps(claimed[k],sort_keys=True)==json.dumps(actual[k],sort_keys=True),'CERTIFICATE_MISMATCH_'+k)
    return actual

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('case',type=Path);p.add_argument('--certificate',type=Path)
    a=p.parse_args()
    try:
        c=load(a.case)
        r=certificate(c,load(a.certificate)) if a.certificate else audit(c)
        print(json.dumps(r,sort_keys=True))
    except OSError:
        print(json.dumps({'accepted':False,'error':'FILE_IO'}));raise SystemExit(2)
    except (Invalid,KeyError,IndexError,TypeError,OverflowError,RecursionError) as e:
        print(json.dumps({'accepted':False,'error':str(e)}));raise SystemExit(2)
if __name__=='__main__':main()
