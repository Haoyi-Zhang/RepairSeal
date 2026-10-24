# Source-linked ceiling division and its policy

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
