# -*- mode:python; coding:utf-8; tab-width:4 -*-

from unittest import TestCase

from doublex import assert_that, Spy, called, ANY_ARG

import Ice
Ice.loadSlice('-I {} cannon.ice'.format(Ice.getSliceDir()))
import Cannon

from processor import ProcessorI

from common import M1, M2, M6


class ProcessorServantTests(TestCase):

    def test_processors_0_block(self):
        # given
        P0 = ProcessorI()
        collector = Spy()
            
        A = M2(0, 0,
               0, 0)
        B = M2(0, 0,
               0, 0)
        C = M2(0, 0,
               0, 0)

        # when
        P0.init(0, 1, None, None, collector)
        P0.injectA(A, 0)
        P0.injectB(B, 0)

        # then
        assert_that(collector.inject, called().with_args(0, C, ANY_ARG))

    def test_processors_6x6_block(self):
        # given
        P0 = ProcessorI()
        collector = Spy()
            
        A = M6(5,  12,  6,  3,  1,  7,  	
               6,  2,  4,  7,  1,  1,  
               7,  8,  2,  3,  4,  2,  
               1,  5,  3,  6,  7,  5,  
               6,  5,  1,  3,  8,  4,  
               1,  4,  6,  3,  4,  6)
        B = M6(21,  2,  5,  9,  2,  3,  	
               4,  3,  25,  17,  3,  6,  
               45,  61,  3,  4,  45,  5,  
               21,  2,  4,  84,  55,  62,  
               6,  46,  1,  62,  1,  28,  
               89,  7,  84,  1,  6,  49)
        C = M6(1115, 513, 944, 594, 524, 674, 	
               556, 329, 205, 755, 590, 561, 
               534, 364, 425, 709, 309, 475, 
               789, 569, 590, 1049, 519, 861, 
               658, 490, 514, 895, 269, 659, 
               928, 612, 643, 607, 489, 649)

        # when
        P0.init(0, 1, None, None, collector)
        P0.injectA(A, 0)
        P0.injectB(B, 0)

        # then
        assert_that(collector.inject, called().with_args(0, C, ANY_ARG))

    def test_processors_2x2_negative_block(self):
        # given
        P0 = ProcessorI()
        collector = Spy()

        A = M2(-5, 2,
               7, -4)
        B = M2(1, -2,
               7, -7)
        C = M2(9, -4, 	
               -21, 14)

        # when
        P0.init(0, 1, None, None, collector)
        P0.injectA(A, 0)
        P0.injectB(B, 0)

        # then
        assert_that(collector.inject, called().with_args(0, C, ANY_ARG))

if __name__ == "__main__":
    unittest.main()
