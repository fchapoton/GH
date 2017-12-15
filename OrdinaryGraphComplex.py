import os
from sage.all import *
import GraphVectorSpace as GVS
import GraphOperator

reload(GVS)
reload(GraphOperator)

dataDir = "./data"
dataDirOdd = dataDir + "/ordinary/oddedge/"
dataDirEven = dataDir + "/ordinary/evenedge/"
imgBaseDir = "img/"


class OrdinaryGVS(GVS.GraphVectorSpace):

    def __init__(self, nVertices, nLoops, evenEdges=True):
        self.nVertices = nVertices
        self.nLoops = nLoops
        self.evenEdges = evenEdges

        self.nEdges = self.nLoops + self.nVertices - 1

        directory = dataDirEven if self.evenEdges else dataDirOdd
        s = "gra%d_%d.g6" % (self.nVertices, self.nLoops)
        file_name = os.path.join(directory, s)

        valid = (3 * self.nVertices <= 2 * self.nEdges) and self.nVertices > 0 and self.nLoops >= 0 and self.nEdges <= self.nVertices * (self.nVertices - 1) / 2

        super(OrdinaryGVS,self).__init__(valid, file_name)

    def _generating_graphs(self):
        # generate List of unmarked graphs
        graphList = self._list_graphs(self.nVertices, self.nLoops)
        #graphList = slef._listGraphs(self.nVertices, self.nLoops, false)
        return graphList

    def _list_graphs(self, nVertices, nLoops, onlyonevi=True):
        """
        creates a list of simple 1vi graphs with at least trivalent vertices
        """
        nEdges = nLoops + nVertices - 1
        if (3 * nVertices > 2 * nEdges) or (nEdges > nVertices * (nVertices - 1) / 2):
            # impossible
            return []
        gL = list(graphs.nauty_geng(("-Cd3" if onlyonevi else "-cd3") + " %d %d:%d" % (nVertices, nEdges, nEdges)))
        return gL

    def perm_sign(self, G, p):
        nVert, nLoops, evenEdges = (self.nVertices, self.nLoops, self.evenEdges)
        nEdges = nLoops + nVert - 1
        if evenEdges:
            # The sign is (induced sign on vertices) * (induced sign edge orientations)
            pp = [j+1 for j in p]
            sgn = Permutation(pp).signature()
            for (u, v) in G.edges(labels=False):
                # we assume the edge is always directed from the larger to smaller index
                if (u < v and p[u] > p[v]) or (u > v and p[u] < p[v]):
                    sgn *= -1
            return sgn
        else:
            # The sign is (induced sign of the edge permutation)
            # we assume the edges are always lex ordered
            # for the computation we use that G.edges() returns the edges in lex ordering

            # we first label the edges on a copy of G lexicographically
            G1 = copy(G)
            for (j,e) in enumerate(G1.edges(labels=False)):
                u,v = e
                G1.set_edge_label(u,v,j)

            # we permute the graph, and read of the new labels
            G1.relabel(p,inplace=True)
            pp = [j+1 for u,v,j in G1.edges()]
            return Permutation(pp).signature()

    def get_work_estimate(self):
        # give estimate of number of graphs
        nEdges = self.nLoops + self.nVertices - 1
        n = self.nVertices
        return binomial((n*(n-1))/2, nEdges) / factorial(n)


# -----  Contraction operator --------
class ContractGO(GraphOperator.GraphOperator):

    def __init__(self, nVertices, nLoops, evenEdges=True):

        directory = dataDirEven if evenEdges else dataDirOdd
        s = "contract%d_%d.txt" % (nVertices, nLoops)
        file_name = os.path.join(directory, s)

        domain = OrdinaryGVS(nVertices, nLoops, evenEdges=evenEdges)
        target = OrdinaryGVS(nVertices-1, nLoops, evenEdges=evenEdges)

        super(ContractGO, self).__init__(file_name, domain, target)

    def _operate_on(self,G):
        image=[]
        for (i, e) in enumerate(G.edges(labels=False)):
            u, v = e
            # permute u,v to position 0,1
            r = range(0,self.domain.nVertices)
            p = list(r)
            p[0] = u
            p[1] = v
            idx = 2
            for j in r:
                if j == u or j== v:
                    continue
                else:
                    p[idx] = j
                    idx +=1

            pp = [j-1 for j in (Permutation([j+1 for j in p]).inverse())]
            sgn = self.domain.perm_sign(G, pp)
            G1 = copy(G)
            G1.relabel(pp, inplace=True)

            for (j, ee) in enumerate(G1.edges(labels=False)):
                a, b = ee
                G1.set_edge_label(a,b,j)
            # now delete the first edge and join the vertices 0 and 1
            #print(G1.edges())
            G1.merge_vertices([0,1])
            #print(G1.edges())
            #print(G1.vertices())
            #G1.relabel(list(range(0,G1.order())), inplace = True)
            #print(G1.vertices())
            #print(G1.edges())
            if not self.domain.evenEdges:
                p = [j for (a, b, j) in G1.edges()]
                #print(p)
                #sgn *= Permutation(p).signature()

            image.append((G1, sgn))
        return image

    def get_work_estimate(self):
        # give estimate of number of graphs
        return self.domain.get_work_estimate() * self.domain.nEdges
