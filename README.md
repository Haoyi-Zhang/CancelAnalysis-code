# Cancellability Conditions

Finite evidence and self-contained proofs for **Observation-Relative Cancellability for Compositional Algebraic Analyses**.

The repository is a standalone companion to the manuscript. It contains no private data, network dependency, external solver, or hidden controller.

## Supported reproduction environment

The documented bounded runner requires:

- Linux (WSL is acceptable because it presents a Linux environment);
- Python 3.10 or newer; and
- only the Python standard library.

Native Windows is not supported by `reproduce.py`: the runner uses the POSIX `resource` module and `os.killpg` process-group termination. A platform/version preflight rejects an unsupported environment before any scientific job starts.

## Reproduce the evidence

From this directory, use a fresh output path:

```sh
python reproduce.py --output reproduction
```

The runner executes nine sequential bounded jobs with one child process at a time. It reconstructs all 63 graph cases, independently checks their certificates, rebuilds and verifies the closure and count-probe universes, runs the exact reversible and transported-square oracles, and executes 45 regression tests. It then compares 73 deterministic JSON/CSV evidence files directly with the bundled results. Timing measurements are recorded but excluded from equality checks.

Expected scientific summary:

| Quantity | Value |
|---|---:|
| Graph cases | 63 |
| Locally natural cases | 20 |
| Locally defective cases | 43 |
| Ordinarily globally natural cases | 54 |
| Local defects hidden at final outputs | 34 |
| Defects exposed by augmented observations | 37 |
| Generator-local equations checked | 15,548 |
| All-arrow local equations checked | 35,010 |
| Ordinary-global equations checked | 4,464 |
| Probe equations checked | 61,164 |
| Total graph equations | 100,638 |
| Regression tests | 45 |
| Directly compared deterministic files | 73 |

The largest graph case has 67,392 equations and 75,474 input bytes. Compact certificates range from 148 to 175 bytes. Every producer certificate is recomputed extensionally before acceptance.

The count-probe verifier separately reconstructs all 50 naturally labelled posets on one through four points, proves each minimum distinguishing number by exhaustive coloring search, rejects missing or duplicate universe records, and enumerates all ordered support tuples at each attempted size through the first feasible size. The current universe requires 1,294 support families. Regression tests reject the specific false `D=4` mutation for `upper_sets=[9,10,12,8]` and reject deleted or duplicated poset records.

## What the results establish

The mathematical argument distinguishes four interfaces.

- A general DAG has a sufficient converse when node outputs are jointly separated and every formal parent tuple is reached. Passive observation of executed merge inputs cannot determine an operator at unreachable tuples.
- Closure operators require exactly separation of strict comparable pairs. The transported theorem needs an extensive idempotent source, a monotone extensive target, and a monotone transport; a defect is observed at `x` or after one source application.
- Nested unary closure forests use absorption to collapse every root-to-node path, so the closure theorem reflects all local squares without prefix surjectivity. Branching is allowed; merge nodes are not. The localized witness also requires natural observation families and strict comparable-pair separation at generator targets.
- Reversible pipelines with identity transports require trivial observation stabilizers. The remaining compatible factorizations have an exact finite-group count.

For finite distributive lattices, the minimum number of permitted unweighted subset-count probes is `ceil(log2 D(P))`, where `D(P)` is the distinguishing number of the join-irreducible poset and `D(empty)=1`. Hence the one-element lattice needs zero probes. For an antichain the formula `D(P)=d` is stated only for `d>=1`. Rank identifies every closure in the selected universes while preserving all lattice automorphisms, demonstrating that closure and reversible interfaces are genuinely different.

The retained negative control `closure-boolean-2-mutated-flat.json` has source table `(0,3,2,3)`, target table `(2,3,2,3)`, observation `(0,1,0,1)`, and input `0`. Its local values differ (`0` versus `2`) while both observations are `0`; the second theorem input is again `0`. It is intentionally excluded by the strict comparable-pair premise.

## Evidence map

| Path | Role |
|---|---|
| `proofs/theory.md` | Complete proof note and model boundaries |
| `src/checker.py` | Structural validation and independent extensional certificate checking |
| `src/construct.py` | Deterministic graph-case producer, including six branching closure-forest cases |
| `src/campaign.py` | Corpus evaluation, controls, and sampling comparison |
| `src/closure_search.py`, `src/closure_checker.py` | Independent closure and observer enumeration paths |
| `src/transport_oracle.py` | Asymmetric transported-square universe and five operator/transport hypothesis controls |
| `src/reversible_oracle.py` | Exact reversible-factorization count |
| `src/probe_search.py`, `src/probe_checker.py` | Candidate production and independent universe, distinguishing-number, and count-probe verification |
| `tests/test_checker.py` | Positive, negative, mutation, parser, resource, and certificate tests |
| `cases/` | Canonical 63 graph instances plus `certificates.json` |
| `results/campaign_summary.json` | Corpus totals |
| `results/case_verification.json` | Per-case recomputed verdicts, witnesses, and controls |
| `results/closure_verification.json` | Exhaustive closure/observer universes |
| `results/transport_verification.json` | Transported theorem and assumption-removal evidence |
| `results/reversible_verification.json` | Reversible count evidence |
| `results/probe_verification.json` | Count-probe optimum, distinguishing-number, and canonical-poset evidence |
| `results/reproduction_measurements.json` | Actual supported-environment run, job measurements, and executed test count |
| `claim_evidence_ledger.csv` | Claim-to-proof/check/result mapping |
| `external_resources.csv` | Scholarly and official resource inventory |

## Resource and portability boundaries

The current clean non-resumed run used Linux kernel 6.18.44 and CPython 3.13.5. The nine jobs used 7.971551 aggregate child CPU seconds and a maximum single-job peak resident set of 98,280 KiB. These values cover the measured jobs only; they are not a retrospective total for proof development, editing, compilation, or packaging. Per-case timing is descriptive and never part of deterministic equality.

The runner rejects a nonempty output unless `--resume` is explicitly supplied. Final validation must not use resume. Scientific children are bounded by an external 120-second timeout and a three-gibibyte address-space limit. Inputs are additionally capped by dimensions and equation counts in the checker.

## Interpretation limits

The program category contains semantics-preserving insertions of labelled `skip` instructions. Extensive closures on three finite abstract domains are sound coarsenings of the identity transformer. Reversible mutations and nonidentity transports are algebraic controls, not production-analyzer or deployed-CFG claims. The repository does not establish performance, industrial representativeness, arbitrary recursive composition, infinite-domain results, or a bridge to a different categorical robustness semantics.

The producer and verifier are separately implemented but share a specification and development history. Passing commands show deterministic agreement for the declared finite model; they are not proof-assistant verification or independent external review.

## License and attribution

Repository code and proof text are covered by `LICENSE`. External scholarly works are cited rather than redistributed. The publisher class and bibliography style live only in the manuscript package, with their original notices retained.
