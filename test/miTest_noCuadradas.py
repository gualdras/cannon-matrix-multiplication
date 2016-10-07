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


class EndToEndTests(TestCase):

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
		
