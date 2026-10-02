"""Producer: distinguishing colorings of all naturally labelled posets up to four points."""
from __future__ import annotations
import itertools as it
import json
from pathlib import Path

def posets(n):
    pairs=list(it.combinations(range(n),2));seen=set()
    for code in range(1<<len(pairs)):
        rows=[1<<i for i in range(n)]
        for k,(i,j) in enumerate(pairs):
            if code>>k&1:rows[i]|=1<<j
        for k in range(n):
            for i in range(n):
                if rows[i]>>k&1:rows[i]|=rows[k]
        key=tuple(rows)
        if key not in seen:
            seen.add(key);yield key

def produce():
    records=[]
    for n in range(1,5):
        for rows in posets(n):
            auto=[p for p in it.permutations(range(n)) if all(((rows[i]>>j)&1)==((rows[p[i]]>>p[j])&1) for i in range(n) for j in range(n))]
            nonid=[p for p in auto if p!=tuple(range(n))]
            count=0
            for k in range(1,n+1):
                good=None
                for coloring in it.product(range(k),repeat=n):
                    count+=1
                    if all(any(coloring[i]!=coloring[p[i]] for i in range(n)) for p in nonid):
                        good=coloring;break
                if good is not None:break
            bitcount=(k-1).bit_length()
            supports=[sum(1<<i for i in range(n) if good[i]>>b&1) for b in range(bitcount)]
            records.append({'points':n,'upper_sets':list(rows),'automorphism_count':len(auto),
                            'distinguishing_number':k,'coloring':list(good),
                            'minimum_count_probes':bitcount,'supports':supports,
                            'colorings_examined':count})
    return records

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args()
    data=produce();a.output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'posets':len(data)}))
