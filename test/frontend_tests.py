# -*- mode:python; coding:utf-8; tab-width:4 -*-

from unittest import TestCase

from hamcrest import assert_that, anything
from doublex import Spy, called

import Ice
Ice.loadSlice('-I {} cannon.ice'.format(Ice.getSliceDir()))
import Cannon

from frontend import FrontendI

from common import M1, M2, M4


class FrontendServantTests(TestCase):
    """
    These are NOT remote tests. We directly instantiate servants here.
    """
    def test_processor_init_2x2_operands_in_2x2_processors(self):
        # given
        nprocs = 4
        procs = [Spy(Cannon.Processor) for i in range(nprocs)]
        frontend = FrontendI(procs)

        # when
        frontend.init_processors()

        # then
        assert_that(procs[0].init, called().with_args(0, 2, procs[2], procs[1], anything()))
        assert_that(procs[1].init, called().with_args(1, 2, procs[3], procs[0], anything()))
        assert_that(procs[2].init, called().with_args(2, 2, procs[0], procs[3], anything()))
        assert_that(procs[3].init, called().with_args(3, 2, procs[1], procs[2], anything()))

    def test_processor_init_3x3_operands_in_3x3_processors(self):
        # given
        nprocs = 9
        procs = [Spy(Cannon.Processor) for i in range(nprocs)]
        frontend = FrontendI(procs)

        # when
        frontend.init_processors()

        # then
        assert_that(procs[0].init, called().with_args(0, 3, procs[6], procs[2], anything()))
        assert_that(procs[1].init, called().with_args(1, 3, procs[7], procs[0], anything()))
        assert_that(procs[2].init, called().with_args(2, 3, procs[8], procs[1], anything()))
        assert_that(procs[3].init, called().with_args(3, 3, procs[0], procs[5], anything()))
        assert_that(procs[4].init, called().with_args(4, 3, procs[1], procs[3], anything()))
        assert_that(procs[5].init, called().with_args(5, 3, procs[2], procs[4], anything()))
        assert_that(procs[6].init, called().with_args(6, 3, procs[3], procs[8], anything()))
        assert_that(procs[7].init, called().with_args(7, 3, procs[4], procs[6], anything()))
        assert_that(procs[8].init, called().with_args(8, 3, procs[5], procs[7], anything()))

    def test_load_2x2_operands_in_2x2_processors(self):
        nprocs = 4

        # given
        A = M2(1, 2,
               3, 4)

        B = M2(5, 6,
               7, 8)

        procs = [Spy(Cannon.Processor) for i in range(nprocs)]

        frontend = FrontendI(procs)

        # when
        frontend.load_processors(A, B)

        # then
        A_blocks = [M1(1), M1(2),
                    M1(4), M1(3)]
        B_blocks = [M1(5), M1(8),
                    M1(7), M1(6)]

        for i in range(nprocs):
            assert_that(procs[i].injectA, called().with_args(A_blocks[i], 0))
            assert_that(procs[i].injectB, called().with_args(B_blocks[i], 0))

    def test_load_4x4_operands_in_2x2_processors(self):
        nprocs = 4

        # given
        A = M4(1,  2,  3,  4,
               5,  6,  7,  8,
               9, 10, 11, 12,
              13, 14, 15, 16)

        B = M4(17, 18, 19, 20,
               21, 22, 23, 24,
               25, 26, 27, 28,
               29, 30, 31, 32)

        procs = [Spy(Cannon.Processor) for i in range(nprocs)]
        frontend = FrontendI(procs)

        # when
        frontend.load_processors(A, B)

        # then
        A_blocks = [
            M2(1, 2,
               5, 6),
            M2(3, 4,
               7, 8),
            M2(11, 12,
               15, 16),
            M2(9, 10,
              13, 14)]

        B_blocks = [
            M2(17, 18,
               21, 22),
            M2(27, 28,
               31, 32),
            M2(25, 26,
               29, 30),
            M2(19, 20,
               23, 24)]

        for i in range(nprocs):
            assert_that(procs[i].injectA, called().with_args(A_blocks[i], 0))
            assert_that(procs[i].injectB, called().with_args(B_blocks[i], 0))

