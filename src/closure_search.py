"""Produce complete closure families via meet-closed fixed-point sets."""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
from construct import boolean, boxes


def family(domain:dict)->dict:
    leq=domain['leq'];n=len(leq)
    meet=[[next(z for z in range(n) if leq[z][x] and leq[z][y]
           and all(not(leq[t][x] and leq[t][y]) or leq[t][z] for t in range(n)))
           for y in range(n)] for x in range(n)]
    top=next(x for x in range(n) if all(leq[y][x] for y in range(n)))
    tables=[]
    for mask in range(1<<n):
        if not(mask>>top&1):continue
        fixed=[x for x in range(n) if mask>>x&1]
        if not all(mask>>meet[x][y]&1 for x in fixed for y in fixed):continue
        table=[]
        for x in range(n):
            y=top
            for z in fixed:
                if leq[x][z]:y=meet[y][z]
            table.append(y)
        tables.append(table)
    # The bundled domain indexing is a linear extension; verified separately.
    rank=[]
    for x in range(n):rank.append(max([rank[y]+1 for y in range(x) if leq[y][x]]+[0]))
    return {'domain':domain,'closures':sorted(tables),'rank':rank,
            'fixed_subsets_examined':1<<n}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args()
    data=[family(d) for d in [boolean(2),boolean(3),boxes()]]
    a.output.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'closure_counts':[len(d['closures']) for d in data]}))
if __name__=='__main__':main()
