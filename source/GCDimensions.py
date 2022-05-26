
from sage.all import *

sGCdims = \
"""36 0 0 0 0 0 0 0 0 0 0 323 6914443 10238197936 2434452003889 149691529204800 3065797882254941 24210784546884942 80125688022289219 115536095318709248 72644240367676642 19131543576030878 1915629738270074 59880793175801 377177693363 103765564
35 0 0 0 0 0 0 0 0 0 0 1005 12300248 11395934706 1854245794476 81248861159249 1206602153008407 6924193168254424 16471150498499870 16647312912300163 7021476589491775 1152712839432828 63299869884371 840308953765 1094185703 0
34 0 0 0 0 0 0 0 0 0 0 2853 20143069 11797416222 1312699826317 40738291624423 434093265619034 1782503996695968 2981432508808535 2045883700715935 551569517056290 52153482139678 1353903801649 5279400293 0 0
33 0 0 0 0 0 0 0 0 0 0 7858 30373223 11324845175 859478584099 18738781553491 141412445181865 407651323249567 466336702482262 208454338524126 33628719414227 1628346636468 15426982080 6247329 0 0
32 0 0 0 0 0 0 0 0 0 0 20198 42109841 10041540904 517319664519 7841523412407 41233491145291 81471527376402 61513198271050 16943477036119 1487486705470 30453218431 59572065 0 0 0
31 0 0 0 0 0 0 0 0 0 0 46221 53552162 8183597882 284157684349 2954983872822 10607822460710 13933178693051 6623831313164 1040005051656 42886529623 257189208 0 0 0 0
30 0 0 0 0 0 0 0 0 0 3 93366 62298561 6092177954 141175882137 990244991515 2364327746626 1983424893300 556534619930 44349201196 664231574 412966 0 0 0 0
29 0 0 0 0 0 0 0 0 0 32 168907 66042289 4111001284 62747495599 290471343715 445893643989 226333613711 34141128298 1141986095 3521433 0 0 0 0 0
28 0 0 0 0 0 0 0 0 1 127 276458 63413970 2490799385 24610685274 73085889211 68938018460 19620090166 1375793368 13412419 0 0 0 0 0 0
27 0 0 0 0 0 0 0 0 1 311 407915 54684111 1339061158 8371041155 15357400905 8360542063 1190269491 30068745 30528 0 0 0 0 0 0
26 0 0 0 0 0 0 0 0 0 684 537528 41907083 629274575 2413785991 2598217463 745263236 43995862 227577 0 0 0 0 0 0 0
25 0 0 0 0 0 0 0 0 0 1545 627110 28187228 253575578 572310253 335860329 44006088 749459 0 0 0 0 0 0 0 0
24 0 0 0 0 0 0 0 0 1 3213 641553 16379726 85417799 106923865 30618203 1424662 2526 0 0 0 0 0 0 0 0
23 0 0 0 0 0 0 0 0 7 5625 567604 8048887 23223881 14779073 1718769 16244 0 0 0 0 0 0 0 0 0
22 0 0 0 0 0 0 0 0 17 8208 426113 3246800 4844186 1365037 45030 0 0 0 0 0 0 0 0 0 0
21 0 0 0 0 0 0 0 0 28 10175 265083 1032036 716981 69847 221 0 0 0 0 0 0 0 0 0 0
20 0 0 0 0 0 0 0 0 65 10658 132526 243759 66081 1274 0 0 0 0 0 0 0 0 0 0 0
19 0 0 0 0 0 0 0 0 155 9033 50863 38916 2938 0 0 0 0 0 0 0 0 0 0 0 0
18 0 0 0 0 0 0 0 0 252 5849 13867 3497 30 0 0 0 0 0 0 0 0 0 0 0 0
17 0 0 0 0 0 0 0 0 291 2742 2329 110 0 0 0 0 0 0 0 0 0 0 0 0 0
16 0 0 0 0 0 0 0 4 262 879 188 0 0 0 0 0 0 0 0 0 0 0 0 0 0
15 0 0 0 0 0 0 1 14 179 170 7 0 0 0 0 0 0 0 0 0 0 0 0 0 0
14 0 0 0 0 0 0 1 16 75 13 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
13 0 0 0 0 0 0 0 10 12 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
12 0 0 0 0 0 0 0 6 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
11 0 0 0 0 0 0 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
10 0 0 0 0 0 0 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
9 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
7 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
6 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
5 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
0 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24"""

# edges, vertices
GCdims = [ [int(w) for w in s.split(" ")[1:] ] for s in sGCdims.splitlines()]
max_vertices = 24
max_edges = 36

# The following routines provide estimates (!!) of the numbers of graphs
def get_ordinary_dim_estimate(n_vertices, n_loops):
    n_edges = n_loops + n_vertices - 1
    if n_edges <= 0 or n_vertices <= 0:
        return 0
    if n_edges <= max_edges and n_vertices <= max_vertices:
        return GCdims[max_edges-n_edges][n_vertices]
    # fallback: use very course estimate
    return binomial((self.n_vertices * (self.n_vertices - 1)) / 2, self.n_edges) / factorial(self.n_vertices)

def get_hairy_dim_estimate(n_vertices, n_loops, n_hairs):
    # hairs can be either on vertices or "on edges" of ordinary graphs
    n_edges = n_loops + n_vertices - 1
    if n_edges <0 or n_vertices <0 or n_hairs<0:
        return 0
    sum = 0
    for n_hairs_on_v in range(n_hairs+1):
        n_hairs_on_e = n_hairs - n_hairs_on_v
        n_reduced_verts = n_vertices - n_hairs_on_e
        n_reduced_edges = n_loops + n_reduced_verts - 1
        gcdim = get_ordinary_dim_estimate(n_reduced_verts, n_loops)
        sum = sum + gcdim * binomial(n_reduced_verts, n_hairs_on_v) \
                    * (n_reduced_edges ** n_hairs_on_e)
    return sum

def get_chairy_dim_estimate(n_vertices, n_loops, n_hairs):
    # very crude
    return get_hairy_dim_estimate(n_vertices, n_loops, n_hairs) * factorial(n_hairs)


def get_wrhairy_dim_estimate(n_vertices, n_loops, n_hairs, n_ws):
    # very crude
    return get_hairy_dim_estimate(n_vertices+1, n_loops, n_hairs+n_ws) * factorial(n_hairs)


## Test
# print([len(s) for s in GCdims])
# print( get_ordinary_dim_estimate(24, 13) )

# for l in range(15):
#     print(f"{l}:", *[get_ordinary_dim_estimate(v,l) for v in range(23)])

# for h in range(8):
#     print(f"\n{h} hairs:")
#     for l in range(15):
#         print(f"{l}:", *[get_ordinary_dim_estimate(v,l) for v in range(23)])
