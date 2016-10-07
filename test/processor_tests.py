# -*- mode:python; coding:utf-8; tab-width:4 -*-

from unittest import TestCase

from doublex import assert_that, Spy, called, ANY_ARG

import Ice
Ice.loadSlice('-I {} cannon.ice'.format(Ice.getSliceDir()))
import Cannon

from processor import ProcessorI

from common import M1, M2, M6


class ProcessorServantTests(TestCase):
    """
    These are NOT remote tests. We directly instantiate servants here.
    """
    def test_processors_1x1_block(self):
        # given
        P0 = ProcessorI()
        collector = Spy()

        A = M1(2)
        B = M1(5)
        C = M1(10)

        # when
        P0.init(0, 1, None, None, collector)
        P0.injectA(A, 0)
        P0.injectB(B, 0)

        # then
        assert_that(collector.inject, called().with_args(0, C, ANY_ARG))

    def test_processors_2x2_block(self):
        # given
        P0 = ProcessorI()
        collector = Spy()

        A = M2(1, 2,
               3, 4)
        B = M2(5, 6,
               7, 8)
        C = M2(19, 22,
               43, 50)

        # when
        P0.init(0, 1, None, None, collector)
        P0.injectA(A, 0)
        P0.injectB(B, 0)

        # then
        assert_that(collector.inject, called().with_args(0, C, ANY_ARG))

if __name__ == "__main__":
    unittest.main()
