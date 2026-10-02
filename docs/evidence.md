# Interpretation of the finite evidence

## Exact checks and manuscript locations

The article contains all acceptance-critical proofs. Standalone numbering is local to `proofs/theory.md`; the last column gives the actual article locations.

| Statement | Proof note | Article |
|---|---|---|
| Generator extension and composition | Proposition 1 | Proposition 2.1; Section 2 |
| Known-context cancellation and the joint-coverage DAG converse | Propositions 2–3 | Proposition 2.2; Section 2 |
| Reversible masking and the soundness distinction | Propositions 4–5 | Section 2; Figure 1 |
| Asymmetric transported cancellation | Lemma 8 | Theorem 3.1; Table 1 |
| Closure identification and scalar capacity | Theorem 6; Corollary 7 | Theorem 3.2; Corollary 3.3; Figure 2 |
| Closure-forest absorption, reflection, and localized witness | Lemma 9; Theorem 10 | Lemma 4.1; Theorem 4.2; Corollary 4.3 |
| Reversible reflection and factorization count | Theorem 11 | Theorem 5.1 |
| Counter stabilizers and the restricted probe optimum | Lemma 12; Theorem 13 | Lemma 6.1; Theorem 6.2 |
| Canonical failed square and finite checking contract | Propositions 14–15 | Propositions 7.2 and 7.1 |

Theorem 10 in the proof note is the closure-forest theorem. It is not used as a pointer to the reversible count; the matching reversible proof is now Theorem 11 and corresponds to article Theorem 5.1.

## Closure and transport universes

`closure_verification.json` records all 7, 61, and 115 closures on the four-, eight-, and nine-state domains. The independent checker enumerates extensive maps rather than reusing the producer's meet-closed fixed-point subsets. It tests 20, 887, and 4,116 monotone scalar observations into the selected height-sized chains. Exactly one observation in each declared universe separates strict comparable pairs and identifies every closure: the height rank. This uniqueness is only for those domains and codomains.

Nested ordered closure pairs number 22, 733, and 1,992. Equal-rank defects detected after one source application number 2, 588, and 2,138. Article Table 3 reports these quantities. They are ordered finite function/input checks, not independent empirical subjects.

`transport_verification.json` enumerates 36 monotone maps on the four-element Boolean lattice, 12 extensive idempotent sources, and 9 monotone extensive targets: 3,888 triples and 15,552 point squares. There are 6,768 underlying defects, including 240 equal-rank first-input defects exposed by the second input. All 779 equal observed profiles have equal underlying maps. The five controls in article Table 1 each remove one source/transport/target hypothesis while retaining the others.

The flat closure control is deliberately retained. In `closure-boolean-2-mutated-flat.json`, the relevant source table is `(0,3,2,3)`, the target table is `(2,3,2,3)`, the observation is `(0,1,0,1)`, and input `0` gives unequal local values `0` and `2` with equal observation `0`; the second theorem input is again `0`. The observation is natural but does not separate the comparable pair `0<2`, so the case is outside Theorem 4.2 and Corollary 4.3 rather than a counterexample to them.

## Reversible and count-probe universes

`reversible_verification.json` enumerates 256 three-gate factorizations of identity over four program objects on the four-element Boolean lattice. Four are locally natural. The numbers passing observation are 256 with no probes, 256 with rank at both cuts, 32 with a rigid probe only at the first cut, and 4 with rigid probes at both cuts. These are exact counts over the declared finite group, not frequencies in production analyzers.

`probe_verification.json` covers the complete canonical universe of 50 naturally labelled posets on one through four points, with size counts `1, 2, 7, 40`. The verifier independently reconstructs that universe, rejects missing or duplicate records, recomputes each automorphism group, and exhaustively proves the minimum distinguishing number rather than trusting the producer's `distinguishing_number` field. It then evaluates integer count probes on every ideal and, at each attempted `k` in `0,1,2`, enumerates every ordered support tuple up to and including the first feasible size. Across the current universe this is 1,294 support families, not 11,480 families at all three sizes for every poset.

Regression tests retain the concrete mutation with `upper_sets=[9,10,12,8]`: its independently recomputed distinguishing number is 3. Changing the candidate to `D=4` and coloring `[0,1,2,3]` while retaining minimum probe count 2 and supports `[2,4]` is rejected. Deleting a poset record or replacing one by a duplicate is also rejected. Arbitrary encodings, weighted counts, dynamic probes, and bit-level instrumentation cost remain outside Theorem 6.2.

## Graph corpus and comparison methods

The corpus contains 63 graph cases: 36 domain/shape/variant cases, one correlated-input control, one nonidentity-transport control, 12 linear nested-closure cases, 6 branching closure-forest cases, one nonnested control, 3 bounded scaling cases, and 3 nonbijective-transport controls. All cases and certificates are bundled.

There are 43 locally defective cases. Ordinary final-output checking detects 9 and correctly accepts the other 34 for its own property; those 34 are the final-output-hidden defects. The supplied augmented observations expose 37 of the 43. The six retained misses are three flat-observer closure cases, the correlated-input case, the nonnested closure case, and the source-nonidempotence transported case, each outside a premise of the applicable converse.

All-arrow local enumeration checks 35,010 local equations. Generator-local enumeration checks 15,548 equations and exposes all 43 defects. This is the logical reduction supplied by generator completeness, not a new performance algorithm.

Sampling eight distinct generator/node/input triples for each seed 0–31 detects 753 of 1,376 defective-case/seed pairs. Per-case detections range from 4 to 32 seeds. Sampling cannot certify absence, and no equal-work speedup, significance test, population generalization, or confidence interval is claimed.

Article Table 4 uses the scaling cases ending in `1-2`, `2-10`, and `3-20`. Their `(objects, arrows, nodes, maximum states)` are `(2,3,2,4)`, `(4,9,10,8)`, and `(8,27,20,32)`, with combined equation counts 48, 2,088, and 67,392. Compact certificate JSON records are 148–175 bytes; the largest input is 75,474 bytes. Small certificates do not make exhaustive verification constant-time.

At the merge boundary, `correlated-inputs.json` feeds the same Boolean value to both arguments. Conjunction and first projection agree on the reachable diagonal `(0,0),(1,1)` but differ at `(1,0)`. Full visibility of the two executed parent values and the output therefore cannot replace joint formal-tuple coverage or an independently proved operator law determining unreachable entries.

## Measurement scope and direct comparison

The current non-resumed run in `results/reproduction_measurements.json` was executed on Linux kernel 6.18.44 with CPython 3.13.5. It ran nine bounded jobs and 45 regression tests in a new output directory. The jobs used 7.971551 aggregate child CPU seconds; the maximum single-job reported peak resident set was 98,280 KiB. These measurements cover only those jobs and are not a retrospective total for proof development, editing, compilation, or packaging.

The runner directly compares 73 deterministic scientific files: 64 case/certificate JSON files and 9 deterministic result JSON/CSV files. Timing records are excluded from equality. Raw JSON/CSV equality is used rather than a generated checksum manifest.

## Scientific scope

The executable equalities are finite checks, not machine-checked general proofs. The producer and verifier are separately implemented but share a mathematical specification and development history. The independent probe verifier now closes the stated four-point universe and distinguishing-number fields, but it does not extend the theorem beyond the declared syntax or finite audit budget.

The two TikZ figures remain the original formal diagrams. No redraw is needed for these textual and verification corrections.
