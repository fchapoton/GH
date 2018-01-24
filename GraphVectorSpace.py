from abc import ABCMeta, abstractmethod
import os
import logging
from sage.all import *
import Shared as SH

reload(SH)


class GraphVectorSpace():
    __metaclass__ = ABCMeta

    def __init__(self, color_counts=None):
        self.color_counts = color_counts
        self.valid = self._set_validity()
        self.basis_file_path = self._set_basis_file_path()
        self.img_path = self._set_img_path()

    @abstractmethod
    def _set_basis_file_path(self):
        pass

    @abstractmethod
    def _set_img_path(self):
        pass

    @abstractmethod
    def get_ref_basis_file_path(self):
        pass

    @abstractmethod
    def _set_validity(self,):
        pass

    @abstractmethod
    def get_work_estimate(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def _generating_graphs(self):
        pass

    @abstractmethod
    def perm_sign(self, G, p):
        pass

    def get_info(self):
        validity = "valid" if self.valid else "not valid"
        built = "basis built" if self.exists_basis_file() else "basis not built"
        dim = "dimension unknown"
        if self.exists_basis_file():
            dim = "dimension = %d" % self.get_dimension()
        return "%s, %s" % (validity, dim)

    def graph_to_canon_g6(self, graph):
        canonG, permDict = graph.canonical_label(certificate=True)
        sign = self.perm_sign(graph, permDict.values())
        return (canonG.graph6_string(), sign)

    def build_basis(self):
        if not self.valid:
            logging.info("Skip building basis: %s is not valid" % str(self))
            return
        if self.exists_basis_file():
            return
        generatingList = self._generating_graphs()
        basisSet = set()
        for G in generatingList:
            canonG = G.canonical_label()
            automList = G.automorphism_group().gens()
            if len(automList):
                canon6=canonG.graph6_string()
                if not canon6 in basisSet:
                    if not self._has_odd_automorphisms(G, automList):
                        basisSet.add(canon6)
        self._store_basis_g6(list(basisSet))
        logging.info("Basis built for %s" % str(self))

    def _has_odd_automorphisms(self, G, automList):
        for g in automList:
            if self.perm_sign(G, g.tuple()) == -1:
               return True
        return False

    def exists_basis_file(self):
        return os.path.isfile(self.basis_file_path)

    def get_dimension(self):
        if not self.valid:
            return 0
        try:
            header = SH.load_line(self.basis_file_path)
        except SH.FileNotExistingError:
            raise SH.NotBuiltError("Cannot load header from file %s: Build basis first" % str(self.basis_file_path))
        return int(header)

    def _store_basis_g6(self, basisList):
        logging.info("Store basis in file: %s" % str(self.basis_file_path))
        basisList.insert(0, str(len(basisList)))
        SH.store_string_list(basisList, self.basis_file_path)

    def _load_basis_g6(self):
        if not self.exists_basis_file():
            raise SH.NotBuiltError("Cannot load basis, No Basis file found for %s: " % str(self))
        logging.info("Load basis from file: %s" % str(self.basis_file_path))
        basisList = SH.load_string_list(self.basis_file_path)
        dim = int(basisList.pop(0))
        if len(basisList) != dim:
            raise ValueError("Basis read from file %s has wrong dimension" % str(self.basis_file_path))
        return basisList

    def get_basis(self, g6=True):
        if not self.valid:
            logging.warn("Empty basis: %s is not valid" % str(self))
            return []
        basis_g6 = self._load_basis_g6()
        logging.info("Get basis of %s with dimension %d" % (str(self), len(basis_g6)))
        if g6:
            return basis_g6
        else:
            basis = []
            for G in basis_g6:
                basis.append(Graph(G))
            return basis

    def delete_basis_file(self):
        if os.path.isfile(self.basis_file_path):
            os.remove(self.basis_file_path)

    def create_graph_images(self, graph6_list):
        SH.generate_path(self.img_path)
        for g6 in graph6_list:
            path = os.path.join(self.img_path, g6 + '.png')
            Graph(g6).plot().show()