import BVCyclic


ovs1 = BVCyclic.GOneVS(9,6)
ovs2 = BVCyclic.GOneVS(8,6)

l = ovs1.get_generating_graphs2()
print(list(l))

# print(vs.get_dimension(), op1.get_matrix_rank(), op2.get_matrix_rank(), opc.get_matrix_rank())
# print(ovs1.get_dimension(), ovs2.get_dimension())