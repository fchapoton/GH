from abc import ABCMeta, abstractmethod
import logging
from sage.all import *
import StoreLoad as SL
import GraphComplex as GC


class RefVectorSpace:
    __metaclass__ = ABCMeta

    def __init__(self, vs):
        self.vs = vs
        self.basis_file_path = vs.get_ref_basis_file_path()

    def _load_basis_g6(self):
        if not self.exists_basis_file():
            raise SL.RefError("%s: Reference basis file not found" % str(self))
        logging.info("Load basis from reference file: %s" % str(self))
        return SL.load_string_list(self.basis_file_path)

    def __str__(self):
        return "Reference vector space: %s" % str(self.basis_file_path)

    def exists_basis_file(self):
        return (self.basis_file_path is not None) and os.path.isfile(self.basis_file_path)

    def _g6_to_canon_g6(self, graph6, sign=False):
        graph = Graph(graph6)
        if not sign:
            return graph.canonical_label().graph6_string()
        canonG, permDict = graph.canonical_label(certificate=True)
        sgn = self.vs.perm_sign(graph, permDict.values())
        return (canonG.graph6_string(), sgn)

    def get_basis_g6(self):
        basis_g6 = self._load_basis_g6()
        basis_g6_canon = []
        for G6 in basis_g6:
            basis_g6_canon.append(self._g6_to_canon_g6(G6))
        return basis_g6_canon

    def get_transformation_matrix(self):
        basis_g6 = self._load_basis_g6()
        dim = len(basis_g6)
        if not dim == self.vs.get_dimension():
            raise ValueError("Dimension of reference basis and basis not equal for %s" % str(self))
        T = matrix(ZZ, dim, dim, sparse=True)
        lookup = {G6: j for (j, G6) in enumerate(self.vs.get_basis(g6=True))}
        i = 0
        for G6 in basis_g6:
            (canonG6, sgn) = self._g6_to_canon_g6(G6, sign=True)
            j = lookup.get(canonG6)
            if j is None:
                raise ValueError("%s: Graph from ref basis not found in basis" % str(self))
            T.add_to_entry(i, j, sgn)
            i += 1
        if not T.is_invertible():
            raise ValueError("%s: Basis transformation matrix not invertible" % str(self))
        return T


class RefOperator:
    __metaclass__ = ABCMeta

    def __init__(self, op):
        self.op = op
        self.ref_domain = RefVectorSpace(self.op.domain)
        self.ref_target = RefVectorSpace(self.op.target)
        self.matrix_file_path = self.op.get_ref_matrix_file_path()
        self.rank_file_path = self.op.get_ref_rank_file_path()

    def _load_matrix(self):
        if not self.exists_matrix_file():
           raise SL.RefError("%s: Reference basis file not found" % str(self))
        logging.info("Load operator matrix from reference file: %s" % str(self.matrix_file_path))
        stringList = SL.load_string_list(self.matrix_file_path)
        entriesList = []
        if len(stringList) == 0:
            return ([], None)
        else:
            (m, n, t) = map(int, stringList.pop().split(" "))
            if t != 0:
                raise ValueError("End line in reference file %s is missing" % str(self))
            shape = (m, n)
            for line in stringList:
                (i, j, v) = map(int, line.split(" "))
                if i < 0 or j < 0:
                    raise ValueError("%s: Negative matrix index" % str(self))
                if i > m or j > n:
                    raise ValueError("%s Matrix index outside matrix size" % str(self))
                if i == 0 or j == 0:
                    continue
                entriesList.append((i - 1, j - 1, v))
        return (entriesList, shape)

    def __str__(self):
        return "Reference operator: %s" % str(self.matrix_file_path)

    def exists_matrix_file(self):
        return os.path.isfile(self.matrix_file_path)

    def exists_rank_file(self):
        return os.path.isfile(self.rank_file_path)

    def get_matrix_wrt_ref(self):
        (entriesList, shape) = self._load_matrix()
        if shape is None:
            (n, m) = self.op.get_matrix_shape()
        else:
            (m, n) = shape
        logging.info("Get reference operator matrix from file %s with shape (%d, %d)" % (str(self), m, n))
        M = matrix(ZZ, m, n, sparse=True)
        for (i, j, v) in entriesList:
            M.add_to_entry(i, j, v)
        return M.transpose()

    def get_rank(self):
        if not self.exists_rank_file():
           raise SL.RefError("%s: Reference rank file not found" % str(self))
        return int(SL.load_line(self.rank_file_path))

    def get_matrix(self, header=False):
        M = self.get_matrix_wrt_ref()
        T_domain = self.ref_domain.get_transformation_matrix()
        T_target = self.ref_target.get_transformation_matrix()
        (m, n) = (M.nrows(), M.ncols())
        if m == 0 or n == 0:
            return M
        return T_target.inverse() * M * T_domain


class RefGraphComplex:
    __metaclass__ = ABCMeta

    def __init__(self, gc):
        self.gc = gc
        self.ref_vs_list = [RefVectorSpace(vs) for vs in self.gc.vs_list]
        self.ref_op_list = [RefOperator(op) for op in self.gc.op_list]



