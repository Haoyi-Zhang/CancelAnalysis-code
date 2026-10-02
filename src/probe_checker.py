"""Independent exhaustive count-probe verifier for naturally labelled posets.

The producer supplies candidate posets, distinguishing colorings, and support
families.  This verifier independently:

* reconstructs the complete canonical universe of naturally labelled posets on
  one through four points and rejects missing or duplicate records;
* recomputes automorphisms and the *minimum* distinguishing number by exhaustive
  coloring search; and
* evaluates count probes on every ideal, enumerating all ordered support tuples
  at each tried size until the first feasible size.

The probe decision therefore does not rely on the producer's coloring criterion.
"""
from __future__ import annotations

import itertools
import json
import time
from collections import Counter
from pathlib import Path
from typing import Iterable


class Invalid(ValueError):
    """Malformed or scientifically inconsistent probe-candidate evidence."""


def need(condition: bool, code: str) -> None:
    if not condition:
        raise Invalid(code)


def is_int(value: object) -> bool:
    return type(value) is int


def canonical_naturally_labelled_posets(n: int) -> set[tuple[int, ...]]:
    """Enumerate all transitive forward relations on labels 0 < ... < n-1.

    This implementation is deliberately different from ``probe_search.py``:
    it retains only already-transitive subsets rather than closing arbitrary
    subsets transitively and deduplicating the closures.
    """
    need(is_int(n) and 1 <= n <= 4, "POINT_COUNT")
    pairs = list(itertools.combinations(range(n), 2))
    result: set[tuple[int, ...]] = set()
    for mask in range(1 << len(pairs)):
        rows = [1 << i for i in range(n)]
        for bit, (i, j) in enumerate(pairs):
            if (mask >> bit) & 1:
                rows[i] |= 1 << j
        relation = {(i, j) for i in range(n) for j in range(n) if (rows[i] >> j) & 1}
        transitive = all(
            (a, d) in relation
            for a, b in relation
            for c, d in relation
            if b == c
        )
        if transitive:
            result.add(tuple(rows))
    return result


def validate_record_shape(record: object) -> tuple[int, list[int]]:
    need(type(record) is dict, "RECORD_TYPE")
    expected = {
        "points",
        "upper_sets",
        "automorphism_count",
        "distinguishing_number",
        "coloring",
        "minimum_count_probes",
        "supports",
        "colorings_examined",
    }
    need(set(record) == expected, "RECORD_FIELDS")
    n = record["points"]
    need(is_int(n) and 1 <= n <= 4, "POINT_COUNT")
    rows = record["upper_sets"]
    need(type(rows) is list and len(rows) == n, "UPPER_SET_SHAPE")
    need(all(is_int(row) and 0 <= row < (1 << n) for row in rows), "UPPER_SET_RANGE")
    need(is_int(record["automorphism_count"]) and record["automorphism_count"] >= 1, "AUTOMORPHISM_COUNT_TYPE")
    need(is_int(record["distinguishing_number"]) and 1 <= record["distinguishing_number"] <= n, "DISTINGUISHING_NUMBER_TYPE")
    need(type(record["coloring"]) is list and len(record["coloring"]) == n, "COLORING_SHAPE")
    need(all(is_int(c) and c >= 0 for c in record["coloring"]), "COLORING_TYPE")
    need(is_int(record["minimum_count_probes"]) and 0 <= record["minimum_count_probes"] <= 2, "PROBE_MINIMUM_TYPE")
    need(type(record["supports"]) is list, "SUPPORTS_TYPE")
    need(all(is_int(s) and 0 <= s < (1 << n) for s in record["supports"]), "SUPPORT_RANGE")
    need(is_int(record["colorings_examined"]) and record["colorings_examined"] >= 1, "COLORING_COUNT_TYPE")
    return n, rows


def relation_from_rows(n: int, rows: Iterable[int]) -> set[tuple[int, int]]:
    return {(i, j) for i in range(n) for j in range(n) if (list(rows)[i] >> j) & 1}


def automorphisms(n: int, relation: set[tuple[int, int]]) -> list[tuple[int, ...]]:
    return [
        p
        for p in itertools.permutations(range(n))
        if {(p[a], p[b]) for a, b in relation} == relation
    ]


def minimum_distinguishing_coloring(
    n: int, permutations: list[tuple[int, ...]]
) -> tuple[int, list[int], int]:
    """Return the exact distinguishing number, first witness, and search count."""
    identity = tuple(range(n))
    nonidentity = [p for p in permutations if p != identity]
    examined = 0
    for colors in range(1, n + 1):
        for coloring in itertools.product(range(colors), repeat=n):
            examined += 1
            if all(any(coloring[i] != coloring[p[i]] for i in range(n)) for p in nonidentity):
                return colors, list(coloring), examined
    raise Invalid("NO_DISTINGUISHING_COLORING")


def verify(record: dict) -> dict:
    started = time.monotonic()
    n, rows = validate_record_shape(record)
    relation = {(i, j) for i in range(n) for j in range(n) if (rows[i] >> j) & 1}
    need(all((i, i) in relation for i in range(n)), "NONREFLEXIVE_POSET")
    need(all(i == j or (j, i) not in relation for i, j in relation), "NONANTISYMMETRIC_POSET")
    need(
        all((a, d) in relation for a, b in relation for c, d in relation if b == c),
        "NONTRANSITIVE_POSET",
    )
    need(all(i <= j for i, j in relation), "NOT_NATURALLY_LABELLED")

    perm = automorphisms(n, relation)
    need(len(perm) == record["automorphism_count"], "AUTOMORPHISM_COUNT_MISMATCH")

    true_d, first_coloring, coloring_count = minimum_distinguishing_coloring(n, perm)
    need(record["distinguishing_number"] == true_d, "DISTINGUISHING_NUMBER_MISMATCH")
    need(record["colorings_examined"] == coloring_count, "COLORINGS_EXAMINED_MISMATCH")
    color = record["coloring"]
    need(color == first_coloring, "COLORING_WITNESS_MISMATCH")
    need(len(set(color)) == true_d, "COLORING_COLOR_COUNT_MISMATCH")

    ideals = [
        s
        for s in range(1 << n)
        if all(not ((s >> b) & 1) or ((s >> a) & 1) for a, b in relation)
    ]
    induced = []
    for p in perm:
        induced.append([sum(1 << p[i] for i in range(n) if (s >> i) & 1) for s in ideals])
    tables = {support: [(support & ideal).bit_count() for ideal in ideals] for support in range(1 << n)}
    index = {ideal: i for i, ideal in enumerate(ideals)}
    # This table is calculated from integer counter values on complete ideals,
    # not from point colors or the producer's distinguishing-number field.
    survives = {
        support: [
            all(tables[support][index[target]] == tables[support][i] for i, target in enumerate(image))
            for image in induced
        ]
        for support in tables
    }

    by_k = []
    least = None
    winning: list[int] = []
    for k in range(0, 3):
        accepted = 0
        first = None
        for supports in itertools.product(range(1 << n), repeat=k):
            stabilizer = [
                pi
                for pi in range(len(perm))
                if all(survives[support][pi] for support in supports)
            ]
            if len(stabilizer) == 1:
                accepted += 1
                if first is None:
                    first = list(supports)
        by_k.append({"probes": k, "families": (1 << n) ** k, "rigid_families": accepted})
        if accepted:
            least = k
            winning = first if first is not None else []
            break
        if time.monotonic() - started > 100:
            raise TimeoutError("probe search deadline")

    need(least is not None, "NO_RIGID_SUPPORT_FAMILY")
    need(least == record["minimum_count_probes"], "MINIMUM_COUNT_PROBES_MISMATCH")
    need(least == (true_d - 1).bit_length(), "THEOREM_RELATION_MISMATCH")

    chosen = record["supports"]
    need(len(chosen) == least, "SUPPORT_COUNT_MISMATCH")
    expected_supports = [
        sum(1 << i for i in range(n) if (color[i] >> bit) & 1)
        for bit in range(least)
    ]
    need(chosen == expected_supports, "SUPPORT_ENCODING_MISMATCH")
    stable = [
        pi
        for pi in range(len(perm))
        if all(survives[support][pi] for support in chosen)
    ]
    need(len(stable) == 1, "PRODUCER_SUPPORTS_NOT_RIGID")

    signatures = [tuple(tables[support][i] for support in chosen) for i in range(len(ideals))]
    return {
        "points": n,
        "upper_sets": rows,
        "lattice_size": len(ideals),
        "automorphism_count": len(perm),
        "distinguishing_number": true_d,
        "first_distinguishing_coloring": first_coloring,
        "colorings_examined": coloring_count,
        "minimum_count_probes": least,
        "producer_supports": chosen,
        "first_optimal_supports": winning,
        "jointly_injective": len(set(signatures)) == len(ideals),
        "family_counts": by_k,
    }


def verify_universe(data: object) -> list[dict]:
    need(type(data) is list, "UNIVERSE_TYPE")
    parsed: list[tuple[int, tuple[int, ...], dict]] = []
    for record in data:
        n, rows = validate_record_shape(record)
        parsed.append((n, tuple(rows), record))

    keys = [(n, rows) for n, rows, _ in parsed]
    need(len(keys) == len(set(keys)), "DUPLICATE_POSET_RECORD")

    expected = {
        (n, rows)
        for n in range(1, 5)
        for rows in canonical_naturally_labelled_posets(n)
    }
    actual = set(keys)
    need(actual == expected, "INCOMPLETE_OR_EXTRA_POSET_UNIVERSE")
    need(Counter(n for n, _, _ in parsed) == Counter({1: 1, 2: 2, 3: 7, 4: 40}), "POSET_SIZE_COUNTS")

    return [verify(record) for _, _, record in parsed]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    verified = verify_universe(data)
    args.output.write_text(json.dumps(verified, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verified_posets": len(verified),
                "tested_families": sum(
                    stage["families"]
                    for record in verified
                    for stage in record["family_counts"]
                ),
                "distinguishing_colorings_examined": sum(
                    record["colorings_examined"] for record in verified
                ),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
