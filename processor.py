#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import sys
import threading

import Ice
Ice.loadSlice('-I {} cannon.ice'.format(Ice.getSliceDir()))
Ice.loadSlice('-I %s container.ice' % Ice.getSliceDir())
import Cannon
import Services
import IceGrid
from matrix_utils import matrix_multiply, matrix_add

class ProcessorFactoryI(Cannon.ProcessorFactory):
    def make(self, current=None):
        servant = ProcessorI()
        proxy = current.adapter.addWithUUID(servant)
        return Cannon.ProcessorPrx.checkedCast(proxy)

class ProcessorI(Cannon.Processor):


    def init(self, index, order, above, left, target, current=None):
        self.index=index
        self.order=order
        self.above=above
        self.left=left
        self.target=target
        self.order=order
        self.step=0
        self.matrixC=None
        self.matrixListA=[]
        self.matrixListB=[]
		self.matrix_is_multiply=[]
		self.mutexA=threading.Lock()
		self.mutexB=threading.Lock()
		self.mutexMultiply=threading.Lock()
		self.mutex_is_multiply=threading.Lock()
        for i in range(order):
            self.matrixListA.append(None)
            self.matrixListB.append(None)
			self.matrix_is_multiply.append(None)
        

    def injectA(self, A, step, current=None):

		if(step+1<self.order and self.left):
            self.left.begin_injectA(A, step+1)

		self.mutexA.acquire()
        self.matrixListA[step]= A
		self.mutexA.release()
		
		self.mutexB.acquire()
		self.mutex_is_multiply.acquire()
        if(self.matrixListB[step] and not self.matrix_is_multiply[step]):
			self.matrix_is_multiply[step]=1
            t = threading.Thread(target=self.multiply, args=(step, ))  
    		t.start()
		self.mutex_is_multiply.release()
		self.mutexB.release()

        

    def injectB(self, B, step, current=None):

		if(step+1<self.order and self.above):
            self.above.begin_injectB(B, step+1)
	
		self.mutexB.acquire()
        self.matrixListB[step]= B
		self.mutexB.release()

		self.mutexA.acquire()
		self.mutex_is_multiply.acquire()
        if(self.matrixListA[step] and not self.matrix_is_multiply[step]):

			self.matrix_is_multiply[step]=1
			t = threading.Thread(target=self.multiply, args=(step, ))  
    		t.start()

		self.mutex_is_multiply.release()
		self.mutexA.release()
        
    def multiply(self, indexStep):
		self.mutexMultiply.acquire()
        self.step+=1
        maux=matrix_multiply(self.matrixListA[indexStep], self.matrixListB[indexStep])

        if(self.matrixC):
            self.matrixC=matrix_add(maux, self.matrixC)
        else:
            self.matrixC=maux	

        if(self.step==self.order):
            self.target.begin_inject(self.index, self.matrixC)
		self.mutexMultiply.release()
    

class Server(Ice.Application):
    def run(self, args):
		index=0
        broker = self.communicator()
        servant = ProcessorFactoryI()

        adapter = broker.createObjectAdapter('ProcessorFactoryAdapter')
        factory = adapter.addWithUUID(servant)
		
		proxy = self.communicator().stringToProxy("IceGrid/Query")
		query = IceGrid.QueryPrx.checkedCast(proxy)
		tipo="::Services::Container"
		containerPrx = query.findObjectByType(tipo)

		container = Services.ContainerPrx.checkedCast(containerPrx)
		while True:
			try:
				container.link(str(index), factory)
				break
			except Services.AlreadyExists:
				index=index+1
		print(index)

        print('processorFactory ready: "{}"'.format(factory))
		sys.stdout.flush()
        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()


if __name__ == '__main__':
    app = Server()
    sys.exit(app.main(sys.argv))
