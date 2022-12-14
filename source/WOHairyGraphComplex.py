"""Graph complexes based on simple graphs with numbered hairs and hairs of two (omega- and epsilon-)decorations 
as in the graph complex computing weight 11 cohomology.

The omega decorations are considered odd !!!!

Implemented Differentials: Contract edges, make eps vertex to omega vertex.


Graphs are realized as simple graphs with 1+w extra vertices for epsilon and omega, (index self.n_vertices and self.n_vertices+1,2,...,w).
WARNING: If there is an eps-eps tadpole the corresponding loop is not part of the graph--one can determine the presence of the tadpole
from the overall one too small loop number.
There must not be tadpoles at internal vertices
TODO: Take care that this does not produce problems
"""


# __all__ = ['WOHairyGraphVS', 'WOHairyGraphSumVS', 'ContractEdgesGO', 'ContractEdgesD',
#            'RestrictedContractEdgesGO', 'RestrictedContractEdgesD',
#            'SymmProjector', 'WOHairyGC']

import itertools
from sage.all import *
import GraphVectorSpace
import GraphOperator
import GraphComplex
import Shared
import NautyInterface
import OrdinaryGraphComplex
import StoreLoad
import Parameters
import SymmetricGraphComplex
import GCDimensions
import inspect
from sage.combinat.shuffle import ShuffleProduct

graph_type = "wohairy"


def dump_args(func):
    """
    Decorator to print function call details.

    This includes parameters names and effective values.
    """

    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(
            map("{0[0]} = {0[1]!r}".format, func_args.items()))
        print(f"{func.__module__}.{func.__qualname__} ( {func_args_str} )")
        return func(*args, **kwargs)

    return wrapper

# ------- Graph Vector Space --------


class WOHairyGraphVS(SymmetricGraphComplex.SymmetricGraphVectorSpace):
    """WOHairy graph vector space.

    Sub vector space with specified number of (internal) vertices, loops, numbered hairs, and omega decorations (ws)
    and at least trivalent vertices. One hair is composed of a hair vertex and an edge connecting it to a vertex.

    Attributes:
        - n_vertices (int): Number of internal vertices.
        - n_loops (int): Number of loops.
        - n_hairs (int): Number of hairs.
        - n_edges (int): Number of edges, not counting edges to numbered hairs.
        - sub_type (str): Sub type of graphs. This is currently not used, but might be needed for an extension later.
        - ogvs (OrdinaryGraphComplex.OrdinaryGVS): Ordinary graph vector space without hairs.

    """

    def __init__(self, n_vertices, n_loops, n_hairs, n_ws):
        """Initialize the hairy graph vector space.

        :param n_vertices: Number of internal vertices.
        :type n_vertices: int
        :param n_loops: the genus of the graph. Warning: this is counted without the special vertex.... e.g., in weight 11 the actual genus is one more
        :type n_loops: int
        :param n_hairs: Number of hairs. They are distinguishable, numbered 1,...,n
        :type n_hairs: int
        :param n_ws: Number of omega decorated hairs.
        :type even_edges: int
        """
        self.n_vertices = n_vertices
        self.n_loops = n_loops
        self.n_hairs = n_hairs
        self.n_ws = n_ws
        # we count only the internal edges and omega and eps edges, but not the hair edges
        self.n_edges = self.n_loops + self.n_vertices
        self.sub_type = ""
        super(WOHairyGraphVS, self).__init__()
        self.ogvs = OrdinaryGraphComplex.OrdinaryGVS(
            self.n_vertices + self.n_hairs+1+self.n_ws, self.n_loops, False)

    def get_type(self):
        return graph_type

    def __eq__(self, other):
        return self.n_vertices == other.n_vertices and self.n_loops == other.n_loops and self.n_hairs == other.n_hairs and self.n_ws == other.n_ws

    def __hash__(self):
        return hash("wogra%d_%d_%d_%d" % self.get_ordered_param_dict().get_value_tuple())

    def get_basis_file_path(self):
        s = "wogra%d_%d_%d_%d.g6" % self.get_ordered_param_dict().get_value_tuple()
        return os.path.join(Parameters.data_dir, graph_type, s)

    def get_ref_basis_file_path(self):
        s = "wogra%d_%d_%d_%d.g6" % self.get_ordered_param_dict().get_value_tuple()
        return os.path.join(Parameters.ref_data_dir, graph_type, s)

    def get_ordered_param_dict(self):
        return Shared.OrderedDict([('vertices', self.n_vertices), ('loops', self.n_loops), ('hairs', self.n_hairs), ('ws', self.n_ws)])

    def get_partition(self):
        # All internal vertices are in color 1, the single eps vertex in color 2, the w vertex in color 3
        # and the hair vertices are in colors 4,...,n+3.
        return [list(range(0, self.n_vertices))] + [[self.n_vertices]] + [list(range(self.n_vertices+1, self.n_vertices+1+self.n_ws))] + [[j] for j in range(self.n_vertices+1+self.n_ws, self.n_vertices + self.n_hairs+self.n_ws+1)]

    def plot_graph(self, G):
        GG = Graph(G, loops=True)
        # add proper tadpole if needed
        if GG.size() < self.n_edges + self.n_hairs:
            GG.add_edge(self.n_vertices, self.n_vertices)

        return GG.plot(partition=self.get_partition(), vertex_labels=True)

    def is_valid(self):
        # At least trivalent internal vertices.
        l = (3 * self.n_vertices + self.n_ws <=
             2 * self.n_edges + self.n_hairs)
        # Nonnegative number of vertices, non negative number of loops, non-negative number of hairs,
        l = l and self.n_vertices >= 0 and self.n_loops >= 0 and self.n_hairs >= 0 and self.n_edges >= 0
        # At most a full graph.
        # l = l and self.n_edges <= (
        #     self.n_vertices+2) * (self.n_vertices + 1) / 2
        return l

    def get_work_estimate(self):
        # TODO
        # Returns the number of possible graphs as work estimate.
        if not self.is_valid():
            return 0
        return GCDimensions.get_wrhairy_dim_estimate(self.n_vertices, self.n_loops, self.n_hairs, self.n_ws)
        # return binomial((self.n_vertices * (self.n_vertices - 1)) / 2, self.n_edges) * (self.n_vertices ** self.n_hairs) / factorial(self.n_vertices)

    @dump_args
    def get_hairy_graphs_no_hair_edge(self, nvertices, nloops, nhairs):
        """ Produces all possibly disconnected hairy graphs with nhairs hairs, that are the last vertices in the ordering.
        Graphs can have multiple hairs, but not tadpoles or multiple edges.
        Also (!!!): The graphs cannot have edges connecting two hairs, i.e., connected components without (internal) vertex
        """
        # Idea: produce all bipartite graphs, the second color being either of degree 1 or 2.
        # Degree 1 vertices are hairs, degree 2 vertices are edges and are removed later.
        nedges = nloops + nvertices - 1  # number of internal edges
        n_vertices_1 = nvertices
        n_vertices_2 = nhairs + nedges
        n_edges_bip = nhairs + 2 * nedges
        deg_range_1 = (3, n_edges_bip + 1)
        deg_range_2 = (1, 2)

        # check if valid
        if (nvertices >= 1 and nedges >= 0 and nhairs >= 0 and n_edges_bip >= n_vertices_2
            and n_edges_bip <= 2*n_vertices_2 and n_edges_bip >= 3 * n_vertices_1
                and n_edges_bip <= n_vertices_1 * n_vertices_2):
            bipartite_graphs = NautyInterface.list_bipartite_graphs_disc(
                n_vertices_1, n_vertices_2, deg_range_1, deg_range_2, n_edges_bip, 1)

            for G in bipartite_graphs:
                yield self._bip_to_ordinary(G, nvertices, nedges, nhairs)

    @dump_args
    def get_hairy_graphs_with_hair_edges(self, nvertices, nloops, nhairs):
        """ Same as before, but graphs can contaîn edges between hairs"""
        count = 0
        nedges = nloops + nvertices - 1
        max_hairedges = min(nhairs // 2, nedges)
        for n_hairedges in range(0, max_hairedges+1):
            for G in self.get_hairy_graphs_no_hair_edge(nvertices, nloops-n_hairedges, nhairs-2*n_hairedges):
                # add n_hairedges hair edges
                nverts = nvertices + nhairs-2*n_hairedges
                for j in range(n_hairedges):
                    G.add_vertex(nverts + 2*j)
                    G.add_vertex(nverts + 2*j+1)
                    G.add_edge(nverts + 2*j, nverts + 2*j+1)
                print("hairy", count)
                count += 1
                yield G

    def get_generating_graphs(self):
        """
        Produces a list of generating graphs
        """
        nvertices = self.n_vertices
        nloops = self.n_loops
        nhairs = self.n_hairs
        nws = self.n_ws

        count = 0
        # we have to have at least one eps or w
        mineps = 1 if nws == 0 else 0
        maxeps = nloops - nws + nvertices
        # print(maxeps)
        for neps in range(mineps, maxeps+1):
            # Produce all permutations of the hairs
            vlist = list(range(0, nvertices))
            all_perm = [vlist + list(p)
                        for hs in itertools.permutations(range(nvertices+neps+nws, nvertices+nhairs+neps+nws))
                        for pp in ShuffleProduct(range(nvertices, nvertices+neps), range(nvertices+neps, nvertices+neps+nws))
                        for p in ShuffleProduct(hs, pp)]
            print(len(all_perm))
            for G in self.get_hairy_graphs_with_hair_edges(nvertices, nloops-nws-neps+1, nhairs+nws+neps):
                for p in all_perm:
                    print("gengr", count, len(all_perm), neps, maxeps)
                    count += 1
                    GGG = G.relabel(p, inplace=False)
                    # check for connectivity
                    GG = copy(GGG)
                    GG.merge_vertices(
                        list(range(nvertices, nvertices+neps+nws)))
                    if GG.is_connected():
                        # merge eps vertices into one
                        tadpole_flag = 0
                        if neps > 0:
                            vertstomerge = list(
                                range(nvertices, nvertices+neps))
                            # check whether merge produces tadpole
                            tadpole_flag = sum(
                                1 for v1 in vertstomerge for v2 in vertstomerge if GGG.has_edge((v1, v2)))
                            if tadpole_flag > 1:
                                continue
                            GGG.merge_vertices(vertstomerge)
                            GGG.relabel(list(range(nvertices+nws+nhairs+1)))
                        else:
                            # add one empty vertex for eps
                            GGG.relabel(
                                list(range(nvertices)) + list(range(nvertices+1, nvertices+nws+nhairs+1)))
                            GGG.add_vertex(nvertices)
                        # check whether graph is admissible...
                        if G.size() - GGG.size() == tadpole_flag:
                            # no edges were removed in the merge
                            yield GGG

    # def get_generating_graphs(self):
    #     # The routines above produce all wgraphs, we just have to permute the hair labels

    #     # Produce all permutations of the hairs
    #     all_perm = [list(range(0, self.n_vertices+2)) + list(p)
    #                 for p in itertools.permutations(range(self.n_vertices+2, self.n_vertices+self.n_hairs+2))]

    #     return (G.relabel(p, inplace=False) for G in self._get_all_wgraphs(self.n_vertices, self.n_loops, self.n_hairs, self.n_ws)
    #             for p in all_perm)

    def perm_sign(self, G, p):
        # The sign is the same as the corresponding sign in the
        # ordinary graph complex, apart from an extra contribution from the omega-vertices.
        sgn = self.ogvs.perm_sign(G, p)

        # Compute the extra contribution from omegas.
        # if self.even_hairs == self.even_edges:
        if self.n_ws > 0:
            wperm = p[self.n_vertices+1:]
            if len(wperm) != 0:
                sgn *= Shared.Perm.shifted(wperm).signature()
        return sgn

    def _bip_to_ordinary(self, G, nvertices, nedges, nhairs):
        # Translates bipartite into ordinary graph by replacing a bivalent vertex of colour 2 with an edge.
        for v in range(nvertices, nvertices + nhairs + nedges):
            neighbors = G.neighbors(v)
            n_l = len(neighbors)
            if n_l == 1:  # hair
                continue
            elif n_l == 2:  # edge
                G.add_edge(neighbors)
                G.delete_vertex(v)
            else:
                raise ValueError(
                    '%s: Vertices of second colour should have 1 or 2 neighbours' % str(self))
        G.relabel(range(0, G.order()))
        return G

    def get_n(self):
        return self.n_hairs

    def vertex_permutation_from_permutation(self, p):
        return list(range(0, self.n_vertices+2)) + [j+self.n_vertices+1 for j in p]

    def get_isotypical_projector(self, rep_index):
        return SymmProjector(self, rep_index)


class WOHairyGraphSumVS(GraphVectorSpace.SumVectorSpace):
    """Direct sum of hairy graph vector spaces with specified number of omega hairs.

    Attributes:
        - v_range (range): Range for the number of vertices.
        - l_range (range): Range for the number of loops.
        - h_range (range): Range for the number of hairs.
        - w_range (range): number of omega hairs
        - sub_type (str): Sub type of graphs.
    """

    def __init__(self, v_range, l_range, h_range, w_range):
        """Initialize the sum vector space.

        :param v_range: Range for the number of vertices.
        :type v_range: range
        :param l_range: Range for the number of loops.
        :type l_range: range
        :param h_range: Range for the number of hairs.
        :type h_range: range
        :param even_edges: True for even edges, False for odd edges.
        :type even_edges: bool
        :param even_hairs: True for even hairs, False for odd hairs.
        :type even_hairs: bool
        """
        self.v_range = v_range
        self.l_range = l_range
        self.h_range = h_range
        self.w_range = w_range
        self.sub_type = ""

        vs_list = [WOHairyGraphVS(v, l, h, w) for
                   (v, l, h, w) in itertools.product(self.v_range, self.l_range, self.h_range, self.w_range)]
        super(WOHairyGraphSumVS, self).__init__(vs_list)

    def get_type(self):
        return 'wohairy graphs'

    def get_ordered_param_range_dict(self):
        return Shared.OrderedDict([('vertices', self.v_range), ('loops', self.l_range), ('hairs', self.h_range), ('ws', self.w_range)])

    def get_info_plot_path(self):
        s = "info_vector_space_%s" % graph_type
        return os.path.join(Parameters.plots_dir, graph_type, self.sub_type, s)


# ------- Operators --------
class ContractEdgesGO(SymmetricGraphComplex.SymmetricGraphOperator):
    """Contract edges graph operator.

    Operate on a w-hairy graph by contracting an edge not connected to a hair vertex and unifying the two adjacent vertices.

    Attributes:
        - sub_type (str): Graphs sub type of the domain.
    """

    def __init__(self, domain, target):
        """Initialize the domain and target vector space of the contract edges graph operator.

        :param domain: Domain vector space of the operator.
        :type domain: HairyGraphVS
        :param target: Target vector space of the operator.
        :type target: HairyGraphVS
        """
        self.sub_type = domain.sub_type
        super(ContractEdgesGO, self).__init__(domain, target)

    @staticmethod
    def is_match(domain, target):
        """Check whether domain and target match to generate a corresponding contract edges graph operator.

        The contract edges operator reduces the number of vertices by one.

        :param domain: Potential domain vector space of the operator.
        :type domain: HairyGraphVS
        :param target: Potential target vector space of the operator.
        :type target: HairyGraphVS
        :return: True if domain and target match to generate a corresponding contract edges graph operator.
        :rtype: bool
        """
        return domain.n_vertices == target.n_vertices + 1 and domain.n_loops == target.n_loops \
            and domain.n_hairs == target.n_hairs and domain.n_ws == target.n_ws

    @classmethod
    def generate_operator(cls, n_vertices, n_loops, n_hairs, n_ws):
        """Return a contract edges graph operator.

        :param n_vertices: Number of vertices of the domain.
        :type n_vertices: int
        :param n_loops: Number of loops of the domain.
        :type n_loops: int
        :param n_hairs: Number of (numbered) hairs.
        :type n_hairs: int
        :param n_ws: Number of omega hairs.
        :type n_ws: int
        :return: Contract edges graph operator based on the specified domain vector space.
        :rtype: ContractEdgesGO
        """
        domain = WOHairyGraphVS(n_vertices, n_loops, n_hairs, n_ws)
        target = WOHairyGraphVS(n_vertices - 1, n_loops, n_hairs, n_ws)
        return cls(domain, target)

    def get_matrix_file_path(self):
        s = "contractD%d_%d_%d_%d.txt" % self.domain.get_ordered_param_dict().get_value_tuple()
        return os.path.join(Parameters.data_dir, graph_type, self.sub_type, s)

    def get_rank_file_path(self):
        s = "contractD%d_%d_%d_%d_rank.txt" % self.domain.get_ordered_param_dict().get_value_tuple()
        return os.path.join(Parameters.data_dir, graph_type, self.sub_type, s)

    def get_ref_matrix_file_path(self):
        s = "contractD%d_%d_%d_%d.txt" % self.domain.get_ordered_param_dict().get_value_tuple()
        return os.path.join(Parameters.ref_data_dir, graph_type, self.sub_type, s)

    def get_ref_rank_file_path(self):
        s = "contractD%d_%d_%d_%d.txt.rank.txt" % self.domain.get_ordered_param_dict().get_value_tuple()
        return os.path.join(Parameters.ref_data_dir, graph_type, self.sub_type, s)

    def get_work_estimate(self):
        # Returns as work estimate: domain.n_edges * domain_dim * log(target dimension, 2)
        if not self.is_valid():
            return 0
        try:
            (domain_dim, dimtarget_dim) = (
                self.domain.get_dimension(), self.target.get_dimension())
        except StoreLoad.FileNotFoundError:
            return 0
        if domain_dim == 0 or dimtarget_dim == 0:
            return 0
        return self.domain.n_edges * domain_dim * math.log(dimtarget_dim, 2)

    def get_type(self):
        return 'contract edges'

    def operate_on(self, G):
        # Operates on the graph G by contracting an edge and unifying the adjacent vertices.
        image = []
        for (i, e) in enumerate(G.edges(labels=False)):
            (u, v) = e
            # only edges not connected to a numbered hair-vertex can be contracted
            if u >= self.domain.n_vertices+self.domain.n_ws+1 or v >= self.domain.n_vertices+self.domain.n_ws+1:
                continue

            # ensure u<v (this should be always true anyway actually)
            if u > v:
                u, v = v, u

            sgn = 1 if i % 2 == 0 else -1
            previous_size = G.size()
            previous_has_tadpole = (
                previous_size - self.domain.n_vertices - self.domain.n_hairs < self.domain.n_loops)
            sgn *= -1 if previous_has_tadpole else 1
            G1 = copy(G)
            # label all edges to determine sign later
            Shared.enumerate_edges(G1)

            # we always delete the lower index vertex. This ensures that the extra vertices are never deleted
            if v <= self.domain.n_vertices:
                G1.merge_vertices([v, u])
                if (previous_size - G1.size()) != 1:
                    continue
                G1.relabel(range(0, self.domain.n_vertices+1 +
                           self.domain.n_hairs), inplace=True)
                # find edge permutation sign
                sgn *= Shared.shifted_edge_perm_sign2(G1)
                image.append((G1, sgn))
            elif u < self.domain.n_vertices and v >= self.domain.n_vertices+1:
                # the second vertex is now an omega-vertex, so we need to merge the vertex with the eps vertex
                # after reconnecting one of the edges to omega
                # we assume that u != eps, because eps-omega-edges cannot be contracted
                G1.delete_edge(u, v)
                # special care must be taken since a tadpole could be created at eps
                # and this is true iff there is an edge u-eps
                eps = self.domain.n_vertices
                new_has_tadpole = G1.has_edge(u, eps)
                # double tadpole => zero
                if new_has_tadpole and previous_has_tadpole:
                    continue
                if new_has_tadpole:
                    # remove the edge and compute the appropriate sign
                    k = G1.edge_label(u, eps)
                    G1.delete_edge(u, eps)
                    sgn *= 1 if ((k % 2 == 0) == (k < i)) else -1
                # loop over other neighbors w to be connected to omega
                for w in G1.neighbors(u):
                    G2 = copy(G1)
                    sgn2 = sgn
                    # reconnect the w-v-edge to omega (i.e., to v)
                    old_label = G2.edge_label(u, w)
                    G2.delete_edge(u, w)
                    G2.add_edge(w, v, old_label)

                    # now merge u and eps
                    G2.merge_vertices([eps, u])
                    # in case we have too few edges some double edges have been created => zero
                    if (previous_size - G2.size()) != (2 if new_has_tadpole else 1):
                        continue
                    G2.relabel(range(0, self.domain.n_vertices +
                               self.domain.n_hairs+self.domain.n_ws), inplace=True)
                    # find edge permutation sign
                    sgn2 *= Shared.shifted_edge_perm_sign2(G2)
                    image.append((G2, sgn2))

        return image

    def restrict_to_isotypical_component(self, rep_index):
        return RestrictedContractEdgesGO(self, rep_index)


class RestrictedContractEdgesGO(SymmetricGraphComplex.SymmetricRestrictedOperatorMatrix):
    # def __init__(opD, opP):

    def get_matrix_file_path(self):
        s = "contractD%d_%d_%d_r%d.txt" % (
            self.domain.vs.get_ordered_param_dict().get_value_tuple() + (self.rep_index,))
        return os.path.join(Parameters.data_dir, graph_type, self.opD.sub_type, s)

    def get_rank_file_path(self):
        s = "contractD%d_%d_%d_r%d_rank.txt" % (
            self.domain.vs.get_ordered_param_dict().get_value_tuple() + (self.rep_index,))
        return os.path.join(Parameters.data_dir, graph_type, self.opD.sub_type, s)

    def get_work_estimate(self):
        return self.opD.get_work_estimate()

    def is_match(self, domain, target):
        return ContractEdgesGO.is_match(domain.vs, target.vs) and domain.rep_index == target.rep_index


class ContractEdgesD(GraphOperator.Differential):
    """Contract edges differential."""

    def __init__(self, sum_vector_space):
        """Initialize the contract edges differential with the underlying sum vector space.

        :param sum_vector_space: Underlying vector space.
        :type sum_vector_space: HairyGraphSumVS
        """
        super(ContractEdgesD, self).__init__(sum_vector_space,
                                             ContractEdgesGO.generate_op_matrix_list(sum_vector_space))

    def get_type(self):
        return 'contract edges'

    def get_cohomology_plot_path(self):
        sub_type = self.sum_vector_space.sub_type
        s = "cohomology_dim_contract_D_%s" % (graph_type)
        return os.path.join(Parameters.plots_dir, graph_type, sub_type, s)

    def get_cohomology_web_path(self):
        sub_type = self.sum_vector_space.sub_type
        s = "cohomology_dim_contract_D_%s" % (graph_type)
        return os.path.join(Parameters.web_dir, graph_type, sub_type, s)

    def get_info_plot_path(self):
        sub_type = self.sum_vector_space.sub_type
        s = "info_contract_D_%s" % (graph_type)
        return os.path.join(Parameters.plots_dir, graph_type, sub_type, s)


class RestrictedContractEdgesD(SymmetricGraphComplex.SymmetricDifferential):

    def get_type(self):
        return 'isotypical contract edges'

    def get_cohomology_plot_path(self):
        sub_type = self.diff.sum_vector_space.sub_type
        s = "cohomology_dim_contract_D_iso_%s_%s" % (graph_type, sub_type)
        return os.path.join(Parameters.plots_dir, graph_type, sub_type, s)

    def get_info_plot_path(self):
        sub_type = self.diff.sum_vector_space.sub_type
        s = "info_contract_D_iso_%s_%s" % (graph_type, sub_type)
        return os.path.join(Parameters.plots_dir, graph_type, sub_type, s)


class EpsToOmegaGO(SymmetricGraphComplex.SymmetricGraphOperator):
    """Operator that makes one eps into an omega hair.

    Attributes:
        - sub_type (str): Graphs sub type of the domain.
    """

    def __init__(self, domain, target):
        """Initialize the domain and target vector space of the contract edges graph operator.

        :param domain: Domain vector space of the operator.
        :type domain: HairyGraphVS
        :param target: Target vector space of the operator.
        :type target: HairyGraphVS
        """
        self.sub_type = domain.sub_type
        super(EpsToOmegaGO, self).__init__(domain, target)

    @staticmethod
    def is_match(domain, target):
        """Check whether domain and target match to generate a corresponding contract edges graph operator.

        The contract edges operator reduces the number of vertices by one.

        :param domain: Potential domain vector space of the operator.
        :type domain: HairyGraphVS
        :param target: Potential target vector space of the operator.
        :type target: HairyGraphVS
        :return: True if domain and target match to generate a corresponding contract edges graph operator.
        :rtype: bool
        """
        return domain.n_vertices == target.n_vertices and domain.n_loops == target.n_loops \
            and domain.n_hairs == target.n_hairs and domain.n_ws+1 == target.n_ws

    @classmethod
    def generate_operator(cls, n_vertices, n_loops, n_hairs, n_ws):
        """Return a contract edges graph operator.

        :param n_vertices: Number of vertices of the domain.
        :type n_vertices: int
        :param n_loops: Number of loops of the domain.
        :type n_loops: int
        :param n_hairs: Number of (numbered) hairs.
        :type n_hairs: int
        :param n_ws: Number of omega hairs.
        :type n_ws: int
        :return: Contract edges graph operator based on the specified domain vector space.
        :rtype: ContractEdgesGO
        """
        domain = WOHairyGraphVS(n_vertices, n_loops, n_hairs, n_ws)
        target = WOHairyGraphVS(n_vertices, n_loops, n_hairs, n_ws+1)
        return cls(domain, target)

    def get_matrix_file_path(self):
        s = "epstowD%d_%d_%d_%d.txt" % self.domain.get_ordered_param_dict().get_value_tuple()
        return os.path.join(Parameters.data_dir, graph_type, self.sub_type, s)

    def get_rank_file_path(self):
        s = "epstowD%d_%d_%d_%d_rank.txt" % self.domain.get_ordered_param_dict().get_value_tuple()
        return os.path.join(Parameters.data_dir, graph_type, self.sub_type, s)

    # def get_ref_matrix_file_path(self):
    #     s = "epstowD%d_%d_%d_%d.txt" % self.domain.get_ordered_param_dict().get_value_tuple()
    #     return os.path.join(Parameters.ref_data_dir, graph_type, self.sub_type, s)

    # def get_ref_rank_file_path(self):
    #     s = "epstowD%d_%d_%d_%d.txt.rank.txt" % self.domain.get_ordered_param_dict().get_value_tuple()
    #     return os.path.join(Parameters.ref_data_dir, graph_type, self.sub_type, s)

    def get_work_estimate(self):
        # Returns as work estimate: domain.n_edges * domain_dim * log(target dimension, 2)
        if not self.is_valid():
            return 0
        try:
            (domain_dim, dimtarget_dim) = (
                self.domain.get_dimension(), self.target.get_dimension())
        except StoreLoad.FileNotFoundError:
            return 0
        if domain_dim == 0 or dimtarget_dim == 0:
            return 0
        return self.domain.n_edges * domain_dim * math.log(dimtarget_dim, 2)

    def get_type(self):
        return 'contract edges'

    def operate_on(self, G):
        GG = copy(G)
        sgn = (-1)**G.size()
        image = []

        # add one new omega vertex in position n_vertices +1
        GG.relabel(list(range(self.domain.n_vertices)) + list(range(self.domain.n_vertices +
                   1, self.domain.n_vertices+self.domain.n_ws+self.domain.n_hairs+1)))
        GG.add_vertex(self.domain.n_vertices+1)

        # reconnect one eps edge to the new vertex
        eps = self.domain.n_vertices
        new_w = self.domain.n_vertices+1
        for v in GG.neighbors(eps):
            GGG = copy(GG)
            GGG.delete_edge(v, eps)
            GGG.add_edge(v, new_w)
            image.append((GGG, sgn))

        return image

    def restrict_to_isotypical_component(self, rep_index):
        return RestrictedEpsToOmegaGO(self, rep_index)


class RestrictedEpsToOmegaGO(SymmetricGraphComplex.SymmetricRestrictedOperatorMatrix):
    # def __init__(opD, opP):

    def get_matrix_file_path(self):
        s = "contractD%d_%d_%d_r%d.txt" % (
            self.domain.vs.get_ordered_param_dict().get_value_tuple() + (self.rep_index,))
        return os.path.join(Parameters.data_dir, graph_type, self.opD.sub_type, s)

    def get_rank_file_path(self):
        s = "contractD%d_%d_%d_r%d_rank.txt" % (
            self.domain.vs.get_ordered_param_dict().get_value_tuple() + (self.rep_index,))
        return os.path.join(Parameters.data_dir, graph_type, self.opD.sub_type, s)

    def get_work_estimate(self):
        return self.opD.get_work_estimate()

    def is_match(self, domain, target):
        return EpsToOmegaGO.is_match(domain.vs, target.vs) and domain.rep_index == target.rep_index


class EpsToOmegaD(GraphOperator.Differential):
    """Contract edges differential."""

    def __init__(self, sum_vector_space):
        """Initialize the contract edges differential with the underlying sum vector space.

        :param sum_vector_space: Underlying vector space.
        :type sum_vector_space: HairyGraphSumVS
        """
        super(EpsToOmegaD, self).__init__(sum_vector_space,
                                          EpsToOmegaGO.generate_op_matrix_list(sum_vector_space))

    def get_type(self):
        return 'EpsToOmega'

    def get_cohomology_plot_path(self):
        sub_type = self.sum_vector_space.sub_type
        s = "cohomology_dim_epstoomega_D_%s" % (graph_type)
        return os.path.join(Parameters.plots_dir, graph_type, sub_type, s)

    def get_cohomology_web_path(self):
        sub_type = self.sum_vector_space.sub_type
        s = "cohomology_dim_epstoomega_D_%s" % (graph_type)
        return os.path.join(Parameters.web_dir, graph_type, sub_type, s)

    def get_info_plot_path(self):
        sub_type = self.sum_vector_space.sub_type
        s = "info_epstoomega_D_%s" % (graph_type)
        return os.path.join(Parameters.plots_dir, graph_type, sub_type, s)


class RestrictedEpsToOmegaD(SymmetricGraphComplex.SymmetricDifferential):

    def get_type(self):
        return 'isotypical epstoomega'

    def get_cohomology_plot_path(self):
        sub_type = self.diff.sum_vector_space.sub_type
        s = "cohomology_dim_epstoomega_D_iso_%s_%s" % (graph_type, sub_type)
        return os.path.join(Parameters.plots_dir, graph_type, sub_type, s)

    def get_info_plot_path(self):
        sub_type = self.diff.sum_vector_space.sub_type
        s = "info_epstoomega_D_iso_%s_%s" % (graph_type, sub_type)
        return os.path.join(Parameters.plots_dir, graph_type, sub_type, s)


class SymmProjector(SymmetricGraphComplex.SymmetricProjectionOperator):
    """This class encodes the projector to an isotypical component of the symmetric group action
        by permuting numbered hairs.
        Warning: The matrix stores not the projector, but projector * n_hairs! / rep_dimension??, to have integral matrices.

    Attributes:
        - sub_type(str): Graphs sub type of the domain.
    """

    def __init__(self, domain, rep_index):
        """Initialize the domain and target vector space of the contract edges graph operator.

        : param domain: Domain vector space of the operator.
        : type domain: HairyGraphVS
        : param rep_index: The index of the representation in the list produced by Partitions(h).
        : type rep_index: int
        """
        self.sub_type = domain.sub_type

        super(SymmProjector, self).__init__(domain, rep_index)

    def get_ordered_param_dict2(self):
        do = self.domain
        return Shared.OrderedDict([('vertices', do.n_vertices), ('loops', do.n_loops), ('hairs', do.n_hairs), ('ws', do.n_ws), ('rep_index', self.rep_index)])

    def get_matrix_file_path(self):
        s = "projectionO%d_%d_%d_%d_%d.txt" % self.get_ordered_param_dict2().get_value_tuple()
        return os.path.join(Parameters.data_dir, graph_type, self.sub_type, s)

    def get_rank_file_path(self):
        s = "projectionO%d_%d_%d_%d_%d_rank.txt" % self.get_ordered_param_dict2().get_value_tuple()
        return os.path.join(Parameters.data_dir, graph_type, self.sub_type, s)

    def get_ref_matrix_file_path(self):
        s = "projectionO%d_%d_%d_%d_%d.txt" % self.get_ordered_param_dict2().get_value_tuple()
        return os.path.join(Parameters.ref_data_dir, graph_type, self.sub_type, s)

    def get_ref_rank_file_path(self):
        s = "projectionO%d_%d_%d_%d_%d.txt.rank.txt" % self.get_ordered_param_dict2().get_value_tuple()
        return os.path.join(Parameters.ref_data_dir, graph_type, self.sub_type, s)


# ------- Graph Complex --------
class WOHairyGC(GraphComplex.GraphComplex):
    """Graph complex for hairy graphs.

    Attributes:
        - v_range(range): Range for the number of vertices.
        - l_range(range): Range for the number of loops.
        - h_range(range): Range for the number of hairs.
        - w_range(range): Range for the number of omega hairs
        - sub_type(str): Sub type of graphs.
    """

    def __init__(self, v_range, l_range, h_range, w_range, differentials):
        """Initialize the graph complex.

        : param v_range: Range for the number of vertices.
        : type v_range: range
        : param l_range: Range for the number of loops.
        : type l_range: range
        : param h_range: Range for the number of numbered hairs.
        : type  h_range: range
        : param w_range: Range for number of omega hairs.
        : type w_range: range
        : param differentials: List of differentials. Options: 'contract', 'et1h'.
        : type differentials: list(str)
        """
        self.v_range = v_range
        self.l_range = l_range
        self.h_range = h_range
        self.w_range = w_range
        self.sub_type = ""

        sum_vector_space = WOHairyGraphSumVS(
            self.v_range, self.l_range, self.h_range, self.w_range)
        differential_list = []
        if not set(differentials).issubset(['contract', 'contract_iso']):
            raise ValueError(
                "Differentials for hairy graph complex: 'contract'")
        contract_edges_dif = ContractEdgesD(sum_vector_space)
        if 'contract' in differentials:
            differential_list.append(contract_edges_dif)
        if 'contract_iso' in differentials:
            contract_iso_edges_dif = RestrictedContractEdgesD(
                contract_edges_dif)
            differential_list.append(contract_iso_edges_dif)
            print("Attention: contract_iso operates on nonzero cohomology entries only, so they need to be computed before!")
        super(WOHairyGC, self).__init__(sum_vector_space, differential_list)

    def __str__(self):
        return '<%s graph complex with %s>' % (graph_type, str(self.sub_type))

    def print_dim_and_eulerchar(self):
        for w in self.w_range:
            for h in self.h_range:
                for l in self.l_range:
                    ds = [WOHairyGraphVS(v, l, h, w).get_dimension()
                          for v in self.v_range]
                    eul = sum([(1 if j % 2 == 0 else -1) *
                              d for j, d in enumerate(ds)])
                    print("Dimensions (w,h,l) ", w,
                          h, l, ":", ds, "Euler", eul)

    def print_cohomology_dim(self):
        for w in self.w_range:
            for h in self.h_range:
                for l in self.l_range:
                    cohomdict = {}
                    for v in self.v_range:
                        D1 = ContractEdgesGO.generate_operator(v, l, h, w)
                        D2 = ContractEdgesGO.generate_operator(v+1, l, h, w)
                        try:
                            d = WOHairyGraphVS(v, l, h, w).get_dimension()
                            r1 = D1.get_matrix_rank()
                            r2 = D2.get_matrix_rank()
                            cohomdict[v] = d-r1-r2
                        except:
                            pass

                    print("Cohomology Dimensions (w,h,l) ",
                          w, h, l, ":", cohomdict)
