# -*- mode:python; coding:utf-8; tab-width:4 -*-

from unittest import TestCase
from hamcrest import assert_that, is_
from frontend import CollectorI
from common import M1, M2, M4


class CollectorServantTests(TestCase):
    """
    These are NOT remote tests. We directly instantiate servants here.
    """
    def test_order_1_block_1x1(self):
        # given
        collector = CollectorI(order=1)

        # when
        M = M1(1)
        collector.inject(0, M)

        # then
        assert_that(collector.get_result(), is_(M))

    def test_order_4_blocks_1x1(self):
        # given
        collector = CollectorI(order=2)
        collector.inject(0, M1(1))
        collector.inject(1, M1(2))
        collector.inject(2, M1(3))

        # when
        collector.inject(3, M1(4))

        # then
        assert_that(collector.get_result(), is_(M2(1, 2,
                                                   3, 4)))

    def test_order_4_blocks_2x2(self):
        # given
        collector = CollectorI(order=2)
        collector.inject(0, M2(1, 2,
                               5, 6))
        collector.inject(1, M2(3, 4,
                               7, 8))
        collector.inject(2, M2(9, 10,
                               13, 14))

        # when
        collector.inject(3, M2(11, 12,
                               15, 16))

        # then
        expected = M4(1,  2,  3,  4,
                      5,  6,  7,  8,
                      9, 10, 11, 12,
                     13, 14, 15, 16)

        assert_that(collector.get_result(), is_(expected))
'''
    def test_order_4_blocks_1x1_with_missing_blocks(self):
        # given
        collector = CollectorI(order=2)
        collector.inject(0, M1(1))
        collector.inject(1, M1(2))
        # block (1,0) never injected

        # when
        collector.inject(3, M1(4))

        # then
        assert_that(collector.get_result(), is_(None))
'''
