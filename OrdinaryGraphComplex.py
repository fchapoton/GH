import os
import itertools
import operator
import logging
from sage.all import *
import GraphVectorSpace as GVS
import GraphOperator as GO
import GraphComplex as GC
import RefData as RF
import Shared as SH

reload(GVS)
reload(GO)
reload(GC)
reload(RF)
reload(SH)

data_dir = "data"
data_ref_dir = "data_ref"
type_dir = "ordinary"
sub_dir_odd = "oddedge"
sub_dir_even = "evenedge"
image_directory = "img"


class OrdinaryGVS(GVS.GraphVectorSpace):

    def __init__(self, n_vertices, n_loops, even_edges):
        self.n_vertices = n_vertices
        self.n_loops = n_loops
        self.even_edges = even_edges
        self.n_edges = self.n_loops + self.n_vertices - 1
        super(OrdinaryGVS,self).__init__()

    def _set_file_path(self):
        s1 = sub_dir_even if self.even_edges else sub_dir_odd
        s2 = "gra%d_%d.g6" % (self.n_vertices, self.n_loops)
        return os.path.join(data_dir, type_dir, s1, s2)

    def get_file_path_ref(self):
        s1 = sub_dir_even if self.even_edges else sub_dir_odd
        s2 = "gra%d_%d.g6" % (self.n_vertices, self.n_loops)
        return os.path.join(data_ref_dir, type_dir, s1, s2)

    def _set_validity(self):
        return (3 * self.n_vertices <= 2 * self.n_edges) and self.n_vertices > 0 and self.n_loops >= 0 and self.n_edges <= self.n_vertices * (self.n_vertices - 1) / 2

    def get_work_estimate(self):
        return binomial((self.n_vertices * (self.n_vertices - 1)) / 2, self.n_edges) / factorial(self.n_vertices)

    def __str__(self):
        return "<Ordinary graphs: %d vertices, %d loops, %s>" % (self.n_vertices, self.n_loops, "even edges" if self.even_edges else "odd edges")

    def __eq__(self, other):
        return self.n_vertices == other.n_vertices and self.n_loops == other.n_loops and self.even_edges == other.even_edges

    def _generating_graphs(self, onlyonevi=True):
        if (3 * self.n_vertices > 2 * self.n_edges) or (self.n_edges > self.n_vertices * (self.n_vertices - 1) / 2):
            # impossible
            return []
        return list(graphs.nauty_geng(("-Cd3" if onlyonevi else "-cd3") + " %d %d:%d" % (self.n_vertices, self.n_edges, self.n_edges)))

    def perm_sign(self, G, p):
        if self.even_edges:
            # The sign is (induced sign on vertices) * (induced sign edge orientations)
            sgn = SH.Perm(p).sign()
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
                (u, v) = e
                G1.set_edge_label(u, v, j)

            # we permute the graph, and read of the new labels
            G1.relabel(p, inplace=True)
            return SH.Perm([j for (u, v, j) in G1.edges()]).sign()


# -----  Contraction operator --------
class ContractGO(GO.GraphOperator):

    def __init__(self, domain, target):
        if domain.n_vertices != target.n_vertices+1 or domain.n_loops != target.n_loops or domain.even_edges != target.even_edges:
            raise ValueError("Domain and target not consistent for contract edge operator")
        super(ContractGO, self).__init__(domain, target)

    @classmethod
    def generate_operators(cls, vs_list):
        return ContractGO.get_operators(cls, vs_list)

    @classmethod
    def get_operator(cls, n_vertices, n_loops, even_edges):
        domain = OrdinaryGVS(n_vertices, n_loops, even_edges)
        target = OrdinaryGVS(n_vertices-1, n_loops, even_edges)
        return cls(domain, target)

    def _set_file_path(self):
        s1 = sub_dir_even if self.domain.even_edges else sub_dir_odd
        s2 = "contractD%d_%d.txt" % (self.domain.n_vertices, self.domain.n_loops)
        return os.path.join(data_dir, type_dir, s1, s2)

    def get_file_path_ref(self):
        s1 = sub_dir_even if self.domain.even_edges else sub_dir_odd
        s2 = "contractD%d_%d.txt" % (self.domain.n_vertices, self.domain.n_loops)
        return os.path.join(data_ref_dir, type_dir, s1, s2)

    def get_work_estimate(self):
        return self.domain.n_edges * sqrt(self.target.get_dimension())

    def __str__(self):
        return "<Contract edges: domain: %s>" % str(self.domain)

    def _operate_on(self,G):
        image=[]
        for (i, e) in enumerate(G.edges(labels=False)):
            (u, v) = e
            r = range(0,self.domain.n_vertices)
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

            pp = SH.Perm(p).inverse()
            sgn = self.domain.perm_sign(G, pp)
            G1 = copy(G)
            G1.relabel(pp, inplace=True)

            for (j, ee) in enumerate(G1.edges(labels=False)):
                a, b = ee
                G1.set_edge_label(a,b,j)
            previous_size = G1.size()
            G1.merge_vertices([0,1])
            if (previous_size - G1.size()) != 1:
                continue
            G1.relabel(list(range(0,G1.order())), inplace = True)
            if not self.domain.even_edges:
                p = [j for (a, b, j) in G1.edges()]
                sgn *= Permutation(p).signature()
            image.append((G1, sgn))
        return image


# ----- Ordinary Graph Complex --------
class OrdinaryGC(GC.GraphComplex):
    def __init__(self, v_range, l_range, even_edges):
        self.v_range = v_range
        self.l_range = l_range
        self.even_edges = even_edges
        super(OrdinaryGC, self).__init__()

    def __str__(self):
        return "<Ordinary graph complex with %s and parameter range: vertices: %s, loops: %s>" % ("even edges" if self.even_edges else "odd edges", str(self.v_range), str(self.l_range))

    def _set_file_path(self):
        s1 = sub_dir_even if self.even_edges else sub_dir_odd
        s2 = "graph_complex.txt"
        return SH.get_path_from_current(data_dir, type_dir, s1, s2)

    def create_vs(self):
        self.vs_list = [OrdinaryGVS(v, l, self.even_edges) for (v, l) in itertools.product(self.v_range, self.l_range)]

    def create_op(self):
        self.op_list = ContractGO.generate_operators(self.vs_list)


# ----- Reference Data Handler --------
class OrdinaryRefVS(RF.RefVectorSpace):

    def _load_basis_g6(self, header):
        basis_g6 = SH.load_string_list(self.file_path_ref, header=header)
        return basis_g6


class OrdinaryRefOP(RF.RefOperator):

    def _load_matrix(self, header):
        shape = None
        matrixList = SH.load_string_list(self.file_path_ref, header=header)
        row = []
        column = []
        data = []
        if matrixList is []:
            shape = (0,0)
        else:
            for line in matrixList:
                (i, j, v) = map(int, line.split(" "))
                row.append(i-1)
                column.append(j-1)
                data.append(v)
            if data[-1] == 0:
                shape = (m, n) = (row.pop(-1)+1, column.pop(-1)+1)
                data.pop(-1)
                if len(row):
                    if min(row) < 0 or min(column) < 0:
                        raise ValueError("%s: Found negative matrix indices: %d %d" % (str(self), min(row), min(column)))
                    if max(row) >= m or max(column) >= n:
                        raise ValueError("Matrix read from reference file %s is wrong: Index outside matrix size" % str(self))
        if shape is None:
            raise ValueError("%s: Shape of reference matrix is unknown" % str(self))
        return ((data, (row, column)), shape)
