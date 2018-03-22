import argparse
import Log
import Profiling
import OrdinaryGraphComplex as OGC
import HairyGraphComplex as HGC
import Parameters


logger = Log.logger.getChild('main')


def positive_int(value):
    value = int(value)
    if value <= 0:
        raise argparse.ArgumentTypeError('positive integer expected')
    return value

def non_negative_int(value):
    value = int(value)
    if value < 0:
        raise argparse.ArgumentTypeError('non negative integer expected')
    return value


def positive_range_type(arg):
    (min, max) = map(positive_int, arg.split(','))
    if min >= max:
        raise argparse.ArgumentTypeError('range min,max with 0 < min < max expected')
    return range(min, max)

graph_complex_types = ['o_ce', 'h_ce', 'h_etoh']

parser = argparse.ArgumentParser(description='Compute the homology of a graph complex')

parser.add_argument('graph_complex_type', type=str, choices=graph_complex_types, help='type of the graph complex')
parser.add_argument('-even_e', action='store_true', help='even edges')
parser.add_argument('-odd_e', action='store_true', help='odd edges')
parser.add_argument('-even_h', action='store_true', help='even hairs')
parser.add_argument('-odd_h', action='store_true', help='odd edges')
parser.add_argument('-v', type=positive_range_type, help='range min,max for number of vertices')
parser.add_argument('-l', type=positive_range_type, help='range min,max for number of loops')
parser.add_argument('-hairs', type=positive_range_type, help='range min,max for number of hairs')
parser.add_argument('-ignore_ex', action='store_true', help='ignore existing files')
parser.add_argument('-n_jobs', type=positive_int, default=1, help='number of parallel processes')
parser.add_argument('-pbar', action='store_true', help='show progressbar')
parser.add_argument('-profile', action='store_true', help='profiling')
parser.add_argument('-log', type=str, choices=Log.log_levels_dict.keys(), help='logging level')
parser.add_argument('-exact_rank', action='store_true', help='exact matrix rank computation')
parser.add_argument('-n_primes', type=non_negative_int, default=1, help='compute matrix rank modulo n_primes different prime numbers')
parser.add_argument('-no_est_rank', action='store_false', help="don't estimate matrix rank")
parser.add_argument('-build', action='store_true', help='just build vector space basis and operator matrix')
parser.add_argument('-build_b', action='store_true', help='just build vector space basis')
parser.add_argument('-build_op', action='store_true', help='just build operator matrix')
parser.add_argument('-rank', action='store_true', help='just compute matrix ranks')
parser.add_argument('-coho', action='store_true', help='just compute cohomology')
parser.add_argument('-square_zero', action='store_true', help='square zero test')

args = parser.parse_args()


@Profiling.cond_decorator(args.profile, Profiling.profile(Parameters.log_dir))
def cohomology_complete(graph_complex):
    graph_complex.build_basis(ignore_existing_files=args.ignore_ex, n_jobs=args.n_jobs, progress_bar=args.pbar)
    graph_complex.build_matrix(ignore_existing_files=args.ignore_ex, n_jobs=args.n_jobs, progress_bar=args.pbar)
    graph_complex.compute_rank(ignore_existing_files=args.ignore_ex)
    graph_complex.plot_cohomology_dim()


@Profiling.cond_decorator(args.profile, Profiling.profile(Parameters.log_dir))
def build(graph_complex):
    graph_complex.build_basis(ignore_existing_files=args.ignore_ex, n_jobs=args.n_jobs, progress_bar=args.pbar)
    graph_complex.build_matrix(ignore_existing_files=args.ignore_ex, n_jobs=args.n_jobs, progress_bar=args.pbar)


@Profiling.cond_decorator(args.profile, Profiling.profile(Parameters.log_dir))
def build_basis(graph_complex):
    graph_complex.build_basis(ignore_existing_files=args.ignore_ex, n_jobs=args.n_jobs, progress_bar=args.pbar)


@Profiling.cond_decorator(args.profile, Profiling.profile(Parameters.log_dir))
def build_operator(graph_complex):
    graph_complex.build_matrix(ignore_existing_files=args.ignore_ex,
                               n_jobs=args.n_jobs, progress_bar=args.pbar)


@Profiling.cond_decorator(args.profile, Profiling.profile(Parameters.log_dir))
def square_zero_test(graph_complex):
    graph_complex.square_zero_test()


@Profiling.cond_decorator(args.profile, Profiling.profile(Parameters.log_dir))
def rank(graph_complex):
    graph_complex.compute_rank(exact=args.exact_rank, n_primes=args.n_primes, estimate=args.no_est_rank,
                               ignore_existing_files=args.ignore_ex, n_jobs=args.n_jobs)


@Profiling.cond_decorator(args.profile, Profiling.profile(Parameters.log_dir))
def cohomology(graph_complex):
    graph_complex.plot_cohomology_dim()


class MissingArgumentError(RuntimeError):
    pass


if __name__ == "__main__":
    if args.log is not None:
        Log.set_log_level(args.log)
        log_file = args.graph_complex_type + '.log'
        Log.set_log_file(log_file)

    logger.warn("\n###########################\n" + "----- Graph Homology -----")

    graph_complex = None

    if args.even_e:
            even_edges = True
    elif args.odd_e:
            even_edges = False
    else:
        raise MissingArgumentError('specify -even_e or -odd_e')

    if args.v is None:
        raise MissingArgumentError('specify -v: range for number of vertices')
    if args.l is None:
        raise MissingArgumentError('specify -l: range for number of loops')

    if args.graph_complex_type in {'h_ce', 'h_etoh'}:
        if args.even_h:
                even_hairs = True
        elif args.odd_h:
                even_hairs = False
        else:
            raise MissingArgumentError('specify -even_h or -odd_h')

        if args.hairs is None:
            raise MissingArgumentError('specify -hairs: range for number of hairs')

    if args.graph_complex_type == 'o_ce':
        graph_complex = OGC.OrdinaryContractEdgesGC(args.v, args.l, even_edges)
    elif args.graph_complex_type == 'h_ce':
        graph_complex = HGC.ContractEdgesGC(args.v, args.l, args.hairs, even_edges, even_hairs)
    elif args.graph_complex_type == 'h_etoh':
        graph_complex = HGC.EdgeToOneHairGC(args.v, args.l, args.hairs, even_edges, even_hairs)

    if not (args.build or args.build_b or args.build_op or args.square_zero or args.rank or args.coho):
        cohomology_complete(graph_complex)
    else:
        if args.build:
            build(graph_complex)
        else:
            if args.build_b:
                build_basis(graph_complex)
            if args.build_op:
                build_operator(graph_complex)
        if args.square_zero:
            square_zero_test(graph_complex)
        if args.rank:
            rank(graph_complex)
        if args.coho:
            cohomology(graph_complex)
