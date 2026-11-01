#include <stdint.h>
#include <stdio.h>
#include <limits.h>
_Static_assert(UINT_MAX == 4294967295u, "requires unsigned32");
#define OLD(M, N) (((M) + (N)-1) / (N))
#define NEW(M, N) (((M) / (N)) + (((M) % (N)) != 0))
static const uint32_t inputs[][2] = {{0u,1u},
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
{4294967294u,4294967295u},
{4294967295u,4294967295u}};
static void run(uint32_t batch,uint32_t limit,uint32_t n,unsigned role,unsigned pos) {
uint32_t requested=4u+n,allocated=4u,index=4u,base=0u,completed=0u; unsigned failed=0u;
if(allocated<requested) allocated=6u>requested?6u:requested;
while(base<batch) { uint32_t left=batch-base,groups=left<limit?left:limit;
if(completed>=64u) return;
if(index>=allocated) { failed=1u; break; } ++index; ++completed; base+=groups; }
printf("%u,%u,%u,%u,%u,%u,%u,%u,%u\n",pos,role,n,requested,allocated,index,completed,failed,base); }
int main(void) { for(unsigned i=0;i<sizeof(inputs)/sizeof(inputs[0]);++i) {
uint32_t b=inputs[i][0],n=inputs[i][1]; run(b,n,OLD(b,n),0u,i); run(b,n,NEW(b,n),1u,i); } return 0; }
