#!python
#cython: boundscheck=False
#cython: wraparound=False
# distutils: language=c++


cimport numpy as _np
from libc.math cimport sin,cos,sqrt
from numpy.math cimport sinl,cosl,sqrtl

from types cimport *


import numpy as _np
from .basis_ops import H_dim,get_Ns,get_basis_type
from scipy.misc import comb

_np.import_array()

include "sources/hcp_bitops.pyx"
include "sources/refstate.pyx"
include "sources/op_templates.pyx"
include "sources/hcp_ops.pyx"
