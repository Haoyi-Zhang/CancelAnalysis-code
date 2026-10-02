# Finite input and certificate representation

The scientific inputs are explicit tables, not Python expressions. All indices start at zero. JSON Boolean values are not integers for index or order-relation purposes. Duplicate keys and nonfinite JSON constants are rejected. A case is at most 4 MiB and contains exactly the following keys.

| Key | Representation |
|---|---|
| `case` | A nonempty identifier, at most 100 characters |
| `category` | `programs`, `arrows`, `identities`, `generators`, `composition` |
| `domains` | Between one and eight finite lattice records |
| `inputs` | One to three lattice indices for external wires |
| `nodes` | One to twenty nodes in topological order |
| `outputs` | A nonempty duplicate-free list of wire indices |
| `transports` | A table for every wire and every category arrow |
| `probes` | At most twenty observation records |

## Category and programs

`programs[P]` is a list beginning with `entry` and ending with `return`. There are at most sixteen interior labels, each a distinct string `skip-` followed by decimal digits. Program objects are indexed; a morphism is a declared insertion of labelled identity instructions. Existing labels must form an **order-preserving subsequence** of the target program. Set inclusion alone is insufficient. These fixtures have identity concrete semantics. The parser is not a language front end for arbitrary CFGs.

`arrows[a] = [P,Q]`. There are at most sixteen objects and sixty-four arrows, including identities. `identities[P]` names the identity at P. `composition[a][b]` denotes first b, then a, or `null` when endpoints do not match. The verifier checks typing, units, and all associativity obligations. Nonidentity generator indices are unique; breadth-first closure must reach every arrow. Parallel declared arrows are permitted when their explicit category laws hold; no equality is inferred from endpoints alone.

## Finite domains and wires

A domain has exactly `name`, `labels`, and `leq`. Labels are unique nonempty strings of at most 100 characters. `leq[x][y]` is integer 0 or 1. The verifier checks reflexivity, antisymmetry, transitivity, unique greatest lower and least upper bounds, and distributivity. A domain has one to thirty-two states.

The executable representation fixes one domain for a wire across all program objects. The broader mathematical notation in the proof note permits object-indexed lattices where its theorem states so. The executable coverage is not silently extended to that notation.

Wire indices first enumerate the external inputs, then one output for each node. A node contains exactly `inputs`, `domain`, and `tables`. Its one to three parent indices must refer to already available wires. Repeated parents are allowed. Each program object has one total output table; the input order is lexicographic Cartesian order, with the last coordinate varying fastest. Monotonicity is checked along every coordinate increase. All node tables together contain at most 100,000 entries.

`transports[w][a][x]` is the target state of x on arrow a. The checker validates totality, range, monotonicity, identities, and all compositions. Transports need not be injective or preserve meet/join.

## Observations and counted equations

An observation record has exactly `wire` and `tables`. Each record contains zero to six scalar tables on that wire. Their entries are integers from 0 through 32. Codomains are constant chains with identity transports. Scalar tables must be monotone and satisfy `table[transport[a][x]] == table[x]` for every arrow and state. Thus a nonnatural probe is not accepted as evidence of a gate's nonnaturality.

Let h be the number of arrows, U the sum of formal node input volumes, X the product of external input cardinalities, and k the number of scalar tables. The checked diagram budget is `h*(U+(k+1)*X) <= 100000`. Identities are counted. Ordinary global checking compares the selected output tuple once per arrow/input, not once per scalar output coordinate. This convention is used consistently in all tables. Structural validation is additional work, not included in the diagram count.

Formal products and reached tuples are distinct. A repeated parent may reach only a diagonal even when each coordinate is marginally surjective. `input_coverage_at_object_zero` is descriptive coverage at that one object; it is not a proof of universal coverage across all generator sources.

## Certificates and failure behavior

A certificate has exactly six fields: `case`, `locally_natural`, `globally_natural`, `local_failures`, `global_failures`, `least_generator_witness`. Naturality fields are Boolean, failure counts integers. A local witness is `[arrow_index,node_index,input_tuple,left,right]`; it is null exactly when there is no local failure.

The least witness is ordered by generator arrow index, node index, then lexicographic formal input tuple. Category validation and the generator-extension proof imply that a failure has a one-generator witness. This is not minimality of the program, domain, node set, or semantic counterexample.

The certificate is a summary, not a succinct proof allowing sublinear verification. The independent checker recomputes all extensional obligations, then compares all six fields with type-sensitive JSON equality. `cases/certificates.json` is an array used by the campaign; the checker's single-certificate option expects one object, not that entire array.

Invalid structures, malformed certificates, exhausted checking time, or input I/O failure must not be interpreted as a scientific negative result. The bounded runner records job failure and stops. The separate closure/probe enumeration scripts consume only the fixed candidate representation produced within this repository; they are not a general parser for arbitrary uploaded datasets or an untrusted-code sandbox.
