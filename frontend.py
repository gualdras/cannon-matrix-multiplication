#!/usr/bin/python -u
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import sys, math, threading

import Ice
Ice.loadSlice('-I {} cannon.ice'.format(Ice.getSliceDir()))
Ice.loadSlice('-I %s container.ice' % Ice.getSliceDir())
import Cannon
import IceGrid
import Services

from matrix_utils import (matrix_horizontal_shift,
                          matrix_vertical_shift,
                          matrix_split, matrix_join)




class FrontendI(Ice.Application, Cannon.Frontend):
    def __init__(self, processors):
        self.processors=processors
        self.order=math.sqrt(len(self.processors))
        self.order=int(self.order)
        self.collector=None
        self.prxCollector=None

    def multiply(self, A, B, current=None):
        self.collector=CollectorI(self.order)
        proxy=current.adapter.addWithUUID(self.collector)
        self.prxCollector=Cannon.CollectorPrx.checkedCast(proxy)
        A,B=self.igualarOrdenMatrices(A,B)
        self.init_processors()
        self.load_processors(A,B)
        result=self.collector.get_result()
        return result
        

    def init_processors(self):
        for i in range(len(self.processors)):
            above=(i-self.order)%len(self.processors)
            if(i%self.order==0):
                left=i+self.order-1
            else:
                left=i-1
            self.processors[i].init(i, self.order, self.processors[above], self.processors[left], self.prxCollector)
            
    def igualarOrdenMatrices(self, A, B):
		nrowsA=len(A.data)/A.ncols
		nrowsB=len(B.data)/B.ncols
		
		if(nrowsA != A.ncols or nrowsB != B.ncols or A.ncols != B.ncols):
			i_max=max(nrowsA, nrowsB, A.ncols, B.ncols)
			A = self.redimensionar_matriz(A, nrowsA, i_max)
			B = self.redimensionar_matriz(B, nrowsB, i_max)	
			
			A.ncols=i_max
			B.ncols=i_max
		
		return A, B	
		
	def redimensionar_matriz(self, M, nrows, i_max):
			for i in range(nrows):
				for j in range(M.ncols, i_max):
					M.data.insert(i*i_max + j, 0)
		
			for i in range(i_max):
				M.data.append(0)
					
			return M
        

    def load_processors(self, A, B):
        A=matrix_horizontal_shift(A, A.ncols/self.order)
        B=matrix_vertical_shift(B, B.ncols/self.order)

        lista_sub_mA=matrix_split(A, A.ncols/self.order)
        lista_sub_mB=matrix_split(B, B.ncols/self.order)

        for i in range(len(self.processors)):
            self.processors[i].begin_injectA(lista_sub_mA[i], 0)
            self.processors[i].begin_injectB(lista_sub_mB[i], 0)
        


class CollectorI(Cannon.Collector):
	
    def __init__(self, order):
		self.semResult=threading.Event()
        self.order=order
        self.mResult=[]
        self.count=0
        for i in range(self.order*self.order):
            self.mResult.append(None) 
        self.semResult.clear()

    def inject(self, index, block, current=None):
        self.mResult[index]= block
        self.count=self.count+1
        if(self.count==self.order*self.order):
            self.semResult.set()
    
    def get_result(self):
        if(self.semResult.wait(300)):
            self.mResult=matrix_join(*self.mResult)	
            return self.mResult
        return None

class Server(Ice.Application):
    def run(self, args):
        processors = []

		proxy = self.communicator().stringToProxy("IceGrid/Query")
		query = IceGrid.QueryPrx.checkedCast(proxy)
		tipo="::Services::Container"
		prxContainer = query.findObjectByType(tipo)
		container = Services.ContainerPrx.checkedCast(prxContainer)
	
		factory_dict=container.list()
		for i in range(len(factory_dict)):
			factory_dict[str(i)]=Cannon.ProcessorFactoryPrx.checkedCast(factory_dict[str(i)])

		for i in range(25):
			processors.append(factory_dict[str(i%len(factory_dict))].make())

        print('found {} processors'.format(len(processors)))

        servant = FrontendI(processors)

        broker = self.communicator()
        adapter = broker.createObjectAdapter('FrontendAdapter')
        proxy = adapter.add(servant, broker.stringToIdentity("frontend"))

        print(proxy)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()


if __name__ == '__main__':
    sys.exit(Server().main(sys.argv))
