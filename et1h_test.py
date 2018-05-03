import HairyGraphComplex as HGC
reload(HGC)

o1 = HGC.EdgeToOneHairGO.generate_operator(8,5,4,True,False)
o2 = HGC.EdgeToOneHairGO.generate_operator(8,4,5,True,False)
o1.get_domain().build_basis()
o1.get_target().build_basis()
o2.get_target().build_basis()
o2.get_domain()==o1.get_target()

b1 = o1.get_domain().get_basis(g6=False)

image_dict = dict()
for G in b1:
    image = o2.operate_on_list(o1.operate_on(G))
    if len(image) > 0:
        print({G:image})


