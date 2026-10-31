#include <stdio.h>
#include <limits.h>
_Static_assert(UINT_MAX == 4294967295u, "requires unsigned32");
#define OLD_CEIL(M, N) (((M) + (N)-1) / (N))
#define NEW_CEIL(M, N) (((M) / (N)) + (((M) % (N)) != 0))
unsigned old_lowered(unsigned m, unsigned n) { return (((m + n) - 1u) / n); }
unsigned new_lowered(unsigned m, unsigned n) { unsigned rs_generated0 = 0u; if (((m % n) != 0u)) { rs_generated0 = 1u; } else { rs_generated0 = 0u; } return ((m / n) + rs_generated0); }
static const unsigned inputs[][2] = {{0u,1u},
{0u,2u},
{0u,3u},
{0u,7u},
{0u,32u},
{0u,4294967295u},
{1u,1u},
{1u,2u},
{1u,3u},
{1u,7u},
{1u,32u},
{1u,4294967295u},
{2u,1u},
{2u,2u},
{2u,3u},
{2u,7u},
{2u,32u},
{2u,4294967295u},
{31u,1u},
{31u,2u},
{31u,3u},
{31u,7u},
{31u,32u},
{31u,4294967295u},
{32u,1u},
{32u,2u},
{32u,3u},
{32u,7u},
{32u,32u},
{32u,4294967295u},
{4294967294u,1u},
{4294967294u,2u},
{4294967294u,3u},
{4294967294u,7u},
{4294967294u,32u},
{4294967294u,4294967295u},
{4294967295u,1u},
{4294967295u,2u},
{4294967295u,3u},
{4294967295u,7u},
{4294967295u,32u},
{4294967295u,4294967295u}};
int main(void) { for (unsigned i=0;i<42u;++i) {
unsigned m=inputs[i][0],n=inputs[i][1];
printf("%u,%u,%u,%u\n",OLD_CEIL(m,n),NEW_CEIL(m,n),old_lowered(m,n),new_lowered(m,n));
} return 0; }
