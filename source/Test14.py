import ForestedGraphComplex
import GraphVectorSpace

"""Builds bases of all forested vector spaces in the "computable" range.
"""


if __name__ == "__main__":
    nr_jobs = 10
    nr_jobs_basis = 10 # set to 1 if pregraphs not yet generated
    print(f"Building all computable forested bases and operators using {nr_jobs} jobs ...")
    # for even_e in [False, True]:
    FGC = ForestedGraphComplex.ContractUnmarkTopD(range(2,3), range(16), range(5,6), True)
    FGC.compute_rank(linbox="rational", n_jobs=nr_jobs)


    FGC = ForestedGraphComplex.ContractUnmarkTopD(range(5,6), range(6,16), range(2,3), True)
    FGC.compute_rank(linbox="rational", n_jobs=nr_jobs)


    # for even_e in [True, False]:
    #     for even_h in [True, False]:
    #         vs_list = vs_list + [HairyGraphComplex.HairyGraphVS(v,l,1,even_e,even_h)
    #                             for v in range(18) for l in range(10)]
    #         vs_list = vs_list + [HairyGraphComplex.HairyGraphVS(v,l,2,even_e,even_h)
    #                             for v in range(18) for l in range(9)]
    #         vs_list = vs_list + [HairyGraphComplex.HairyGraphVS(v,l,3,even_e,even_h)
    #                             for v in range(18) for l in range(7)]
    #         vs_list = vs_list + [HairyGraphComplex.HairyGraphVS(v,l,4,even_e,even_h)
    #                             for v in range(18) for l in range(6)]
    #         vs_list = vs_list + [HairyGraphComplex.HairyGraphVS(v,l,5,even_e,even_h)
    #                             for v in range(18) for l in range(6)]



    print("Finished computing ranks.")
