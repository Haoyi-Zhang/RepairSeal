# Source-linked ceiling division and its policy

## Selected-expression transfer

The optional typed bridge consumes the authoritative selected macro definition,
not a producer's normalized function. It admits pure unsigned word parameters,
nonnegative decimal literals, arithmetic with a word operand, and comparisons.
Arithmetic without a word operand is refused because C's signed intermediate
semantics would need a separate range argument. Calls, side effects, casts,
short-circuit operators and preprocessing are outside this bridge.

Under the caller-supplied pure unsigned-32 premise, structural induction gives
value and definedness correspondence. A parameter denotes its supplied word;
a permitted literal has its stated C value. With a word operand, usual
arithmetic conversions give unsigned word arithmetic, including conversion of
nonnegative literals and comparison results. Comparison operands in the
admitted vocabulary have nonnegative integer values, so Boolean promotion
preserves their comparison. A comparison used as a word is lowered to an
outer-block unsigned temporary set to zero or one by an explicit conditional.
That temporary equals the C/C++ comparison's numeric conversion. Division and
remainder keep the zero-divisor definedness condition. Other arithmetic is
modulo 2^32. Induction therefore relates the generated function's word result
to the selected macro expression wherever defined; it does not justify caller
types, select an active preprocessor branch, or preserve native execution traces.

The native retained check compares the original and replacement macros and
their generated lowerings at the existing 42 pure-argument points under both
GCC and Clang. The mathematical reference is calculated separately. It is a
bounded check of this translation argument for one upstream edit, not a new
source population or a mechanically verified compiler.

## Repair policy and mathematical correspondence

The source identity and exact before/after macro definitions are in
`public-data/ceil-div-source.json`. They come from llama.cpp PR 25245,
before revision d80e87850173a674ea2673fd003ac54ac93774c0 and after revision
86961efd5675279a4ec2f3d1a3c7d6e3803c1935, path
`ggml/src/ggml-vulkan/ggml-vulkan.cpp`. The MIT source notice is retained.
The optional retrieval checks the complete files' SHA-256 identities and the
exact macro lines. It reads source text, not executable evidence.

Assume the two macro arguments are pure unsigned 32-bit scalar values m,n,
with n>0. No claim is made for signed arithmetic, argument side effects or
caller evaluation. Set U=2^32-1. Original arithmetic computes
((m+n-1) mod 2^32) div n. Left-associated modular addition and subtraction
give this same result even if their individual intermediate sums wrap.

The receiver's region R is m+n-1>U, written without overflow as
m > U-(n-1). Since 1<=n<=U, n-1 and U-(n-1) are valid unsigned values.
For a point outside R, m+n-1 lies in [0,U], so its final modular numerator
equals the mathematical numerator. Thus the old result is mathematical
ceiling division there, including m=0.

The replacement computes q=m div n and adds one when m mod n is nonzero.
The explicit scalar normalization converts that comparison to an if. It
preserves the macro's integer result under the pure-argument premise. The
increment cannot wrap: n=1 has zero remainder, whereas n>=2 gives
q<=floor(U/2). Division/remainder are defined because n>0.

The separately written reference is 0 for m=0 and 1+(m-1) div n otherwise.
Its intermediates are in [0,U], and the quotient/remainder identity proves
that it equals the replacement. These identities establish repair-region
reference agreement and complementary preservation; they are not inferred
from the finite test count. Candidate definedness is checked separately.

The finite consumer chooses m in {0,1,2,31,32,U-1,U} and
n in {1,2,3,7,32,U}. This is a 42-point Cartesian domain with 12 repair and
30 preservation points. The universal certificate quantifies over those
points. The algebra above explains the local source mapping under the stated
premises; it does not establish call-site applicability or GPU behavior.

The unchanged original and actual replacement are source-linked local
models. The three adverse candidates are authored diagnostic controls.
The preservation control changes the zero-input output to 1; the definedness
control evaluates an unused 1/(n-1); and the trace control repairs only n=2,
preceded by an m=2 scratch branch. None is represented as an upstream patch.
Undefined expressions are interpreted as data, never executed in native C.

Source-if events belong to these explicit scalar functions. They are not
instrumented native macro events. For the trace control, (2,U) has trace
[(0,1),(1,0)] and (31,U) has trace [(0,0),(1,0)]. Both violate repair, but
the latter is canonical because trace precedes numeric input. A one-point
packet for the former remains a valid existential refutation. A compact
packet with an altered trace rejects, even if its outer digest is recomputed.

The direct baseline receives the identical source, domain, region, three
obligations and diagnostic ordering. It has the same counted semantic-cell
work and every identical verdict/witness. Full packets instead carry values
that a recipient authenticates under that policy; they do not supply extra
semantic information, prove their own source history, or accelerate ordinary
complete-domain decision.

## Selected caller's allocation-consumption obligation

The fixed source anchors in `public-data/descriptor-context.json` identify the
single-dispatch-family branch, unsigned batch declaration, request accumulation,
pool growth and descriptor consumption. The optional whole-source check verifies
these anchors in both complete immutable files. Vulkan's physical-device-limits
declaration gives the dispatch limit an unsigned32 type. This correspondence was
inspected for the selected context; a string-anchor check is not a general
control-flow or type-analysis algorithm.

Let the fixed batch and positive limit be b and l. After j loop iterations,
the mathematical invariant is a_j=min(b,j*l). Each machine update adds
min(b-a_j,l), so a_j stays in [0,b] and does not wrap. The loop therefore makes
q=ceil(b/l) dispatches, including zero when b=0. This is an unbounded algebraic
argument under these scalar conditions, not a claim obtained from the32 runs.

Let I<=R<=C be initial consumed, requested and allocated counts. Suppose adding
q does not wrap the cumulative counter, allocation succeeds with representable
counts, the limit remains fixed and there is no intervening consumer. Reserving
q gives C'>=R+q. Before dispatch j<q, its index is I+j<I+q<=R+q<=C'. Thus the
checked scalar result discharges this selected availability obligation. Other
GPU assertions, shader behavior, resource failures and concurrent mutation are
not part of that proposition.

The explicit starting state I=R=C=4 follows the accounting pattern reported
by the upstream contributor. At b=2,l=UINT32_MAX, the old count is zero and the
first dispatch lacks a slot. The new count is one; the selected 50-percent
growth rule raises capacity to six and the dispatch fits. The upstream report
is a reported device observation; the local execution is a source-derived,
project-authored accounting abstraction. An existing pool with spare capacity
can conceal the old under-request, as a separate regression demonstrates.

The same42 pairs as the expression study are filtered before native execution
by q<=64. All10 excluded pairs are retained as exclusions, not successes. The32
admitted pairs and two roles under two compilers give128 observed rows. The
seven pairs at the reported maximum limit are distinguished from the smaller
positive limits, which are arithmetic stress controls rather than claimed
device configurations. The
source-bound full certificate and equally informed direct receiver still
accept the42-point request with1680 cells each. This adds an application-level
consequence and its conditional proof, not new independent applications,
automated general caller admission, or a local Vulkan-device reproduction.
