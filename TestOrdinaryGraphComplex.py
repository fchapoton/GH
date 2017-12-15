import unittest
import GraphVectorSpace as GVS
import GraphOperator
import OrdinaryGraphComplex as OGC
from sage.all import *

reload(GVS)
reload(GraphOperator)
reload(OGC)


class OGCTestCase(unittest.TestCase):

    def test_perm_sign(self):
        print('test of the permutation sign')

        ogc_even = OGC.OrdinaryGVS(6, 5, even_edges=True)
        ogc_odd = OGC.OrdinaryGVS(6, 5, even_edges=False)
        G = graphs.WheelGraph(5)
        p = [0, 2, 3, 4, 5, 1]
        self.assertTrue(ogc_odd.perm_sign(G, p) == 1, 'incorrect permutation sign')
        self.assertTrue(ogc_even.perm_sign(G, p) == 1, 'incorrect permutation sign')
        p = [0, 1, 5, 4, 3, 2]
        #self.assertTrue(ogc_odd.perm_sign(G, p) == 1, 'incorrect permutation sign')
        #self.assertTrue(ogc_even.perm_sign(G, p) == -1, 'incorrect permutation sign')
        p = [0, 1, 2, 4, 3, 5]
        self.assertTrue(ogc_odd.perm_sign(G, p) == -1, 'incorrect permutation sign')
        self.assertTrue(ogc_even.perm_sign(G, p) == 1, 'incorrect permutation sign')

    def test_valid(self):
        ogc_even = OGC.OrdinaryGVS(5, 5, even_edges=True)

    def test_basis_functionality(self):

        for even_edges in [True, False]:
            print('test for basis functionality for even_edges=%s' % even_edges)

            ogc = OGC.OrdinaryGVS(7, 8, even_edges=even_edges)
            ogc.delete_file()
            self.assertFalse(ogc.basis_built(),'basis should have been deleted')
            self.assertRaises(GVS.NotBuiltError, ogc.get_basis)
            ogc.create_basis()
            self.assertTrue(ogc.basis_built(),'basis should exist')
            basis_g6=ogc.get_basis()
            self.assertTrue(len(basis_g6)>0,'basis_g6 has size 0 for even_edges=%s' % even_edges)
            self.assertIsInstance(basis_g6,list,'type of basis_g6 is not a list')
            self.assertIsInstance(basis_g6[0],basestring, 'type of basis_g6 elements is not string')
            basis=ogc.get_basis(g6=False)
            self.assertEqual(len(basis), len(basis_g6),' basis_g6 and basis have not the same size for even_edges=%s' % even_edges)
            self.assertIsInstance(basis,list,'type of basis is not a list')
            for i in range(len(basis_g6)):
                self.assertEqual(basis_g6[i], basis[i].graph6_string(),'error: basis is not equal to basis_g6 for even_edges=%s' % even_edges)

    def test_operator_functionality(self):

        op=OGC.ContractGO(6, 5, even_edges=False)
        op.delete_file()
        op.create_domain_basis()
        op.create_target_basis()
        op.create_operator_matrix()

def suite():
    suite = unittest.TestSuite()
    suite.addTest(OGCTestCase('test_valid'))
    suite.addTest(OGCTestCase('test_perm_sign'))
    suite.addTest(OGCTestCase('test_basis_functionality'))
    suite.addTest(OGCTestCase('test_operator_functionality'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
