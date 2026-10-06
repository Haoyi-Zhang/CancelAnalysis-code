# Observation-relative cancellability for compositional algebraic analyses

This note is self-contained mathematical evidence for the finite claims. Its proofs are human-readable mathematical arguments, not proof-assistant derivations. Executable checks test finite instances and do not establish these general arguments by themselves. Standard closure-operator and lattice representation facts are proved where used; their underlying mathematics is not claimed as new.

## 1. Finite typed model

Let C be an explicitly specified finite category with a list G of generating arrows. A wire w carries a functor L_w from C to finite lattices and monotone maps. Write tau_w(a) for its map on an arrow a:P->Q. A fixed finite acyclic graph has external input wires and operator nodes in topological order. Node v has a (possibly repeated) ordered tuple of parent wires p(v), one output wire v, and a family of monotone functions

    f_v(P): product_{w in p(v)} L_w(P) -> L_v(P).

Repeated parents denote separate formal argument positions, not independent realizable values. The local naturality condition for a:P->Q is

    tau_v(a) f_v(P) = f_v(Q) product_{w in p(v)} tau_w(a).       (N)

The external input functor is I=product L_w over external input wires. Let E_w(P):I(P)->L_w(P) be the result at wire w, obtained by evaluating the graph, with input wires interpreted as projections. For selected output wires O, the ordinary global result is E_O=product_{w in O}E_w. Ordinary global robustness means naturality of E_O. It is distinct from local naturality of every f_v.

An observation at w is a natural family q_{wj}:L_w->Y_{wj}, with declared observer functor Y_{wj}. Observation robustness means naturality of q_{wj}E_w for each selected observation, together with ordinary global robustness when terminal outputs are included. It concerns a larger interface than the original external outputs.

All equalities quantify over every argument in the stated finite domain. Semantic soundness is not part of the definition of a monotone table. A separate concretization and soundness argument are needed to interpret a table as a sound abstract transformer.

### Proposition 1 (generators and composition)

If (N) holds on every generator, it holds on every arrow. If every node is locally natural, every E_w and every result formed from natural observations is natural.

**Proof.** Identity squares commute by the functor identity laws. For composable arrows a:P->Q and b:Q->R, assume the two local squares commute. With T denoting the parent-product functor,

    tau_v(ba) f_v(P)
      = tau_v(b) tau_v(a) f_v(P)
      = tau_v(b) f_v(Q) T(a)
      = f_v(R) T(b) T(a)
      = f_v(R) T(ba).

Induction on a generator word proves the first statement. The explicit category and functor laws ensure that different words for the same arrow have the same meaning. For the graph statement, input projections are natural. At a node v, the tuple B_v=(E_w)_{w in p(v)} is natural if all parent executions are. Composing B_v with the local square for f_v shows naturality of E_v=f_v B_v. Topological induction reaches every wire. Products and postcomposition with natural observations preserve naturality. QED.

The argument requires no distributivity. Finiteness is needed for the delivered exhaustive checker, not for this elementary implication.

### Proposition 2 (known-context cancellation)

Suppose B:I->X and S:Y->Z are natural, B(P) is surjective at the source of each generator, S(Q) is injective at its target, and F(P)=S(P)f(P)B(P). Naturality of F implies naturality of f.

**Proof.** For a:P->Q, use naturality of B and S in the square for F to obtain

    S(Q) tau_Y(a) f(P) B(P)
      = S(Q) f(Q) tau_X(a) B(P).

Cancel the injective S(Q), then the surjective B(P), to get the square for f. Proposition 1 extends generator squares. Both contexts must already be natural; this argument cannot cancel several unknown factors simultaneously. QED.

### Proposition 3 (general observed-DAG converse)

For every node output v, suppose its observation family is jointly injective at every generator target. Include the identity observation when the full wire is an ordinary output. Suppose the tuple map B_v(P):I(P)->product L_parent(P) is surjective at every generator source. Then observation robustness is equivalent to local naturality of every node.

**Proof.** One direction is Proposition 1. Conversely, for a:P->Q and external x, observation naturality and naturality of q give, for every j,

    q_vj(Q) tau_v(a) E_v(P)(x)
      = q_vj(Q) E_v(Q) tau_I(a)(x).

Joint injectivity identifies the two wire values, so E_v is natural; input projections already are. The tuple B_v is consequently natural. Since E_v=f_v B_v, the same equality without q reads

    tau_v(a) f_v(P) B_v(P)
      = f_v(Q) product tau_parent(a) B_v(P).

Surjectivity of B_v(P) gives (N) on every formal parent tuple. QED.

Joint surjectivity is a substantive assumption. In a two-element chain, feed the same input twice to a binary node. The families AND at P and first projection at Q agree on the reachable diagonal {(0,0),(1,1)}, but disagree on (1,0). Both argument projections are individually surjective. Even a full observation of the output cannot expose the unreachable disagreement.

Proposition 3 is a sufficient rule, not a claim that coverage is necessary for every fixed monotone instance. On the chain {0<1}, a monotone function with f(0)=1 must also satisfy f(1)=1. A constant-0 prefix can therefore leave input 1 unreachable while the observed value at 0 determines the whole function. A proved law or monotonicity constraint may fix off-relation values; the correlated-input control shows only that this cannot be assumed in general.

## 2. Masking and the meaning of soundness

### Proposition 4 (small reversible masking)

Let L be the four-element Boolean lattice and let s interchange its two atoms. For a two-object category P->Q with identity transports, put (f_1(P),f_2(P))=(id,id) and (f_1(Q),f_2(Q))=(s,s). Both operators fail naturality, while their composite is identity at both objects. Every component is an order isomorphism.

**Proof.** The atom interchange preserves the lattice order and squares to identity. At either atom, each local square fails. The products are identity. A single gate cannot exhibit this masking when the full final state is observed, because it is the global map. A finite lattice with fewer than four elements is a chain and has no nonidentity order automorphism. These are minimum gate and lattice sizes within this two-object constant-transport reversible fragment; no minimum-object claim is made for arbitrary categories with nonidentity endomorphisms. QED.

If H is any nontrivial closure, the two sound skip transformers id and H can also be masked by a constant-top final transformer. This is erasure, not reversible masking.

### Proposition 5 (extensive reversible maps)

An extensive order automorphism of a finite poset is identity.

**Proof.** A permutation f has finite order k. Extensivity gives x<=f(x)<=...<=f^k(x)=x. Antisymmetry makes every inequality equality. QED.

Thus the atom-interchange example is not a sound skip abstraction under the usual faithful concretization. The closure examples below are extensive and do supply sound skip abstractions. Monotonicity, reversibility, and semantic soundness must not be conflated.

## 3. Which observations identify closure operators?

A closure operator c:L->L is monotone, extensive (x<=c(x)), and idempotent. Let Q=(q_j) be a family of monotone, state-only observations. Say Q is *strict on comparable pairs* when for every x<y there is j with q_j(x) != q_j(y). Joint injectivity on arbitrary pairs is stronger.

### Theorem 6 (exact closure-observation criterion)

For a finite lattice L, the following are equivalent:

1. For all closure operators c,d on L, equality q_j c=q_j d for all j implies c=d.
2. Q is strict on comparable pairs.

**Proof, 2 implies 1.** If x is fixed by c, equality of observations gives q_j(d(x))=q_j(c(x))=q_j(x) for every j. Since x<=d(x), strictness forces d(x)=x. Symmetry shows that c and d have the same fixed points. Every closure sends x to the least fixed point above x: c(x) is fixed and above x; if y is fixed and x<=y, monotonicity gives c(x)<=c(y)=y. Hence equal fixed-point sets imply equal closures.

**Proof, 1 implies 2.** Suppose a<b and q_j(a)=q_j(b) for every j. Write top for the lattice maximum. Define

    C_b(x)   = b if x<=b, and top otherwise;
    D_ab(x)  = a if x<=a, b if x<=b but x is not <=a,
               and top otherwise.

Both maps are monotone, extensive and idempotent. Their images are respectively {b,top} and {a,b,top}, with redundant entries removed; these are chains. They differ only on inputs x<=a, where their values b and a have identical observations. Thus Q C_b=Q D_ab despite C_b(a)!=D_ab(a). QED.

**Reconstruction.** A complete observed profile q_j(c(x)), together with q_j(x), determines exactly the fixed points by equality of all coordinates. The closure is then the least fixed point above each x, or the meet of all fixed points above x. This uses the whole input-indexed profile, not a single observed scalar value.

**Contrast with unrestricted monotone maps.** If Q identifies every monotone map X->L for a nonempty X, then Q is jointly injective on L: any indistinguishable a,b give indistinguishable distinct constant maps. Conversely joint injectivity cancels any maps pointwise. The weaker criterion in Theorem 6 uses extensivity and idempotence, not merely monotonicity.

### Corollary 7 (exact scalar range budget)

Let h be the number of elements in a longest chain of L. A single monotone scalar observation identifying all closures requires at least h distinct ordered values, and h suffice. More generally, observations into chains {0,...,b_j} can identify all closures exactly when sum_j b_j >= h-1.

**Proof.** Along a longest chain, the joint observation must change at every strict step. Each coordinate is nondecreasing and can increase at most b_j times in units of at least one. Thus total capacity must be at least h-1. For sufficiency, let r(x) be the maximum number of strict steps in a chain ending at x. If x<y, r(y)>=r(x)+1, and 0<=r(x)<=h-1. For s_j=sum_{ell<j}b_ell, set q_j(x)=min(b_j,max(0,r(x)-s_j)). The resulting vector distinguishes every two distinct ranks from 0 to h-1 whenever sum b_j>=h-1. Therefore it is strict on comparable pairs. Taking one b=h-1 gives the scalar result. QED.

This is a bound on fixed, monotone, poststate-only observations, not on arbitrary certificates or relational instrumentation. The input-output predicate [c(x)=x] already encodes the fixed-point set using one bit per tested input, but it is not a function of the output state alone. A fixed-point bit vector can be a smaller standalone closure encoding than a rank profile. No compression optimality over such encodings is claimed.

### Lemma 8 (asymmetric observation cancellation)

Let X,Y be posets, tau:X->Y monotone, c:X->X extensive and idempotent, and d:Y->Y monotone and extensive. The source c need not be monotone; the target d need not be idempotent. Let Q be a family of maps on Y jointly separating every strict comparable pair. Then

    Q tau c = Q d tau   if and only if   tau c = d tau.

Neither finiteness, distributivity, injectivity of Q, nor invertibility of tau is needed for this lemma. These broader mathematical hypotheses do not expand the declared finite checker input model.

**Proof.** Only the forward direction needs proof. At the input c(x), observed equality and c(c(x))=c(x) give Q(tau c(x))=Q(d tau c(x)). Extensivity of d makes these two arguments comparable, hence d tau c(x)=tau c(x). Since x<=c(x), monotonicity of tau and d gives d tau(x)<=d tau c(x)=tau c(x). Observed equality at x and separation of comparable pairs now force d tau(x)=tau c(x). QED.

**Constructive witness.** If tau c(x) differs from d tau(x), then some observation differs at x or at c(x). Otherwise the two equalities used in the proof hold and force equality. Thus a known failed square transfers to an observed failure after at most one additional application of the source c. This does not promise that c(x) is the least encoded input.

Theorem 6 is the tau=id, c,d closures instance, with the explicit two-closure construction supplying necessity of strictness. Lemma 8 also explains the asymmetry: source idempotence and target monotonicity do the work, not a formal inverse of the transport.

**Sharp boundary controls on B2.** Write maps in the order (empty,{a},{b},{a,b}), and let Q=(0,1,1,2). In each following triple (tau,c,d), the full observed equation holds but the underlying square does not. Each drops only the indicated condition of Lemma 8:

- source idempotence: ((0,1,1,3),(1,3,3,3),(2,3,2,3));
- source extensivity: ((0,1,2,3),(0,1,1,3),(0,1,2,3));
- transport monotonicity: ((0,0,1,2),(0,1,3,3),(0,1,2,3));
- target extensivity: ((0,0,0,1),(0,1,2,3),(0,2,0,2));
- target monotonicity: ((0,0,0,1),(3,3,3,3),(2,1,2,3)).

The finite transport oracle verifies these tables and the retained hypotheses independently.

## 4. Nested closure forests

A closure forest is a unary acyclic graph in which each component is rooted at an external input. Every wire in a component uses one ambient lattice and the same monotone transport. Each node v carries a closure c_v. If node u is the parent of node v, assume c_u <= c_v pointwise. External inputs act as identity closures. Branching is allowed; merge nodes are not. Every sink is a full output, while each other node has a natural observation family. A linear nested pipeline is the one-branch special case.

### Lemma 9 (absorption and path collapse)

If c<=d are closures, then dc=cd=d. Consequently the executed map E_v along the unique root-to-v path is exactly c_v.

**Proof.** For dc, x<=c(x)<=d(x), so monotonicity and idempotence of d give d(x)<=d(c(x))<=d(d(x))=d(x). For cd, extensivity gives d(x)<=c(d(x)), while c<=d gives c(d(x))<=d(d(x))=d(x). Induct down the unique path: a root node executes c_v, and a child v of u executes c_v E_u=c_v c_u=c_v. QED.

### Theorem 10 (closure-forest reflection)

If every non-output observation family is natural and separates strict comparable pairs at each generator target, observation robustness is equivalent to local naturality of every forest node. No prefix-surjectivity assumption is needed.

**Proof.** Local naturality implies observation robustness by Proposition 1. Conversely, path collapse changes naturality of the observed execution at v into Q_v tau c_v(P)=Q_v c_v(Q) tau. For a sink, use the identity observation supplied by the full output. Lemma 8 gives tau c_v(P)=c_v(Q) tau. This holds on generators and hence on all arrows. QED.

For common L, identity transports on wires and observer codomains, fixed observation families Q_v, a connected category with at least two objects, and unrestricted nested closure families, strictness at every internal cut is also necessary for universal reflection. A linear pipeline is already a closure forest. If Q_v flattens a<b, place D_ab and C_b from Theorem 6 at that cut on a nonconstant partition of the program objects, use identity closures above it, and constant-top closures below it. Every observed execution is natural and every sink is constant top, while the selected local square fails. This is universal necessity for the stated class, not instance-wise necessity.

These additional category and transport premises matter. In an identity-only category every local square commutes without any observation. In a two-object insertion category whose generator transport is constant top, every closure square also commutes: tau c(x)=top=c'(tau(x)), since a closure fixes top. Constant observations are natural in both examples. The forest sufficiency theorem remains unchanged, but strictness is not universally necessary for an arbitrary fixed transport.

The height observation r is natural under every order isomorphism, since isomorphisms preserve chains and their lengths. Thus rank gives an explicit observer in the common identity/isomorphism special case. For arbitrary monotone transports, observer naturality must be checked rather than assumed. The noninjective B2 transport (0,1,1,3) preserves rank and supplies a genuinely noninvertible instance. On a distributive ideal lattice, r(I)=|I|.

Input coverage is not hidden in the theorem. A nonidentity closure prefix can have a proper image, but absorption determines every later nested closure from its executed path. Removing nesting invalidates that step: for a nonidentity closure e, put e at the first stage at both objects and put identity at the second stage at P but e at Q. Both executed prefixes equal e, yet the second local square fails. Unique parents are also essential to this argument. At a merge, formal product tuples may be unreachable even when each marginal is covered; the correlated-input counterexample witnesses this boundary.

Under the hypotheses of Theorem 10, every forest defect at x is exposed by Lemma 8 at x or c_v(P)(x). Lemma 9 gives the node execution itself as E_v(P)=c_v(P), so both are realizable root inputs. The statement keeps the same transformation and node; only the input may change. The retained flat-observer case shows why strictness must remain explicit: c_P=(0,3,2,3), c_Q=(2,3,2,3), Q=(0,1,0,1), and x=0 give unequal local values 0 and 2 with equal observation 0; the second input c_P(0) is again 0. This case is outside Theorem 10 because Q flattens the comparable pair 0<2.

## 5. Reversible pipelines

Let a connected finite category have m>=2 objects and identity state transports on a common finite lattice L. At each internal cut fix an object-independent family of monotone functions q:L→Y_q into constant observer functors with identity transports. A length-n pipeline, n>=2, has factors in G=Aut(L) and a fixed composite H. For internal cut i, let K_i be the subgroup of automorphisms g such that qg=q for every observation q at that cut. Write A_i(P)=f_i(P)...f_1(P), with A_0=id and A_n=H.

### Theorem 11 (reversible reflection and factorization count)

For this fixed-observer class, the number of fixed-composite pipelines whose internal observations are natural is

    |G|^(n-1) product_{i=1}^{n-1} |K_i|^(m-1).

Exactly |G|^(n-1) are locally natural. Hence the enlarged interface reflects local naturality for every pipeline in this class if and only if every K_i is trivial.

**Proof.** Prefixes determine the factors uniquely by f_i(P)=A_i(P)A_{i-1}(P)^{-1}. Fix a base object P_0. Since transports are identities and the category is connected, observed naturality at cut i is equivalent to qA_i(P)=qA_i(P_0) for every object P and every observation q. This is equivalent to A_i(P)A_i(P_0)^{-1} being in K_i. For each internal cut, choose A_i(P_0) in |G| ways and then, independently, one element of K_i for each of the other m-1 objects. Multiplying over the n-1 cuts gives the displayed count. Local naturality is exactly constancy of every prefix A_i, leaving |G| choices per cut and |G|^(n-1) total. If some K_i contains a nonidentity element, alter A_i at one non-base object by that element and recover the adjacent factors from the prefix formula; observations remain natural while local naturality fails. If every K_i is trivial, observed naturality forces every prefix, and hence every factor, to be constant. QED.

The theorem concerns the admitted automorphism group, fixed observation functions with identity observer transports, identity state transports, and a connected finite category. It does not give a formula for arbitrary natural observation functors, noninvertible factors or mixed closure/reversible pipelines.

## 6. Optimal subset-count probes

For a finite distributive lattice L let P=J(L), the poset of nonzero join-irreducibles. Identify L with Idl(P), the ideals ordered by inclusion. For S subset P, an allowed unweighted count probe is

    q_S(I)=|I intersect S|.

It is monotone into the chain 0,...,|S|.

**Representation justification.** Every element x of a finite lattice is the join of the join-irreducibles below it, by induction on the size of its lower set. Distributivity makes each join-irreducible j join-prime: if j<=a join b, then j=(j meet a) join (j meet b), so j<=a or j<=b. Consequently x maps to {j:j<=x} as an injective lattice homomorphism to ideals. For an ideal I, x=join I has exactly I as its join-irreducibles, by join-primality and downward closure. This is surjectivity. Lattice automorphisms restrict to poset automorphisms of P, and any automorphism of P acts on ideals; these operations are inverse.

### Lemma 12 (counter stabilizers)

An automorphism g of P preserves q_S on every ideal if and only if g(S)=S.

**Proof.** q_S(gI)=|I intersect g^{-1}S|, so setwise preservation is sufficient. Conversely define w(p)=1_{g^{-1}S}(p)-1_S(p). Equality of counters means sum_{p in I}w(p)=0 for every ideal I. In particular this holds for every principal ideal down(p). Induct in a linear extension of P: after all strict predecessors have weight zero, the principal-ideal equation gives w(p)=0. Thus all weights are zero and g^{-1}S=S. QED.

The argument uses full integer counts. Merely thresholding a count can lose information on comparable join-irreducibles; the same proof cannot be reused for arbitrary Boolean predicates.

Let D(P) be the least number of colors in a coloring of P that no nonidentity order automorphism preserves. Put D(empty)=1. This is the standard distinguishing-number invariant.

### Theorem 13 (restricted optimum)

The least number of unweighted subset-count probes with trivial common automorphism stabilizer is ceil(log_2 D(P)).

**Proof.** A family S_1,...,S_k colors each point by the k-bit incidence vector (1_{S_1}(p),...,1_{S_k}(p)). Lemma 12 says its stabilizer is exactly the color-preserving automorphism group. Triviality therefore gives a distinguishing coloring with at most 2^k colors, proving the lower bound. Conversely encode a distinguishing D(P)-coloring using k=ceil(log_2 D(P)) binary digits and use the digit supports as the S_j. The resulting counters have trivial stabilizer. QED.

For d>=1 incomparable points, D(P)=d: any repeated color permits a transposition, and all distinct colors suffice. Hence a Boolean lattice with d atoms needs ceil(log_2 d) such probes. For P=empty, Idl(P) is the one-element lattice and D(empty)=1 yields zero probes. For two disjoint two-point chains, D(P)=2, so one probe suffices. The nine-element anchored-box lattice is the ideal lattice of this latter poset.

The theorem does not optimize arbitrary weighted sums, observation alphabet bits, relational observers, or cross-cut reuse. Assigning distinct weights to atoms can sometimes replace several counters by one wider weighted sum, outside the permitted syntax. Distinguishing colorings of L itself, as studied in the poset literature, are a different optimization problem from these counters on J(L).

## 7. Finite witnesses and verification complexity

### Proposition 14 (canonical minimum square)

If a locally naturality equation fails, some generator equation fails. Therefore a minimum-length noncommuting word has length one. Fix the artifact's arrow indices, node topological indices, and lexicographic tuple encoding. Exhaustively scanning generator/node/tuple triples in that order returns the unique least encoded failing square.

**Proof.** The first statement is the contrapositive of Proposition 1. Identity words never fail after functor validation, so length zero is impossible and one is minimum. Every relevant finite triple is scanned, so the first failing one is lexicographically least. QED.

This is minimality relative to declared encodings, not smallest concrete program, smallest lattice, smallest edit, or semantic distance between programs. Breadth-first search computes generator closure and shortest representatives of all category arrows; it is not needed to search for longer obstructions.

### Proposition 15 (finite checking contract)

For an admitted finite input, the checker rejects invalid category, lattice, typing, monotonicity, transport or observation structures before accepting a verdict. After validation, a certificate is accepted exactly when its local and external verdicts, failure counts and least generator witness equal the extensional equations of that input.

**Proof at the algorithmic level.** Category unit, typing, associativity and generator-closure loops cover every finite obligation. Order checks cover all order axioms, all pairwise joins and meets, and the distributive identity on all triples. Coordinatewise monotonicity checks suffice for a product order because any comparable tuples are connected by a sequence of coordinate increases. Transport identity/composition equations are exhaustive. Operator evaluation follows topological wire dependencies. The local loops enumerate every arrow, node and formal input tuple; global and observation loops enumerate every arrow and external input. Thus each collected inequality is an actual failed equation, and no failed equation is omitted. Generator completeness justifies existence of the canonical generator witness. Certificate fields are compared to freshly calculated values with type-sensitive JSON comparison. QED.

This is a proof of the stated algorithm and its coverage, not machine verification of the Python interpreter or implementation. The separately implemented producer and checker reduce shared-code coupling but share one development process and mathematical specification.

Let m be object count, h arrow count, g generator count, v node count, N maximum lattice size, a_v node arity, U=sum_v product_parent |L_parent|, X the external input-product size, and k the number of scalar probes. Local diagram counts are hU (or gU using generators); whole-output comparisons are hX, each requiring graph evaluation unless cached. Scalar observation comparisons are hkX. A direct evaluator costs O(mX sum a_v) table lookup steps plus these comparison loops. Input table size is already proportional to mU; arity and independent external inputs can cause exponential growth in a succinct domain description.

Structural work is not free. A naive lattice join/meet construction takes O(N^4), distributivity O(N^3), category associativity O(h^3), and transport composition O((v+inputs)h^2N), in addition to product-map monotonicity checks. Integer encodings use O(log N) bits per state and bounded probe values. Bounded explicit-table checking does not imply a polynomial procedure for arbitrary succinct analyzers. The delivered caps count local, external and scalar-probe diagrams together; structural checks have separate finite dimension bounds and a process timeout.

## 8. Semantic fixtures and non-claims

The Boolean constant lattice is the powerset of {0,1}. The disjunctive sign lattice is the powerset of the three sign blocks, with abstraction collecting signs and concretization taking their union. The anchored boxes are [0,a] x [0,b], a,b in {0,1,2}; abstraction takes componentwise maxima with empty maximum zero, and concretization is box inclusion. This is a Galois insertion, although bottom does not represent the empty set exactly. All three lattices are distributive and pairwise nonisomorphic by cardinality 4,8,9. An extensive closure on any of them gives a sound coarsening of the identity abstract transformer and therefore a sound abstraction of skip.

The full interval domain on three ordered concrete values is not distributive: {1} meet ({0} join {2})={1}, while ({1} meet {0}) join ({1} meet {2}) is empty. The anchored-product restriction is explicit rather than silently treating full intervals as distributive.

Finite program objects consist of entry, selected labelled skip instructions, and return. Each program denotes identity; inserting skips preserves this semantics, and commuting insertions are identified by the category table. Generated algebraic operator graphs are not production analyzers. A separate nonidentity-transport case tests coordinate maps, not additional CFG expressiveness.

No theorem here handles recursive graph evaluation, irreducible CFG robustification, infinite domains, incomplete transformation vocabularies, noisy measurements, partial input sampling as a proof, or deployed analyzer performance. Naturality of the specified finite equational interfaces is not automatically the concrete-functor robustness notion of other categorical program-analysis frameworks.
