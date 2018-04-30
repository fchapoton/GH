import itertools
import StoreLoad as SL
import Shared as SH
import Parameters
import Log

logger = Log.logger.getChild('graph_complex')


class GraphComplex(object):
    def __init__(self, vector_space, operator_collection_list):
        self.vector_space = vector_space
        self.operator_collection_list = operator_collection_list

    def get_vector_space(self):
        return self.vector_space

    def get_differential_list(self):
        return self.operator_collection_list

    def build_basis(self, ignore_existing_files=True, n_jobs=1, progress_bar=False, info_tracker=False):
        self.vector_space.build_basis(ignore_existing_files=ignore_existing_files, n_jobs=n_jobs,
                                      progress_bar=progress_bar, info_tracker=info_tracker)

    def build_matrix(self, ignore_existing_files=True, n_jobs=1, progress_bar=False, info_tracker=False):
        for dif in self.operator_collection_list:
            dif.build_matrix(ignore_existing_files=ignore_existing_files, n_jobs=n_jobs, progress_bar=progress_bar,
                             info_tracker=info_tracker)

    def square_zero_test(self):
        for dif in self.operator_collection_list:
            dif.square_zero_test()

    def compute_rank(self, exact=False, n_primes=1, estimate=False, ignore_existing_files=True, n_jobs=1,
                     info_tracker=False):
        for dif in self.operator_collection_list:
            dif.compute_rank(exact=exact, n_primes=n_primes, estimate=estimate,
                             ignore_existing_files=ignore_existing_files, n_jobs=n_jobs, info_tracker=info_tracker)

    def plot_cohomology_dim(self):
        for dif in self.operator_collection_list:
            ordered_param_range_dict = self.vector_space.get_ordered_param_range_dict()
            dif.plot_cohomology_dim(ordered_param_range_dict)

    def test_pairwise_commutativity(self):
        for (op_collection1, op_collection2) in itertools.combinations(self.operator_collection_list, 2):
            self.test_commutativity(op_collection1, op_collection2)

    def test_commutativity(self, op_collection1, op_collection2, anti_commute=False, eps=Parameters.commute_test_eps):
        print('Test commutativity for %s and %s' % (str(op_collection1), str(op_collection2)))
        succ = []  # holds pairs for which test was successful
        fail = []  # failed pairs
        triv = []  # pairs for which test trivially succeeded because at least one operator is the empty matrix
        inc = []  # pairs for which operator matrices are missing

        op_list1 = op_collection1.get_op_list()
        op_list2 = op_collection2.get_op_list()
        for (op1a, op2a) in itertools.product(op_list1, op_list2):
            if op1a.get_domain() == op2a.get_domain():
                for op1b in op_list1:
                    if op1b.get_domain() == op2a.get_target():
                        for op2b in op_list2:
                            if op2b.get_domain() == op1a.get_target() and op1b.get_target() == op2b.get_target():
                                p = (op1a, op1b, op2a, op2b)

                                if not((op1a.is_valid() and op2b.is_valid()) or (op2a.is_valid() and op2b.is_valid())):
                                    triv.append(p)
                                    continue

                                if op1a.is_valid() and op2b.is_valid() and (not (op2a.is_valid() and op1b.is_valid())):
                                    try:
                                        if op1a.is_trivial() or op2b.is_trivial():
                                            triv.append(p)
                                            continue
                                        M1a = op1a.get_matrix()
                                        M2b = op2b.get_matrix()
                                    except SL.FileNotFoundError:
                                        inc.append(p)
                                        continue
                                    if SH.matrix_norm(M2b * M1a) < eps:
                                        succ.append(p)
                                        continue
                                    fail.append(p)
                                    continue

                                if (not (op1a.is_valid() and op2b.is_valid())) and op2a.is_valid() and op1b.is_valid():
                                    try:
                                        if op1b.is_trivial() or op2a.is_trivial():
                                            triv.append(p)
                                            continue
                                        M1b = op1b.get_matrix()
                                        M2a = op2a.get_matrix()
                                    except SL.FileNotFoundError:
                                        inc.append(p)
                                        continue
                                    if SH.matrix_norm(M1b * M2a) < eps:
                                        succ.append(p)
                                        continue
                                    fail.append(p)
                                    continue

                                try:
                                    if (op1a.is_trivial() or op2b.is_trivial()) and (op2a.is_trivial() or op1b.is_trivial()):
                                        triv.append(p)
                                        continue
                                    if (not (op1a.is_trivial() or op2b.is_trivial())) and (op2a.is_trivial() or op1b.is_trivial()):
                                        M1a = op1a.get_matrix()
                                        M2b = op2b.get_matrix()
                                        if SH.matrix_norm(M2b * M1a) < eps:
                                            succ.append(p)
                                            continue
                                    if (op1a.is_trivial() or op2b.is_trivial()) and (not (op2a.is_trivial() or op1b.is_trivial())):
                                        M1b = op1b.get_matrix()
                                        M2a = op2a.get_matrix()
                                        if SH.matrix_norm(M1b * M2a) < eps:
                                            succ.append(p)
                                            continue
                                    M1a = op1a.get_matrix()
                                    M2b = op2b.get_matrix()
                                    M1b = op1b.get_matrix()
                                    M2a = op2a.get_matrix()
                                    if SH.matrix_norm(M2b * M1a + (1 if anti_commute else -1) * M1b * M2a) < eps:
                                        succ.append(p)
                                except SL.FileNotFoundError:
                                    inc.append(p)
                                    continue

        (triv_l, succ_l, inc_l, fail_l) = (len(triv), len(succ), len(inc), len(fail))
        print("trivial success: %d, success: %d, inconclusive: %d, failed: %d pairs" % (triv_l, succ_l, inc_l, fail_l))
        if inc_l:
            logger.warn("Commutation test for %s: inconclusive: %d paris" % (str(self), inc_l))
        for (op1, op2) in fail:
            logger.error("Commutation test for %s: failed for the pair %s, %s" % (str(self), str(op1), str(op2)))
        return (triv_l, succ_l, inc_l, fail_l)
