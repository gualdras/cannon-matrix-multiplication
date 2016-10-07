#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-
import sys

import Ice
from frontend import FrontendI
from processor import ProcessorI
Ice.loadSlice('-I {} cannon.ice'.format(Ice.getSliceDir()))
import Cannon
import IceGrid
from hamcrest import assert_that, anything, is_

from matrix_utils import matrix_multiply

from doublex import Mimic, Spy, called, wait_that

class Client(Ice.Application):
    def run(self, argv):

		proxy = self.communicator().stringToProxy("IceGrid/Query")
		query = IceGrid.QueryPrx.checkedCast(proxy)
		tipo="::Cannon::Frontend"
		prxFrontend = query.findObjectByType(tipo)
        frontend = Cannon.FrontendPrx.checkedCast(prxFrontend)

        if not frontend:
            raise RuntimeError('Invalid proxy')

		ncols=400*400
        matrixA= Cannon.Matrix(400, range(1, 1+ncols))
		matrixB=Cannon.Matrix(400, range(1 + ncols,1 + ncols*2))
	 	# when
        C = frontend.multiply(matrixA, matrixB)

        # then
        expected = matrix_multiply(matrixA, matrixB)
        print(expected==C)
        


        #print(frontend.multiply(matrixA,matrixB))
        return 0

'''        
        
'''        
		


sys.exit(Client().main(sys.argv))
'''
        prxProcs=[]
        #for i in leng(argv-1):
        #    prxProcs[i]=self.communicator().stringToProxy(argv[i+1])

        prxProcs1 = self.communicator().stringToProxy(argv[2])
        prxProcs2 = self.communicator().stringToProxy(argv[3])
        prxProcs3 = self.communicator().stringToProxy(argv[4])
        prxProcs4 = self.communicator().stringToProxy(argv[5])

        #for i in leng(argv-1):
        #    prxProcs[i]=self.communicator().stringToProxy(argv[i+1])
'''
