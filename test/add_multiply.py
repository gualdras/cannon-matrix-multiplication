# -*- mode:python; coding:utf-8; tab-width:4 -*-

from unittest import TestCase

from hamcrest import assert_that, is_
from numpy.testing import assert_array_almost_equal

from matrix_utils import matrix_add, matrix_multiply

import Cannon
from common import M2, M6


class AddTests(TestCase):
    def test_order_1(self):
        # given
        A = Cannon.Matrix(1, [3])
        B = Cannon.Matrix(1, [4])

        # when
        C = matrix_add(A, B)

        # then
        assert_that(C, is_(Cannon.Matrix(1, [7])))

    def test_order_2(self):
        # given
        A = M2(1, 2,
               3, 4)
        B = M2(3, 5,
               1, 0)

        # when
        C = matrix_add(A, B)

        # then
        assert_that(C, is_(M2(4, 7,
                              4, 4)))


class MultiplyTests(TestCase):
    def test_order_1(self):
        # given
        A = Cannon.Matrix(1, [3])
        B = Cannon.Matrix(1, [4])

        # when
        C = matrix_multiply(A, B)

        # then
        assert_that(C, is_(Cannon.Matrix(1, [12])))

    def test_1_order_2(self):
        # given
        A = M2(1, 2,
               3, 4)
        B = M2(3, 5,
               1, 0)

        # when
        C = matrix_multiply(A, B)

        # then
        assert_that(C, is_(M2(5, 5,
                             13, 15)))

    def test_2_order_2(self):
        # given
        A = M2(1, 2,
               3, 4)
        B = M2(5, 6,
               7, 8)

        # when
        C = matrix_multiply(A, B)

        # then
        assert_that(C, is_(M2(19, 22,
                              43, 50)))

    def test_order_6(self):
        # given
        A = M6(1,	2,	-1,	3,	-5,	3,
               3,	0,	2,	7,	1,	2,
               5,	3,	3,	1,	4,	4,
               2,	1,	2,	2,	3,	3,
               -2,	2,	6,	6,	9,	7,
               -2,	2,	-4,	2,	6,	5)

        B = M6(1,	2,	7,	7,	-1,	3,
               2,	1,	2,	1,	-1,	2,
               3,	0,	5,	5,	6,	1,
               3,	1,	4,	1,	6,	4,
               2,	4,	3,	3,	3,	9,
               1,	4,	3,	2,	1,	9)

        # when
        C = matrix_multiply(A, B)

        # then
        expected = M6(4,    -1,	12,	-2,	-3,	0,
                      34,	25,	68,	45,	56,	66,
                      35,	46,	84,	74,	32,	100,
                      25,	31,	52,	42,	33,	72,
                      63,	68,	92,	65,	106,172,
                      13,	44,	11,	-2,	11,	101)

        assert_that(C, is_(expected))


    def test_order_2_floats(self):
        # given
        A = M2(1.1, 2.3,
               3.5, 4.6)
        B = M2(3.7, 5.1,
               1.5, 1.0 / 3)

        # when
        C = matrix_multiply(A, B)

        # then
        assert_that(C.ncols, is_(2))
        assert_array_almost_equal(C.data,
                                  [ 7.52,  6.37,
                                   19.85, 19.38],
                                  decimal=2)

    def test_matrices_have_right_dimensions(self):
        # FIXME
        pass
