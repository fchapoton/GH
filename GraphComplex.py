from abc import ABCMeta, abstractmethod
import logging
import operator
import itertools
from joblib import Parallel, delayed
import multiprocessing
import os
import pandas
import webbrowser
from urllib import pathname2url
import StoreLoad as SL


class GraphComplex():
    __metaclass__ = ABCMeta

    def __init__(self, vs_list, op_list):
        self.vs_list = vs_list
        self.op_list = op_list
        manager = multiprocessing.Manager()
        self.vs_info_dict = manager.dict(dict())
        self.op_info_dict = manager.dict(dict())
        self.computing = manager.dict(dict())
        self.info_file_path = self.set_info_file_path()

    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def get_params_range(self):
        pass

    @abstractmethod
    def get_params_names(self):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def set_info_file_path(self):
        pass

    @abstractmethod
    def get_cohomology_plot_path(self):
        pass

    @abstractmethod
    def get_cohomology_dim(self):
        pass

    @abstractmethod
    def plot_cohomology_dim(self):
        pass

    def load_member_info(self):
        for vs in self.vs_list:
            self.vs_info_dict.update({vs.get_params(): vs.get_info()})
        for op in self.op_list:
            self.op_info_dict.update({op.get_params(): op.get_info()})

    def plot_member_info(self):
        vsList = []
        opList = []
        for key, value in self.vs_info_dict.items():
            vsList.append(list(key) + list(value))
        for key, value in self.op_info_dict.items():
                opList.append(list(key) + list(value))
        vsColumns = list(self.get_params_names()) + ['valid', 'dimension']
        opColumns = list(self.get_params_names()) + ['valid', 'shape', 'entries', 'rank']
        vsTable = pandas.DataFrame(data=vsList, columns=vsColumns)
        opTable = pandas.DataFrame(data=opList, columns=opColumns)
        vsTable.to_html('./plots/vs.html')
        opTable.to_html('./plots/op.html')
        url = 'file:{}'.format(pathname2url(os.path.abspath('./plots/vs.html')))
        webbrowser.open(url)

    def build_basis(self, ignore_existing_files=True, n_jobs=1):
        self.sort_vs()
        if n_jobs > 1:
            P = Parallel(n_jobs=n_jobs)
            P(delayed(self._build_single_basis)(vs, ignore_existing_file=ignore_existing_files)
              for vs in self.vs_list)
        else:
            for vs in self.vs_list:
                self._build_single_basis(vs, ignore_existing_file=ignore_existing_files)
        self.plot_member_info()

    def _build_single_basis(self, vs, ignore_existing_file=True):
        vs.build_basis(ignore_existing_file=ignore_existing_file)
        self.vs_info_dict.update({vs.get_params(): vs.get_info()})

    def build_operator_matrix(self, ignore_existing_files=True, n_jobs=1):
        self.sort_op()
        for op in self.op_list:
            op.build_matrix(ignore_existing_file=ignore_existing_files, n_jobs=n_jobs)
            self.op_info_dict.update({op.get_params(): op.get_info()})
        self.plot_member_info()

    def build(self, ignore_existing_files=True, n_jobs=1):
        self.build_basis(ignore_existing_files=ignore_existing_files, n_jobs=n_jobs)
        self.build_operator_matrix(ignore_existing_files=ignore_existing_files, n_jobs=n_jobs)

    def sort_vs(self, dimension=False):
        if dimension:
            self.vs_list.sort(key=operator.methodcaller('get_dimension'))
        else:
            self.vs_list.sort(key=operator.methodcaller('get_work_estimate'))

    def sort_op(self, entries=False):
        if entries:
            self.op_list.sort(key=operator.methodcaller('get_matrix_entries'))
        else:
            self.op_list.sort(key=operator.methodcaller('get_work_estimate'))

    def square_zero_test(self, eps):
        succ = []  # holds pairs for which test was successful
        fail = []  # failed pairs
        triv = []  # pairs for which test trivially succeeded because at least one operator is the empty matrix
        inc = []  # pairs for which operator matrices are missing
        for (op1, op2) in itertools.product(self.op_list, self.op_list):
            if op2.matches(op1):
                # A composable pair is found
                p = (op1, op2)
                if not (op1.valid and op2.valid):
                    triv.append(p)
                    continue
                try:
                    M1 = op1.get_matrix()
                    M2 = op2.get_matrix()
                except SL.FileNotFoundError:
                    logging.warn("Cannot test square zero: "
                                 "Operator matrix not built for %s or %s" % (str(op1), str(op2)))
                    inc.append(p)
                    continue
                if op1.is_trivial() or op2.is_trivial():
                    triv.append(p)
                    continue
                if sum(map(abs, (M2 * M1).list())) < eps:
                    succ.append(p)
                else:
                    fail.append(p)
        (triv_l, succ_l, inc_l, fail_l) = (len(triv), len(succ), len(inc), len(fail))
        logging.warn("Square zero test for %s: trivial success: "
                     "%d, success: %d, inconclusive: %d, failed: %d pairs" % (str(self), triv_l, succ_l, inc_l, fail_l ))
        if inc_l:
            logging.warn("Square zero test for %s: inconclusive: %d paris" % (str(self), inc_l))
        for (op1, op2) in fail:
            logging.error("Square zero test for %s: failed for the pair %s, %s" % (str(self), str(op1), str(op2)))
        return (triv_l, succ_l, inc_l, fail_l)

    def compute_ranks(self, ignore_existing_files=True, n_jobs=1):
        self.sort_op(entries=True)
        if n_jobs > 1:
            P = Parallel(n_jobs=n_jobs)
            P(delayed(self._compute_single_rank)(op, ignore_existing_file=ignore_existing_files)
              for op in self.op_list)
        else:
            for op in self.op_list:
                self._compute_single_rank(op,  ignore_existing_file=ignore_existing_files)
        self.plot_member_info()

    def _compute_single_rank(self, op, ignore_existing_file=True):
        op.compute_rank(ignore_existing_file=ignore_existing_file)
        self.op_info_dict.update({op.get_params(): op.get_info()})

    #Computes the cohomology, i.e., ker(D)/im(DD)
    def get_general_cohomology_dim_dict(self):
        cohomology_dim = dict()
        for (opD, opDD) in itertools.product(self.op_list, self.op_list):
            if opD.matches(opDD):
                dim = opD.cohomology_dim(opDD)
                cohomology_dim.update({opD.domain: dim})
        return cohomology_dim

    def get_cohomology_info(self, cohomology_dim=None):
        if cohomology_dim is None:
            return []
        cohomologyList = []
        for vs in self.vs_list:
            dim = cohomology_dim.get(vs)
            if dim is not None:
                line = "%s: %s" % (str(vs), str(dim))
                cohomologyList.append(line)
        return cohomologyList
