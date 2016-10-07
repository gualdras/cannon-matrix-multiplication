# -*- mode:python; coding:utf-8; tab-width:4 -*-

import Ice
Ice.loadSlice('-I {} cannon.ice'.format(Ice.getSliceDir()))
import Cannon
from numpy import matrix
import math
import itertools


def matrix_multiply(A, B):
    order = A.ncols
    C = Cannon.Matrix(order, [])

    for i, j in itertools.product(xrange(order), repeat=2):
        C.data.append(
            sum(A.data[i * order + k] * B.data[k * order + j] for k in xrange(order))
        )

    return C

def matrix_add(A, B):
    matrixA=matrix(A.data)
    matrixA=matrixA.reshape(-1, A.ncols)
    matrixB=matrix(B.data)
    matrixB=matrixB.reshape(-1, B.ncols)
    matrixC=matrixA + matrixB
    matrixC=matrixC.reshape(1,-1)
    matrixC=matrixC.tolist()
    m_result=Cannon.Matrix(A.ncols, matrixC[0])
    return m_result

def list_split(M, n):
    matriz=matrix(M)
    matriz=matriz.reshape(-1,n)
    matriz=matriz.tolist()
    return matriz


def matrix_split(M, block_order):
    matrizM=matrix(M.data)
    matrizM=matrizM.reshape(-1,M.ncols)
    blocks=[]
    for i in range(M.ncols/block_order):
        for j in range(M.ncols/block_order):
            data=matrizM[i*block_order:i*block_order+block_order, j*block_order:j*block_order+block_order]
            data=data.reshape(1,-1)
            data=data.tolist()  
            m_aux=Cannon.Matrix(block_order, data[0])
            blocks.append(m_aux)
            
    return blocks

def matrix_horizontal_shift(M, block_order):
    lista_sub_m=matrix_split(M, block_order)
    subm_order=M.ncols/block_order
    lista_sub_m=matrix(lista_sub_m)
    lista_sub_m=lista_sub_m.reshape(-1,subm_order)
    laux=lista_sub_m.copy()
    for i in range(subm_order):
        for j in range(subm_order):
            lista_sub_m[i,(j-i)%subm_order]=laux[i,j]

    lista_sub_m=lista_sub_m.reshape(1,-1)
    lista_sub_m=lista_sub_m.tolist()
    lista_sub_m=lista_sub_m[0]    
    return matrix_join(*lista_sub_m)
    

def matrix_vertical_shift(M, block_order):
    lista_sub_m=matrix_split(M, block_order)
    subm_order=M.ncols/block_order
    lista_sub_m=matrix(lista_sub_m)
    lista_sub_m=lista_sub_m.reshape(-1,subm_order)
    laux=lista_sub_m.copy()
    for i in range(subm_order):
        for j in range(subm_order):
            lista_sub_m[(i-j)%subm_order,j]=laux[i,j]
	
    lista_sub_m=lista_sub_m.reshape(1,-1)
    lista_sub_m=lista_sub_m.tolist()
    lista_sub_m=lista_sub_m[0]    
        
    return matrix_join(*lista_sub_m)


def matrix_join(*lista_sub_m):
    block_order=lista_sub_m[0].ncols
    subm_order=int(math.sqrt(len(lista_sub_m)))
    ncols=lista_sub_m[0].ncols * subm_order
    lista_sub_m=matrix(lista_sub_m)        
    lista_sub_m=lista_sub_m.reshape(-1, subm_order)
    resultado=[]
    for i in range(subm_order):
		fila_sub_m=lista_sub_m[i,:]	
		fila_sub_m=fila_sub_m.tolist()
		fila_sub_m=fila_sub_m[0]

		for k in range(block_order):
			for j in range(subm_order):
				block=fila_sub_m[j]
				blockM=matrix(block.data)
				blockM=blockM.reshape(-1,block_order)
				blockM=blockM[k,:]
				block=blockM.tolist()
				block=block[0]
				resultado.append(block)

    resultado=sum(resultado, [])
    matriz_result=Cannon.Matrix(ncols, resultado)
    return matriz_result
    
