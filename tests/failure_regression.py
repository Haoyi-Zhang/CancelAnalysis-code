"""Pure bounded failure-accounting regressions; no private files or producer."""
from __future__ import annotations

import copy
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import checker

CERTIFICATE_KEYS = ('case', 'locally_natural', 'globally_natural',
                    'local_failures', 'global_failures', 'least_generator_witness')


def fixture(tables=None):
    # Put a non-generator composite before all generators. Declarations are
    # deliberately reverse ordered; canonical witnesses follow arrow indices.
    arrows = [[0, 0], [0, 3], [0, 1], [0, 2], [1, 1],
              [1, 3], [2, 2], [2, 3], [3, 3]]
    index = {tuple(a): i for i, a in enumerate(arrows)}
    composition = [[index[(b[0], a[1])] if b[1] == a[0] else None
                    for b in arrows] for a in arrows]
    cat = {'programs': [['entry', 'return'], ['entry', 'skip-0', 'return'],
                        ['entry', 'skip-1', 'return'],
                        ['entry', 'skip-0', 'skip-1', 'return']],
           'arrows': arrows, 'identities': [0, 4, 6, 8],
           'generators': [7, 5, 3, 2], 'composition': composition}
    return {'case': 'public-failure-accounting', 'category': cat,
            'domains': [{'name': 'two-state-chain', 'labels': ['0', '1'],
                         'leq': [[1, 1], [0, 1]]}], 'inputs': [0],
            'nodes': [{'inputs': [0], 'domain': 0,
                       'tables': [list(table) for table in (tables or [[0, 1]] * 4)]},
                      {'inputs': [1], 'domain': 0, 'tables': [[1, 1] for _ in range(4)]}],
            'outputs': [2], 'transports': [[[0, 1] for _ in arrows] for _ in range(3)],
            'probes': [{'wire': 1, 'tables': [[0, 1]]}]}


def independent_equations(case):
    """Raw finite equations using tuple maps and recursive wire evaluation.

    This is not structural validation and is used only on admitted fixtures.
    It does not call checker helpers or copy the historical implementation.
    """
    inputs, nodes = case['inputs'], case['nodes']
    wire_domains = inputs + [node['domain'] for node in nodes]
    sizes = [len(case['domains'][d]['labels']) for d in wire_domains]
    objects = len(case['category']['programs'])
    arrows = case['category']['arrows']
    transports = case['transports']
    arguments = [tuple(itertools.product(*(range(sizes[w]) for w in node['inputs'])))
                 for node in nodes]
    functions = {(obj, vi): dict(zip(arguments[vi], node['tables'][obj]))
                 for obj in range(objects) for vi, node in enumerate(nodes)}
    external = tuple(itertools.product(*(range(sizes[w]) for w in range(len(inputs)))))
    memo = {}

    def wire(obj, xs, w):
        key = (obj, xs, w)
        if key not in memo:
            if w < len(inputs):
                memo[key] = xs[w]
            else:
                vi = w - len(inputs)
                ys = tuple(wire(obj, xs, parent) for parent in nodes[vi]['inputs'])
                memo[key] = functions[obj, vi][ys]
        return memo[key]

    defects = {}
    for vi, node in enumerate(nodes):
        for xs in arguments[vi]:
            for ai, (source, target) in enumerate(arrows):
                left = transports[len(inputs) + vi][ai][functions[source, vi][xs]]
                ys = tuple(transports[w][ai][x] for w, x in zip(node['inputs'], xs))
                right = functions[target, vi][ys]
                if left != right:
                    defects[ai, vi, xs] = (left, right)
    generator_keys = sorted(key for key in defects if key[0] in case['category']['generators'])
    first = None
    if generator_keys:
        ai, vi, xs = generator_keys[0]
        left, right = defects[ai, vi, xs]
        first = [ai, vi, list(xs), left, right]
    global_count = 0
    probe_count = 0
    scalar_count = sum(len(probe['tables']) for probe in case['probes'])
    for xs in external:
        for ai, (source, target) in enumerate(arrows):
            ys = tuple(transports[w][ai][x] for w, x in enumerate(xs))
            global_count += any(transports[w][ai][wire(source, xs, w)] != wire(target, ys, w)
                                for w in case['outputs'])
            for probe in case['probes']:
                for table in probe['tables']:
                    probe_count += table[wire(source, xs, probe['wire'])] != table[wire(target, ys, probe['wire'])]
    local_diagrams = len(arrows) * sum(len(points) for points in arguments)
    global_diagrams = len(arrows) * len(external)
    coverage = [[len({tuple(wire(0, xs, w) for w in node['inputs']) for xs in external}),
                 len(points)] for node, points in zip(nodes, arguments)]
    return {'case': case['case'], 'locally_natural': not defects,
            'globally_natural': not global_count, 'local_failures': len(defects),
            'global_failures': global_count, 'least_generator_witness': first,
            'local_diagrams': local_diagrams, 'global_diagrams': global_diagrams,
            'generator_diagrams': len(case['category']['generators']) * sum(map(len, arguments)),
            'probe_checks': scalar_count * global_diagrams, 'probe_failures': probe_count,
            'total_diagrams': local_diagrams + (scalar_count + 1) * global_diagrams,
            'input_coverage_at_object_zero': coverage}


class FailureAccountingTests(unittest.TestCase):
    def compare(self, case):
        saved = copy.deepcopy(case)
        expected = independent_equations(case)
        actual = checker.audit(case)
        self.assertEqual({key: actual[key] for key in expected}, expected)
        self.assertEqual(case, saved)
        claimed = {key: expected[key] for key in CERTIFICATE_KEYS}
        self.assertEqual(checker.certificate(case, claimed), actual)
        return actual

    def test_exhaustive_monotone_chain_tables(self):
        # All 3^4 object-indexed monotone unary families, with three distinct
        # output/probe interfaces. Each case has at most 108 equation visits.
        for tables in itertools.product(([0, 0], [0, 1], [1, 1]), repeat=4):
            for mode in range(3):
                case = fixture(tables)
                if mode == 1:
                    case['outputs'] = [1, 2]
                    case['probes'] = []
                elif mode == 2:
                    case['outputs'] = [0, 1, 2]
                    case['probes'][0]['tables'] = [[0, 0], [0, 1], [1, 1]]
                self.compare(case)

    def test_non_generator_before_unsorted_generators(self):
        case = fixture([[0, 1], [1, 1], [0, 1], [1, 1]])
        actual = self.compare(case)
        self.assertEqual(actual['least_generator_witness'], [2, 0, [0], 0, 1])
        self.assertGreater(actual['local_failures'], 1)
        for declarations in itertools.permutations(case['category']['generators']):
            case['category']['generators'] = list(declarations)
            self.assertEqual(self.compare(case), actual)

    def test_identity_only_empty_generator_null_witness(self):
        case = fixture()
        case['category'] = {'programs': [['entry', 'return']], 'arrows': [[0, 0]],
                            'identities': [0], 'generators': [], 'composition': [[0]]}
        for node in case['nodes']:
            node['tables'] = node['tables'][:1]
        case['transports'] = [[[0, 1]] for _ in range(3)]
        actual = self.compare(case)
        self.assertIsNone(actual['least_generator_witness'])
        self.assertEqual((actual['local_failures'], actual['global_failures']), (0, 0))

    def test_repeated_parent_off_diagonal_failure(self):
        case = fixture()
        case['nodes'][0] = {'inputs': [0, 0], 'domain': 0,
                            'tables': [[0, 0, 0, 1], [0, 0, 1, 1],
                                       [0, 0, 0, 1], [0, 0, 1, 1]]}
        case['outputs'] = [1, 2]
        actual = self.compare(case)
        self.assertEqual(actual['input_coverage_at_object_zero'][0], [2, 4])
        self.assertEqual(actual['least_generator_witness'], [2, 0, [1, 0], 0, 1])
        self.assertFalse(actual['locally_natural'])
        self.assertTrue(actual['globally_natural'])

    def test_certificate_fields_remain_type_sensitive(self):
        case = fixture([[0, 1], [1, 1], [0, 1], [1, 1]])
        expected = independent_equations(case)
        certificate = {key: expected[key] for key in CERTIFICATE_KEYS}
        changes = {'case': 'other-case', 'locally_natural': 0, 'globally_natural': 1,
                   'local_failures': float(certificate['local_failures']),
                   'global_failures': False, 'least_generator_witness': None}
        for key, value in changes.items():
            bad = copy.deepcopy(certificate)
            bad[key] = value
            with self.assertRaisesRegex(checker.Invalid, 'CERTIFICATE_MISMATCH_' + key):
                checker.certificate(case, bad)

    def test_deadline_and_generator_validation_unchanged(self):
        case = fixture()
        with self.assertRaisesRegex(checker.Invalid, 'TIME_LIMIT'):
            checker.audit(case, seconds=-1)
        case['category']['generators'].append(case['category']['generators'][0])
        with self.assertRaisesRegex(checker.Invalid, '^GENERATORS$'):
            checker.audit(case)
        self.assertEqual(checker.MAX_BYTES, 4 * 1024 * 1024)
        self.assertEqual(checker.MAX_DIAGRAMS, 100_000)


if __name__ == '__main__':
    unittest.main()
