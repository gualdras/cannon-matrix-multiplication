# -*- mode:python; coding:utf-8; tab-width:4 -*-

from unittest import TestCase

from hamcrest import assert_that, anything, is_
import Ice
from doublex import Mimic, Spy, called, wait_that

from processor import ProcessorI
from frontend import FrontendI
import Cannon

from matrix_utils import matrix_multiply

from common import M1, M2, M3, M4


class Broker(object):
    def __init__(self, properties=None):
        properties = properties or []

        data = Ice.InitializationData()
        data.properties = Ice.createProperties()
        for p in properties:
            data.properties.setProperty(p[0], p[1])

        self.communicator = Ice.initialize(data)
        self.adapter = self.communicator.createObjectAdapterWithEndpoints('Adapter', 'tcp')
        self.adapter.activate()

    def add_servant(self, servant, iface):
        proxy = self.adapter.addWithUUID(servant)
        return iface.uncheckedCast(proxy)

    def shutdown(self):
        self.adapter.deactivate()
        self.communicator.shutdown()


class ProcessorObjectTests(TestCase):
    def setUp(self):
        self.broker = Broker([
            ["Ice.ThreadPool.Server.Size", "10"],
            ["Ice.ThreadPool.Client.Size", "10"]])

    def tearDown(self):
        self.broker.shutdown()

    def test_collector_called(self):
        # given
        processor = self.broker.add_servant(ProcessorI(), Cannon.ProcessorPrx)

        collector_servant = Mimic(Spy, Cannon.Collector)
        collector = self.broker.add_servant(collector_servant, Cannon.CollectorPrx)

        A = M2(1, 2,
               3, 4)
        B = M2(5, 6,
               7, 8)

        # when
        processor.init(0, 1, None, None, collector)
        processor.injectA(A, 0)
        processor.injectB(B, 0)

        # then
        C = M2(19, 22,
               43, 50)
        assert_that(collector_servant.inject,
                    called().async(1).with_args(0, C, anything()))

    def test_linked_processors(self):
        P0 = self.broker.add_servant(ProcessorI(), Cannon.ProcessorPrx)

        P1_servant = Mimic(Spy, Cannon.Processor)
        P1 = self.broker.add_servant(P1_servant, Cannon.ProcessorPrx)

        P2_servant = Mimic(Spy, Cannon.Processor)
        P2 = self.broker.add_servant(P2_servant, Cannon.ProcessorPrx)

        collector_servant = Mimic(Spy, Cannon.Collector)
        collector = self.broker.add_servant(collector_servant, Cannon.CollectorPrx)

        A0 = M1(1)
        B0 = M1(5)

        P0.init(3, 2, P2, P1, collector)
        P0.injectA(A0, 0)
        P0.injectB(B0, 0)

        assert_that(P1_servant.injectA,
                    called().async(1).with_args(A0, 1, anything()))
        assert_that(P2_servant.injectB,
                    called().async(1).with_args(B0, 1, anything()))

    def test_2x2_processors_2x2_operands(self):
        '''
        initial shift:
        1 2     1 2      5 6    5 8
        3 4 <   4 3      7 8    7 6
                           ^

        processors and collectors are distributed objects
        '''
        P = [self.broker.add_servant(ProcessorI(), Cannon.ProcessorPrx)
             for i in range(4)]

        collector_servant = Mimic(Spy, Cannon.Collector)
        collector = self.broker.add_servant(collector_servant, Cannon.CollectorPrx)

        # by-hand shifted submatrices
        A0 = M1(1)
        A1 = M1(2)
        A2 = M1(4)
        A3 = M1(3)

        B0 = M1(5)
        B1 = M1(8)
        B2 = M1(7)
        B3 = M1(6)

        # by-hand processor initialization
        P[0].init(0, 2, P[2], P[1], collector)
        P[1].init(1, 2, P[3], P[0], collector)
        P[2].init(2, 2, P[0], P[3], collector)
        P[3].init(3, 2, P[1], P[2], collector)

        # by-hand processor loading
        P[0].injectA(A0, 0); P[0].injectB(B0, 0)
        P[1].injectA(A1, 0); P[1].injectB(B1, 0)
        P[2].injectA(A2, 0); P[2].injectB(B2, 0)
        P[3].injectA(A3, 0); P[3].injectB(B3, 0)

        wait_that(collector_servant.inject,
                  called().times(4))

        # expected result blocks
        C0 = M1(19)
        C1 = M1(22)
        C2 = M1(43)
        C3 = M1(50)

        assert_that(collector_servant.inject, called().with_args(0, C0, anything()))
        assert_that(collector_servant.inject, called().with_args(1, C1, anything()))
        assert_that(collector_servant.inject, called().with_args(2, C2, anything()))
        assert_that(collector_servant.inject, called().with_args(3, C3, anything()))


class EndToEndTests(TestCase):
    def setUp(self):
        self.broker = Broker([
            ["Ice.ThreadPool.Server.Size", "20"],
            ["Ice.ThreadPool.Client.Size", "20"]])

    def tearDown(self):
        self.broker.shutdown()

    def test_2x2_processors_2x2_operands(self):
        nprocs = 4

        # given
        P = [self.broker.add_servant(ProcessorI(), Cannon.ProcessorPrx)
             for i in range(nprocs)]
        frontend = self.broker.add_servant(FrontendI(P), Cannon.FrontendPrx)

        A = M2(1, 2,
               3, 4)
        B = M2(3, 5,
               1, 0)

        # when
        C = frontend.multiply(A, B)

        # then
        expected = M2(5,  5,
                     13, 15)

        assert_that(C, is_(expected))

    def test_3x3_processors_3x3_operands(self):
        nprocs = 9

        # given
        P = [self.broker.add_servant(ProcessorI(), Cannon.ProcessorPrx)
             for i in range(nprocs)]
        frontend = self.broker.add_servant(FrontendI(P), Cannon.FrontendPrx)

        A = M3(1, 2, 3,
               4, 5, 6,
               7, 8, 9)
        B = M3(10, 11, 12,
               13, 14, 15,
               16, 17, 18)

        # when
        C = frontend.multiply(A, B)

        # then
        expected = M3(84,  90,  96,
                     201, 216, 231,
                     318, 342, 366)

        assert_that(C, is_(expected))
	
	def test_2x3_processors_3x2_operands(self):
        nprocs = 9

        # given
        P = [self.broker.add_servant(ProcessorI(), Cannon.ProcessorPrx)
             for i in range(nprocs)]
        frontend = self.broker.add_servant(FrontendI(P), Cannon.FrontendPrx)

		A =	Cannon.Matrix(3, [1, 2, 3, 4, 5, 6])
			
		B = Cannon.Matrix(2, [1, 2, 3, 4, 5, 6])
   

        # when
        C = frontend.multiply(A, B)

        # then
        expected = M3(22, 28, 0,
                      49, 64, 0,
                      0, 0, 0)

        assert_that(C, is_(expected))
		

    def test_2x2_processors_4x4_operands(self):
        nprocs = 4

        # given
        P = [self.broker.add_servant(ProcessorI(), Cannon.ProcessorPrx)
             for i in range(nprocs)]
        frontend = self.broker.add_servant(FrontendI(P), Cannon.FrontendPrx)

        A = M4(1,  2,  3,  4,
               5,  6,  7,  8,
               9, 10, 11, 12,
              13, 14, 15, 16)

        B = M4(17, 18, 19, 20,
               21, 22, 23, 24,
               25, 26, 27, 28,
               29, 30, 31, 32)

        # when
        C = frontend.multiply(A, B)

        # then
        expected = M4(250,  260,  270,  280,
                      618,  644,  670,  696,
                      986, 1028, 1070, 1112,
                     1354, 1412, 1470, 1528)

        assert_that(C, is_(expected))

    def test_5x5_processors_200x200_operands(self):
        nprocs = 25

        # given
        P = [self.broker.add_servant(ProcessorI(), Cannon.ProcessorPrx)
             for i in range(nprocs)]
        frontend = self.broker.add_servant(FrontendI(P), Cannon.FrontendPrx)

        A_last = 200 * 200
        A = Cannon.Matrix(200, range(1, 1 + A_last))
        B = Cannon.Matrix(200, range(1 + A_last, 1 + A_last * 2))

        # when
        C = frontend.multiply(A, B)

        # then
        expected = matrix_multiply(A, B)
        assert_that(C, is_(expected))

