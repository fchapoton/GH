import OrdinaryGraphBiComplex as OGBC

if __name__ == "__main__":

    ignore_ex = True

    n_jobs = 8

    even_e = False
    deg_range = range(3, 17)

    gc = OGBC.OrdinaryBiGC(deg_range, even_e)

    gc.build_basis(info_tracker=True, ignore_existing_files=ignore_ex, n_jobs=n_jobs)

    gc.build_matrix(info_tracker=True, ignore_existing_files=ignore_ex, n_jobs=n_jobs)

    #gc.square_zero_test()

    op_list = gc.operator_collection_list[0].get_op_list()
    for op in op_list:
        m = op.get_matrix()


    #gc.compute_rank(info_tracker=True, ignore_existing_files=ignore_ex, n_jobs=n_jobs)

    #gc.plot_cohomology_dim()