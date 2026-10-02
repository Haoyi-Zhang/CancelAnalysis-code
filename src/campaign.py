"""Full case/certificate checks plus deterministic generator-sampling baselines."""
from __future__ import annotations
import argparse
import csv
import itertools as it
import json
import random
import time
from pathlib import Path
import checker

def samples(c:dict)->dict:
    dims=[len(d['labels']) for d in c['domains']]
    wires=c['inputs']+[v['domain'] for v in c['nodes']]
    population=[]
    for a in sorted(c['category']['generators']):
        for v,node in enumerate(c['nodes']):
            for xs in it.product(*(range(dims[wires[w]]) for w in node['inputs'])):population.append((a,v,xs))
    def defect(s):
        a,vi,xs=s;node=c['nodes'][vi];p,q=c['category']['arrows'][a]
        def call(obj,ys):
            k=0
            for w,y in zip(node['inputs'],ys):k=k*dims[wires[w]]+y
            return node['tables'][obj][k]
        left=c['transports'][len(c['inputs'])+vi][a][call(p,xs)]
        right=call(q,tuple(c['transports'][w][a][x] for w,x in zip(node['inputs'],xs)))
        return left!=right
    failures=sum(defect(s) for s in population)
    detected=[]
    for seed in range(32):
        trial=random.Random(seed).sample(population,min(8,len(population)))
        detected.append(any(defect(s) for s in trial))
    return {'generator_population':len(population),'generator_defects':failures,
            'sample_size':min(8,len(population)),'seeds':list(range(32)),
            'detected_by_seed':detected,'detected_seed_count':sum(detected)}

def run(case_dir:Path,destination:Path)->dict:
    destination.mkdir(parents=True,exist_ok=True)
    certs=json.loads((case_dir/'certificates.json').read_text());records=[];metrics=[]
    expected={c['case'] for c in certs}
    if len(expected)!=len(certs):raise ValueError('duplicate case certificate')
    actual={p.stem for p in case_dir.glob('*.json') if p.name!='certificates.json'}
    if expected!=actual:raise ValueError('case set mismatch')
    for cert in sorted(certs,key=lambda x:x['case']):
        f=case_dir/(cert['case']+'.json');c=checker.load(f)
        t=time.perf_counter();cpu=time.process_time()
        r=checker.certificate(c,cert)
        metrics.append({'case':r['case'],'wall_seconds':time.perf_counter()-t,'cpu_seconds':time.process_time()-cpu,
                        'case_bytes':f.stat().st_size,'certificate_bytes':len(json.dumps(cert,sort_keys=True,separators=(',',':')).encode())})
        r['sampling']=samples(c)
        if r['locally_natural'] and not r['globally_natural']:raise AssertionError('composition contradiction')
        if r['nested_closure_forest'] and r['all_internal_probes_strict']:
            if r['locally_natural']!=(r['globally_natural'] and r['probe_failures']==0):raise AssertionError('closure reflection contradiction')
        if bool(r['sampling']['generator_defects'])==r['locally_natural']:raise AssertionError('generator inconsistency')
        records.append(r)
    (destination/'case_verification.json').write_text(json.dumps(records,sort_keys=True,indent=2)+'\n')
    keys=['case','objects','arrows','generators','nodes','max_domain','locally_natural','globally_natural',
          'local_failures','global_failures','local_diagrams','global_diagrams','generator_diagrams','probe_checks','probe_failures','total_diagrams','table_entries']
    with (destination/'case_summary.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,keys);writer.writeheader();writer.writerows({k:r[k] for k in keys} for r in records)
    (destination/'case_measurements.json').write_text(json.dumps(metrics,sort_keys=True,indent=2)+'\n')
    summary={'cases':len(records),'locally_natural':sum(r['locally_natural'] for r in records),
             'globally_natural':sum(r['globally_natural'] for r in records),
             'externally_masked_local_defects':sum(not r['locally_natural'] and r['globally_natural'] for r in records),
             'local_diagrams':sum(r['local_diagrams'] for r in records),
             'global_diagrams':sum(r['global_diagrams'] for r in records),
             'probe_diagrams':sum(r['probe_checks'] for r in records),
             'all_certificates_match':True}
    (destination/'campaign_summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('cases',type=Path);p.add_argument('destination',type=Path);a=p.parse_args()
    print(json.dumps(run(a.cases,a.destination),sort_keys=True))
