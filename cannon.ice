// No editar este fichero (vinculado al documento)

#include <Ice/BuiltinSequences.ice>

module Cannon {
  struct Matrix {
    int ncols;
    Ice::DoubleSeq data;
    string UUID;
  };

  interface Frontend {
    Matrix multiply(Matrix a, Matrix b);
  };

  interface Collector {
    void inject(int index, Matrix m);
  };

  interface Processor {
    void init(int index, int order,
	      Processor* above, Processor* left, Collector* target);
    void injectA(Matrix a, int step);
    void injectB(Matrix b, int step);
  };

  interface ProcessorFactory {
    Processor* make();
  };
};

module CannonTest {
  interface MatrixGenerator {
    void genMatrixPair(int order, out Cannon::Matrix A, out Cannon::Matrix B);
  };
};
