import unittest
import logging
import Log
import TestGraphComplex
import BiColoredHairyGraphComplex


log_file = "HGC_Unittest.log"

v_range = range(0, 9)
l_range = range(0, 5)
h_a_range = range(0, 6)
h_b_range = range(0, 6)


class GraphComplexTest(TestGraphComplex.GraphComplexTest):
    def setUp(self):
        self.gc_list = [BiColoredHairyGraphComplex.BiColoredHairyGC(v_range, l_range, h_a_range, h_b_range,
                                                                    False, True, True, ['contract', 'split'])]


class SquareZeroTest(TestGraphComplex.SquerZeroTest):
    def setUp(self):
        self.gc_list = [BiColoredHairyGraphComplex.BiColoredHairyGC(v_range, l_range, h_a_range, h_b_range,
                                                                    False, True, True, ['contract', 'split'])]


class AntiCommutativityTest(TestGraphComplex.AntiCommutativityTest):
    def setUp(self):
        self.gc_list = [BiColoredHairyGraphComplex.BiColoredHairyGC(v_range, l_range, h_a_range, h_b_range,
                                                                    False, True, True, ['contract', 'split'])]


def suite():
    suite = unittest.TestSuite()
    suite.addTest(GraphComplexTest('test_graph_complex_functionality'))
    suite.addTest(SquareZeroTest('test_square_zero'))
    suite.addTest(AntiCommutativityTest('test_anti_commutativity'))
    return suite


if __name__ == '__main__':
    Log.set_log_file(log_file)
    Log.set_log_level('warning')
    logging.warn("\n#######################################\n" + "----- Start test suite for bi colored hairy graph complex -----")
    runner = unittest.TextTestRunner()
    runner.run(suite())