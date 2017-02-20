from ..base import basis,MAXPRINT
from ._constructors import kblock_Ns_estimate,op_array_size
from . import _check_1d_symm as _check
import numpy as _np
from numpy import array,cos,sin,exp,pi
from numpy.linalg import norm

import scipy.sparse as _sm

import warnings


# this is how we encode which fortran function to call when calculating 
# the action of operator string

_dtypes={"f":_np.float32,"d":_np.float64,"F":_np.complex64,"D":_np.complex128}
if hasattr(_np,"float128"): _dtypes["g"]=_np.float128
if hasattr(_np,"complex256"): _dtypes["G"]=_np.complex256


_basis_op_errors={1:"opstr character not recognized.",
				-1:"attemping to use real hamiltonian with complex matrix elements.",
				-2:"index of operator not between 0 <= index <= L-1"}



class OpstrError(Exception):
	# this class defines an exception which can be raised whenever there is some sort of error which we can
	# see will obviously break the code. 
	def __init__(self,message):
		self.message=message
	def __str__(self):
		return self.message



class basis_1d(basis):
	def __init__(self,ops,L,Np=None,_Np=None,pars=None,**blocks):

		if type(Np) is int:
			self._ops = ops
			self._check_pcon=True
			self._make_Np_block(L,Np=Np,pars=pars,**blocks)
	
		elif Np is None: # User hasn't specified Np,
			if _Np is not None: # check to see if photon_basis can create the particle sectors.

				if type(_Np) is not int:
					raise ValueError("Np must be integer")

				if _Np == -1: 
					self.__init__(L,_Np=None,pars=pars,**blocks)
				elif _Np >= 0:
					if _Np+1 > L: _Np = L
					blocks["count_particles"] = True

					zblock = blocks.get("zblock")
					zAblock = blocks.get("zAblock")
					zBblock = blocks.get("zAblock")
				
					if (type(zblock) is int) or (type(zAblock) is int) or (type(zBblock) is int):
						raise ValueError("spin inversion symmetry not compatible with particle conserving photon_basis.")
					
					# loop over the first Np particle sectors (use the iterator initialization).
					self.__init__(L,Np=range(_Np+1),pars=pars,**blocks)
				else:
					raise ValueError("_Np == -1 for no particle conservation, _Np >= 0 for particle conservation")

			else: # if _Np is None then assume user wants to not specify Magnetization sector
				self._ops = ops
				self._check_pcon = False
				self._make_Np_block(L,pars=pars,**blocks)


		else: # try to interate over Np 
			try:
				Nup_iter = iter(Np)
			except TypeError:
				raise TypeError("Np must be integer or iteratable object.")

			blocks["check_z_symm"] = False
			Np = next(Nup_iter)

			self._make_Np_block(L,Np=Np,pars=pars,**blocks)

			for Np in Nup_iter:
				temp_basis =self.__class__(L,Np,pars=pars,**blocks)
				self.append(temp_basis)	
		


				


	def _make_Np_block(self,L,Np=None,pars=None,**blocks):
		# getting arguments which are used in basis.
		kblock=blocks.get("kblock")
		zblock=blocks.get("zblock")
		zAblock=blocks.get("zAblock")
		zBblock=blocks.get("zBblock")
		pblock=blocks.get("pblock")
		pzblock=blocks.get("pzblock")
		a=blocks.get("a")

		count_particles = blocks.get("count_particles")
		if count_particles is None:
			count_particles=False

		check_z_symm = blocks.get("check_z_symm")
		if check_z_symm is None:
			check_z_symm=True


		if type(L) is not int:
			raise TypeError('L must be integer')




		if type(a) is not int:
			raise TypeError('a must be integer')

		# checking if a is compatible with L
		if(L%a != 0):
			raise ValueError('L must be interger multiple of lattice spacing a')


		# checking type, and value of blocks
		if Np is not None:
			if type(Np) is not int: raise TypeError('Np must be integer')
			if Np < 0 or Np > L: raise ValueError("0 <= Number of particles <= %d" % L)

		if pblock is not None:
			if type(pblock) is not int: raise TypeError('pblock must be integer')
			if abs(pblock) != 1: raise ValueError("pblock must be +/- 1")

		if zblock is not None:
			if type(zblock) is not int: raise TypeError('zblock must be integer')
			if abs(zblock) != 1: raise ValueError("zblock must be +/- 1")

		if zAblock is not None:
			if type(zAblock) is not int: raise TypeError('zAblock must be integer')
			if abs(zAblock) != 1: raise ValueError("zAblock must be +/- 1")

		if zBblock is not None:
			if type(zBblock) is not int: raise TypeError('zBblock must be integer')
			if abs(zBblock) != 1: raise ValueError("zBblock must be +/- 1")

		if pzblock is not None:
			if type(pzblock) is not int: raise TypeError('pzblock must be integer')
			if abs(pzblock) != 1: raise ValueError("pzblock must be +/- 1")

		if kblock is not None and (a < L):
			if type(kblock) is not int: raise TypeError('kblock must be integer')
			kblock = kblock % (L//a)
			blocks["kblock"] = kblock



		self._L = L
		self._Ns = self._ops.get_Ns(L,Np,**blocks)
		self._basis_type = self._ops.get_basis_type(L,Np,**blocks)
		self._pars = pars
		if type(kblock) is int: self._k = 2*(_np.pi)*a*kblock/L

		if type(Np) is int:
			self._conserved = "N"
		else:
			self._conserved = ""


		# shout out if pblock and zA/zB blocks defined simultaneously
		if type(pblock) is int and ((type(zAblock) is int) or (type(zBblock) is int)):
			raise ValueError("zA and zB symmetries incompatible with parity symmetry")

		if check_z_symm:
			blocks["Np"] = Np
			# checking if spin inversion is compatible with Np and L
			if (type(Np) is int) and ((type(zblock) is int) or (type(pzblock) is int)):
				if (L % 2) != 0:
					raise ValueError("spin inversion symmetry with magnetization conservation must be used with even number of sites")
				if Np != L//2:
					raise ValueError("spin inversion symmetry only reduces the 0 magnetization sector")

			if (type(Np) is int) and ((type(zAblock) is int) or (type(zBblock) is int)):
				raise ValueError("zA and zB symmetries incompatible with magnetisation symmetry")

			# checking if ZA/ZB spin inversion is compatible with unit cell of translation symemtry
			if (type(kblock) is int) and ((type(zAblock) is int) or (type(zBblock) is int)):
				if a%2 != 0: # T and ZA (ZB) symemtries do NOT commute
					raise ValueError("unit cell size 'a' must be even")




		self._blocks_1d = blocks
		self._unique_me = True	
		
		if (type(kblock) is int) and (type(pblock) is int) and (type(zblock) is int):
			if self._conserved: self._conserved += " & T & P & Z"
			else: self._conserved = "T & P & Z"

			self._blocks_1d["pzblock"] = pblock*zblock
			self._unique_me = False

			self._basis=_np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.t_p_z_op

			if self._basis_type == _np.object:
				self._N=_np.empty(self._basis.shape,dtype=_np.int32) 
				self._m=_np.empty(self._basis.shape,dtype=_np.int32)
			else:
				self._N=_np.empty(self._basis.shape,dtype=_np.int8) # normalisation*sigma
				self._m=_np.empty(self._basis.shape,dtype=_np.int16) #m = mp + (L+1)mz + (L+1)^2c; Anders' paper

			if (type(Np) is int):
				# arguments get overwritten by ops.spin_...  
				self._Ns = self._ops.n_t_p_z_basis(L,Np,pblock,zblock,kblock,a,self._pars,self._N,self._m,self._basis)
			else:
				self._Ns = self._ops.t_p_z_basis(L,pblock,zblock,kblock,a,self._pars,self._N,self._m,self._basis)

			# cut off extra memory for overestimated state number
			self._N.resize((self._Ns,))
			self._m.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._m,self._basis,self._L,self._pars]

		elif (type(kblock) is int) and (type(zAblock) is int) and (type(zBblock) is int):
			if self._conserved: self._conserved += " & T & ZA & ZB"
			else: self._conserved = "T & ZA & ZB"
			self._blocks_1d["zblock"] = zAblock*zBblock


			self._basis=_np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.t_zA_zB_op

			if self._basis_type == _np.object:
				self._N=_np.empty(self._basis.shape,dtype=_np.int32) 
				self._m=_np.empty(self._basis.shape,dtype=_np.int32)
			else:
				self._N=_np.empty(self._basis.shape,dtype=_np.int8)
				self._m=_np.empty(self._basis.shape,dtype=_np.int16)

			if (type(Np) is int):
				self._Ns = self._ops.n_t_zA_zB_basis(L,Np,zAblock,zBblock,kblock,a,self._pars,self._N,self._m,self._basis)
			else:
				self._Ns = self._ops.t_zA_zB_basis(L,zAblock,zBblock,kblock,a,self._pars,self._N,self._m,self._basis)

			self._N.resize((self._Ns,))
			self._m.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._m,self._basis,self._L,self._pars]

		elif (type(kblock) is int) and (type(pzblock) is int):
			if self._conserved: self._conserved += " & T & PZ"
			else: self._conserved = "T & PZ"
			self._unique_me = False

			self._basis=_np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.t_pz_op

			if self._basis_type == _np.object:
				self._N=_np.empty(self._basis.shape,dtype=_np.int32) 
				self._m=_np.empty(self._basis.shape,dtype=_np.int32)
			else:			
				self._N=_np.empty(self._basis.shape,dtype=_np.int8)
				self._m=_np.empty(self._basis.shape,dtype=_np.int8) #mpz

			if (type(Np) is int):
				self._Ns = self._ops.n_t_pz_basis(L,Np,pzblock,kblock,a,self._pars,self._N,self._m,self._basis)
			else:
				self._Ns = self._ops.t_pz_basis(L,pzblock,kblock,a,self._pars,self._N,self._m,self._basis)

			self._N.resize((self._Ns,))
			self._m.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._m,self._basis,self._L,self._pars]

		elif (type(kblock) is int) and (type(pblock) is int):
			if self._conserved: self._conserved += " & T & P"
			else: self._conserved = "T & P"
			self._unique_me = False

			self._basis=_np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.t_p_op

			if self._basis_type == _np.object:
				self._N=_np.empty(self._basis.shape,dtype=_np.int32) 
				self._m=_np.empty(self._basis.shape,dtype=_np.int32)
			else:			
				self._N=_np.empty(self._basis.shape,dtype=_np.int8)
				self._m=_np.empty(self._basis.shape,dtype=_np.int8)

			if (type(Np) is int):
				self._Ns = self._ops.n_t_p_basis(L,Np,pblock,kblock,a,self._pars,self._N,self._m,self._basis)
			else:
				self._Ns = self._ops.t_p_basis(L,pblock,kblock,a,self._pars,self._N,self._m,self._basis)


			self._N.resize((self._Ns,))
			self._m.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._m,self._basis,self._L,self._pars]

		elif (type(kblock) is int) and (type(zblock) is int):
			if self._conserved: self._conserved += " & T & Z"
			else: self._conserved = "T & Z"
			self._basis=_np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.t_z_op

			if self._basis_type == _np.object:
				self._N=_np.empty(self._basis.shape,dtype=_np.int32) 
				self._m=_np.empty(self._basis.shape,dtype=_np.int32)
			else:
				self._N=_np.empty(self._basis.shape,dtype=_np.int8)
				self._m=_np.empty(self._basis.shape,dtype=_np.int8)

			if (type(Np) is int):
				self._Ns = self._ops.n_t_z_basis(L,Np,zblock,kblock,a,self._pars,self._N,self._m,self._basis)
			else:
				self._Ns = self._ops.t_z_basis(L,zblock,kblock,a,self._pars,self._N,self._m,self._basis)

			self._N.resize((self._Ns,))
			self._m.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._m,self._basis,self._L,self._pars]


		elif (type(kblock) is int) and (type(zAblock) is int):
			if self._conserved: self._conserved += " & T & ZA"
			else: self._conserved = "T & ZA"
			self._basis=_np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.t_zA_op

			if self._basis_type == _np.object:
				self._N=_np.empty(self._basis.shape,dtype=_np.int32) 
				self._m=_np.empty(self._basis.shape,dtype=_np.int32)
			else:			
				self._N=_np.empty(self._basis.shape,dtype=_np.int8)
				self._m=_np.empty(self._basis.shape,dtype=_np.int8)

			if (type(Np) is int):
				self._Ns = self._ops.n_t_zA_basis(L,Np,zAblock,kblock,a,self._pars,self._N,self._m,self._basis)
			else:
				self._Ns = self._ops.t_zA_basis(L,zAblock,kblock,a,self._pars,self._N,self._m,self._basis)

			self._N.resize((self._Ns,))
			self._m.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._m,self._basis,self._L,self._pars]

		elif (type(kblock) is int) and (type(zBblock) is int):
			if self._conserved: self._conserved += " & T & ZB"
			else: self._conserved = "T & ZB"
			self._basis=_np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.t_zB_op

			if self._basis_type == _np.object:
				self._N=_np.empty(self._basis.shape,dtype=_np.int32) 
				self._m=_np.empty(self._basis.shape,dtype=_np.int32)
			else:			
				self._N=_np.empty(self._basis.shape,dtype=_np.int8)
				self._m=_np.empty(self._basis.shape,dtype=_np.int8)

			if (type(Np) is int):
				self._Ns = self._ops.n_t_zB_basis(L,Np,zBblock,kblock,a,self._pars,self._N,self._m,self._basis)
			else:
				self._Ns = self._ops.t_zB_basis(L,zBblock,kblock,a,self._pars,self._N,self._m,self._basis)

			self._N.resize((self._Ns,))
			self._m.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._m,self._basis,self._L,self._pars]

		elif (type(pblock) is int) and (type(zblock) is int):
			if self._conserved: self._conserved += " & P & Z"
			else: self._conserved += "P & Z"
			self._basis = _np.empty((self._Ns,),dtype=self._basis_type)
			self._N=_np.empty((self._Ns,),dtype=_np.int8)
			self._op = self._ops.p_z_op

			if (type(Np) is int):
				self._Ns = self._ops.n_p_z_basis(L,Np,pblock,zblock,self._pars,self._N,self._basis)
			else:
				self._Ns = self._ops.p_z_basis(L,pblock,zblock,self._pars,self._N,self._basis)

			self._N.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._basis,self._L,self._pars]


		elif (type(zAblock) is int) and (type(zBblock) is int):
			if self._conserved: self._conserved += " & ZA & ZB"
			else: self._conserved += "ZA & ZB"
			self._basis = _np.empty((self._Ns,),dtype=self._basis_type)
			if (type(Np) is int):
				self._Ns = self._ops.n_zA_zB_basis(L,Np,self._pars,self._basis)
			else:
				self._Ns = self._ops.zA_zB_basis(L,self._pars,self._basis)

			self._basis.resize((self._Ns,))
			self._op_args=[self._basis,self._L,self._pars]



		elif type(pblock) is int:
			if self._conserved: self._conserved += " & P"
			else: self._conserved = "P"
			self._basis = _np.empty((self._Ns,),dtype=self._basis_type)
			self._N=_np.empty((self._Ns,),dtype=_np.int8)
			self._op = self._ops.p_op

			if (type(Np) is int):
				self._Ns = self._ops.n_p_basis(L,Np,pblock,self._pars,self._N,self._basis)
			else:
				self._Ns = self._ops.p_basis(L,pblock,self._pars,self._N,self._basis)

			self._N.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._basis,self._L,self._pars]



		elif type(zblock) is int:
			if self._conserved: self._conserved += " & Z"
			else: self._conserved += "Z"
			self._basis = _np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.z_op

			if (type(Np) is int):
				self._Ns = self._ops.n_z_basis(L,Np,self._pars,self._basis)
			else:
				self._Ns = self._ops.z_basis(L,self._pars,self._basis)

			self._basis.resize((self._Ns,))
			self._op_args=[self._basis,self._L,self._pars]

		elif type(zAblock) is int:
			if self._conserved: self._conserved += " & ZA"
			else: self._conserved += "ZA"
			self._basis = _np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.zA_op

			if (type(Np) is int):
				self._Ns = self._ops.n_zA_basis(L,Np,self._pars,self._basis)
			else:
				self._Ns = self._ops.zA_basis(L,self._pars,self._basis)

			self._basis.resize((self._Ns,))
			self._op_args=[self._basis,self._L,self._pars]


		elif type(zBblock) is int:
			if self._conserved: self._conserved += " & ZB"
			else: self._conserved += "ZB"
			self._basis = _np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.zB_op

			if (type(Np) is int):
				self._Ns = self._ops.n_zB_basis(L,Np,self._pars,self._basis)
			else:
				self._Ns = self._ops.zB_basis(L,self._pars,self._basis)

			self._basis.resize((self._Ns,))
			self._op_args=[self._basis,self._L,self._pars]
				
		elif type(pzblock) is int:
			if self._conserved: self._conserved += " & PZ"
			else: self._conserved += "PZ"
			self._basis = _np.empty((self._Ns,),dtype=self._basis_type)
			self._N=_np.empty((self._Ns,),dtype=_np.int8)
			self._op = self._ops.pz_op

			if (type(Np) is int):
				self._Ns = self._ops.n_pz_basis(L,Np,pzblock,self._pars,self._N,self._basis)
			else:
				self._Ns = self._ops.pz_basis(L,pzblock,self._pars,self._N,self._basis)

			self._N.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._basis,self._L,self._pars]
	
		elif type(kblock) is int:
			if self._conserved: self._conserved += " & T"
			else: self._conserved = "T"
			self._basis=_np.empty((self._Ns,),dtype=self._basis_type)
			self._op = self._ops.t_op
			
			if self._basis_type == _np.object:
				self._N=_np.empty(self._basis.shape,dtype=_np.int32) 
			else:			
				self._N=_np.empty(self._basis.shape,dtype=_np.int8)

			if (type(Np) is int):
				self._Ns = self._ops.n_t_basis(L,Np,kblock,a,self._pars,self._N,self._basis)
			else:
				self._Ns = self._ops.t_basis(L,kblock,a,self._pars,self._N,self._basis)

			self._N.resize((self._Ns,))
			self._basis.resize((self._Ns,))
			self._op_args=[self._N,self._basis,self._L,self._pars]

		else: 
			if type(Np) is int:
				self._basis = _np.empty((self._Ns,),dtype=self._basis_type)
				self._ops.n_basis(L,Np,self._pars,self._Ns,self._basis)
			else:
				self._basis = _np.arange(0,self._Ns,1,dtype=self._basis_type)
			self._op_args=[self._basis]

		if count_particles: self._Np = _np.full_like(self._basis,Np,dtype=_np.int8)



	def append(self,other):
		if not isinstance(other,self.__class__):
			raise TypeError("can only append basis objects of the same type")
		if self._L != other._L:
			raise ValueError("appending incompatible system sizes with")
		if self._blocks_1d != other._blocks_1d:
			raise ValueError("appending incompatible blocks")
		

		Ns = self._Ns + other._Ns

		if self._conserved == "" or self._conserved == "M":
			self._op_args=[]
		else:
			self._op_args=[self._L]


		self._basis.resize((Ns,),refcheck=False)
		self._basis[self._Ns:] = other._basis[:]
		arg = _np.argsort(self._basis)
		self._basis = self._basis[arg]

		self._op_args.insert(0,self._basis)

		if hasattr(self,"_Np"):
			self._Np.resize((Ns,),refcheck=False)
			self._Np[self._Ns:] = other._Np[:]
			self._Np = self._Np[arg]

		if hasattr(self,"_m"):
			self._m.resize((Ns,),refcheck=False)
			self._m[self._Ns:] = other._m[:]
			self._m = self._m[arg]
			self._op_args.insert(0,self._m)	

		if hasattr(self,"_N"):
			self._N.resize((Ns,),refcheck=False)
			self._N[self._Ns:] = other._N[:]
			self._N = self._N[arg]
			self._op_args.insert(0,self._N)

		self._Ns = Ns

	@property
	def blocks(self):
		return self._blocks

	@property
	def L(self):
		return self._L

	@property
	def N(self):
		return self._L

	@property
	def conserved(self):
		return self._conserved

	@property
	def operators(self):
		return self._operators
	@property
	def m(self):
		return self._blocks_1d["m"]
	

	@property
	def description(self):
		blocks = ""
		lat_space = "lattice spacing: a = {a}".format(**self._blocks)

		for symm in self._blocks:
			if symm != "a":
				blocks += symm+" = {"+symm+"}, "

		blocks = blocks.format(**self._blocks)

		if len(self.conserved) == 0:
			symm = "no symmetry"
		elif len(self.conserved) == 1:
			symm = "symmetry"
		else:
			symm = "symmetries"

		string = """1d basis for chain of L = {0} containing {5} states \n\t{1}: {2} \n\tquantum numbers: {4} \n\t{3} \n\n""".format(self._L,symm,self._conserved,lat_space,blocks,self._Ns)
		string += self.operators
		return string 


	def _get_basis_type(L,Np,**blocks):
		raise NotImplementedError("specializations of basis_1d must implement _get_basis_type function which determines the dtype for the size of the integer representation.")

	def _get_Ns(L,Np,**blocks):
		raise NotImplementedError("specializations of basis_1d must implement _get_Ns function to estimate the size of the hilbert space given the symmetry sectors.")

	def __getitem__(self,key):
		return self._basis.__getitem__(key)

	def index(self,s):
		return _np.searchsorted(self._basis,s)

	def __iter__(self):
		return self._basis.__iter__()


	def Op(self,opstr,indx,J,dtype):
		indx = _np.asarray(indx,dtype=_np.int32)

		if len(opstr) != len(indx):
			raise ValueError('length of opstr does not match length of indx')
		if _np.any(indx >= self._L) or _np.any(indx < 0):
			raise ValueError('values in indx falls outside of system')

		if self._Ns <= 0:
			return [],[],[]

		N_op = op_array_size[self._conserved]*self.Ns
		col = _np.zeros(N_op,dtype=self._basis_type)
		row = _np.zeros(N_op,dtype=self._basis_type)
		ME = _np.zeros(N_op,dtype=dtype)

		error = self._op(row,col,ME,opstr,indx,J,*self._op_args,**self._blocks_1d)

		if error != 0: raise OpstrError(_basis_op_errors[error])

		mask = _np.logical_not(_np.isnan(ME))
		col = col[mask]
		row = row[mask]
		ME = ME[mask]

		return ME,row,col		



	def get_norms(self,dtype):
		a = self._blocks_1d.get("a")
		kblock = self._blocks_1d.get("kblock")
		pblock = self._blocks_1d.get("pblock")
		zblock = self._blocks_1d.get("zblock")
		zAblock = self._blocks_1d.get("zAblock")
		zBblock = self._blocks_1d.get("zBblock")
		pzblock = self._blocks_1d.get("pzblock")


		if (type(kblock) is int) and (type(pblock) is int) and (type(zblock) is int):
			c = _np.empty(self._m.shape,dtype=_np.int8)
			nn = array(c)
			mm = array(c)
			_np.floor_divide(self._m,(self._L+1)**2,out=c)
			_np.floor_divide(self._m,self._L+1,out=nn)
			_np.mod(nn,self._L+1,out=nn)
			_np.mod(self._m,self._L+1,out=mm)
			if _np.abs(_np.sin(self._k)) < 1.0/self._L:
				norm = _np.full(self._basis.shape,4*(self._L/a)**2,dtype=dtype)
			else:
				norm = _np.full(self._basis.shape,2*(self._L/a)**2,dtype=dtype)
			norm *= _np.sign(self._N)
			norm /= self._N
			# c = 2
			mask = (c == 2)
			norm[mask] *= (1.0 + _np.sign(self._N[mask])*pblock*_np.cos(self._k*mm[mask]))
			# c = 3
			mask = (c == 3)
			norm[mask] *= (1.0 + zblock*_np.cos(self._k*nn[mask]))	
			# c = 4
			mask = (c == 4)
			norm[mask] *= (1.0 + _np.sign(self._N[mask])*pzblock*_np.cos(self._k*mm[mask]))	
			# c = 5
			mask = (c == 5)
			norm[mask] *= (1.0 + _np.sign(self._N[mask])*pblock*_np.cos(self._k*mm[mask]))
			norm[mask] *= (1.0 + zblock*_np.cos(self._k*nn[mask]))	
			del mask
		elif (type(kblock) is int) and (type(zAblock) is int) and (type(zBblock) is int):
			c = _np.empty(self._m.shape,dtype=_np.int8)
			mm = array(c)
			_np.floor_divide(self._m,(self._L+1),c)
			_np.mod(self._m,self._L+1,mm)
			norm = _np.full(self._basis.shape,4*(self._L/a)**2,dtype=dtype)
			norm /= self._N
			# c = 2
			mask = (c == 2)
			norm[mask] *= (1.0 + zAblock*_np.cos(self._k*mm[mask]))
			# c = 3
			mask = (c == 3)
			norm[mask] *= (1.0 + zBblock*_np.cos(self._k*mm[mask]))	
			# c = 4
			mask = (c == 4)
			norm[mask] *= (1.0 + zblock*_np.cos(self._k*mm[mask]))	
			del mask
		elif (type(kblock) is int) and (type(pblock) is int):
			if _np.abs(_np.sin(self._k)) < 1.0/self._L:
				norm = _np.full(self._basis.shape,2*(self._L/a)**2,dtype=dtype)
			else:
				norm = _np.full(self._basis.shape,(self._L/a)**2,dtype=dtype)
			norm *= _np.sign(self._N)
			norm /= self._N
			# m >= 0 
			mask = (self._m >= 0)
			norm[mask] *= (1.0 + _np.sign(self._N[mask])*pblock*_np.cos(self._k*self._m[mask]))
			del mask
		elif (type(kblock) is int) and (type(pzblock) is int):
			if _np.abs(_np.sin(self._k)) < 1.0/self._L:
				norm = _np.full(self._basis.shape,2*(self._L/a)**2,dtype=dtype)
			else:
				norm = _np.full(self._basis.shape,(self._L/a)**2,dtype=dtype)
			norm *= _np.sign(self._N)
			norm /= self._N
			# m >= 0 
			mask = (self._m >= 0)
			norm[mask] *= (1.0 + _np.sign(self._N[mask])*pzblock*_np.cos(self._k*self._m[mask]))
			del mask
		elif (type(kblock) is int) and (type(zblock) is int):
			norm = _np.full(self._basis.shape,2*(self._L/a)**2,dtype=dtype)
			norm /= self._N
			# m >= 0 
			mask = (self._m >= 0)
			norm[mask] *= (1.0 + zblock*_np.cos(self._k*self._m[mask]))
			del mask
		elif (type(kblock) is int) and (type(zAblock) is int):
			norm = _np.full(self._basis.shape,2*(self._L/a)**2,dtype=dtype)
			norm /= self._N
			# m >= 0 
			mask = (self._m >= 0)
			norm[mask] *= (1.0 + zAblock*_np.cos(self._k*self._m[mask]))
			del mask
		elif (type(kblock) is int) and (type(zBblock) is int):
			norm = _np.full(self._basis.shape,2*(self._L/a)**2,dtype=dtype)
			norm /= self._N
			# m >= 0 
			mask = (self._m >= 0)
			norm[mask] *= (1.0 + zBblock*_np.cos(self._k*self._m[mask]))
			del mask
		elif (type(pblock) is int) and (type(zblock) is int):
			norm = array(self._N,dtype=dtype)
		elif (type(zAblock) is int) and (type(zBblock) is int):
			norm = _np.full(self._basis.shape,4.0,dtype=dtype)
		elif (type(pblock) is int):
			norm = array(self._N,dtype=dtype)
		elif (type(pzblock) is int):
			norm = array(self._N,dtype=dtype)
		elif (type(zblock) is int):
			norm = _np.full(self._basis.shape,2.0,dtype=dtype)
		elif (type(zAblock) is int):
			norm = _np.full(self._basis.shape,2.0,dtype=dtype)
		elif (type(zBblock) is int):
			norm = _np.full(self._basis.shape,2.0,dtype=dtype)
		elif (type(kblock) is int):
			norm = _np.full(self._basis.shape,(self._L/a)**2,dtype=dtype)
			norm /= self._N
		else:
			norm = _np.ones(self._basis.shape,dtype=dtype)
	
		_np.sqrt(norm,norm)

		return norm




	def get_vec(self,v0,sparse=True):
		if _sm.issparse(v0):
			raise TypeError("expecting v0 to be dense array")

		if not hasattr(v0,"shape"):
			v0 = _np.asanyarray(v0)

		if self._Ns <= 0:
			return array([])
		if v0.ndim == 1:
			ravel=True
			shape = (2**self._L,1)
			v0 = v0.reshape((-1,1))
		elif v0.ndim == 2:
			ravel=False
			shape = (2**self._L,v0.shape[1])
		else:
			raise ValueError("excpecting v0 to have ndim at most 2")

		if v0.shape[0] != self._Ns:
			raise ValueError("v0 shape {0} not compatible with Ns={1}".format(v0.shape,self._Ns))


		norms = self.get_norms(v0.dtype)

		a = self._blocks_1d.get("a")
		kblock = self._blocks_1d.get("kblock")
		pblock = self._blocks_1d.get("pblock")
		zblock = self._blocks_1d.get("zblock")
		zAblock = self._blocks_1d.get("zAblock")
		zBblock = self._blocks_1d.get("zBblock")
		pzblock = self._blocks_1d.get("pzblock")


		if (type(kblock) is int) and ((type(pblock) is int) or (type(pzblock) is int)):
			mask = (self._N < 0)
			ind_neg, = _np.nonzero(mask)
			mask = (self._N > 0)
			ind_pos, = _np.nonzero(mask)
			del mask
			def C(r,k,c,norms,dtype,ind_neg,ind_pos):
				c[ind_pos] = cos(dtype(k*r))
				c[ind_neg] = -sin(dtype(k*r))
				_np.true_divide(c,norms,c)
		else:
			ind_pos = _np.fromiter(range(v0.shape[0]),count=v0.shape[0],dtype=_np.int32)
			ind_neg = array([],dtype=_np.int32)
			def C(r,k,c,norms,dtype,*args):
				if k == 0.0:
					c[:] = 1.0
				elif k == _np.pi:
					c[:] = (-1.0)**r
				else:
					c[:] = exp(dtype(1.0j*k*r))
				_np.true_divide(c,norms,c)

		if sparse:
			return _get_vec_sparse(self._ops,self._pars,v0,self._basis,norms,ind_neg,ind_pos,shape,C,self._L,**self._blocks_1d)
		else:
			if ravel:
				return  _get_vec_dense(self._ops,self._pars,v0,self._basis,norms,ind_neg,ind_pos,shape,C,self._L,**self._blocks_1d).ravel()
			else:
				return  _get_vec_dense(self._ops,self._pars,v0,self._basis,norms,ind_neg,ind_pos,shape,C,self._L,**self._blocks_1d)


	def get_proj(self,dtype):
		if self._Ns <= 0:
			return array([])

		norms = self.get_norms(dtype)

		a = self._blocks_1d.get("a")
		kblock = self._blocks_1d.get("kblock")
		pblock = self._blocks_1d.get("pblock")
		zblock = self._blocks_1d.get("zblock")
		zAblock = self._blocks_1d.get("zAblock")
		zBblock = self._blocks_1d.get("zBblock")
		pzblock = self._blocks_1d.get("pzblock")

		if (type(kblock) is int) and ((type(pblock) is int) or (type(pzblock) is int)):
			mask = (self._N < 0)
			ind_neg, = _np.nonzero(mask)
			mask = (self._N > 0)
			ind_pos, = _np.nonzero(mask)
			del mask
			def C(r,k,c,norms,dtype,ind_neg,ind_pos):
				c[ind_pos] = cos(dtype(k*r))
				c[ind_neg] = -sin(dtype(k*r))
				_np.true_divide(c,norms,c)
		else:
			if (type(kblock) is int):
				if ((2*kblock*a) % self._L != 0) and not _np.iscomplexobj(dtype(1.0)):
					raise TypeError("symmetries give complex vector, requested dtype is not complex")

			ind_pos = _np.arange(0,self._Ns,1)
			ind_neg = array([],dtype=_np.int32)
			def C(r,k,c,norms,dtype,*args):
				if k == 0.0:
					c[:] = 1.0
				elif k == _np.pi:
					c[:] = (-1.0)**r
				else:
					c[:] = exp(dtype(1.0j*k*r))
				_np.true_divide(c,norms,c)

		return _get_proj_sparse(self._ops,self._pars,self._basis,norms,ind_neg,ind_pos,dtype,C,self._L,**self._blocks_1d)









	def _check_symm(self,static,dynamic,basis=None):
		kblock = self._blocks_1d.get("kblock")
		pblock = self._blocks_1d.get("pblock")
		zblock = self._blocks_1d.get("zblock")
		pzblock = self._blocks_1d.get("pzblock")
		zAblock = self._blocks_1d.get("zAblock")
		zBblock = self._blocks_1d.get("zBblock")
		a = self._blocks_1d.get("a")
		L = self.L

		if basis is None:
			basis = self

		static_list,dynamic_list = basis.get_lists(static,dynamic)

		static_blocks = {}
		dynamic_blocks = {}
		if kblock is not None:
			missingops = _check.check_T(basis,static_list,L,a)
			if missingops:	static_blocks["T symm"] = (tuple(missingops),)

			missingops = _check.check_T(basis,dynamic_list,L,a)
			if missingops:	dynamic_blocks["T symm"] = (tuple(missingops),)

		if pblock is not None:
			missingops = _check.check_P(basis,static_list,L)
			if missingops:	static_blocks["P symm"] = (tuple(missingops),)

			missingops = _check.check_P(basis,dynamic_list,L)
			if missingops:	dynamic_blocks["P symm"] = (tuple(missingops),)

		if zblock is not None:
			oddops,missingops = _check.check_Z(basis,static_list)
			if missingops or oddops:
				static_blocks["Z symm"] = (tuple(oddops),tuple(missingops))

			oddops,missingops = _check.check_Z(basis,dynamic_list)
			if missingops or oddops:
				dynamic_blocks["Z symm"] = (tuple(oddops),tuple(missingops))

		if zAblock is not None:
			oddops,missingops = _check.check_ZA(basis,static_list)
			if missingops or oddops:
				static_blocks["ZA symm"] = (tuple(oddops),tuple(missingops))

			oddops,missingops = _check.check_ZA(basis,dynamic_list)
			if missingops or oddops:
				dynamic_blocks["ZA symm"] = (tuple(oddops),tuple(missingops))

		if zBblock is not None:
			oddops,missingops = _check.check_ZB(basis,static_list)
			if missingops or oddops:
				static_blocks["ZB symm"] = (tuple(oddops),tuple(missingops))

			oddops,missingops = _check.check_ZB(basis,dynamic_list)
			if missingops or oddops:
				dynamic_blocks["ZB symm"] = (tuple(oddops),tuple(missingops))

		if pzblock is not None:
			missingops = _check.check_PZ(basis,static_list,L)
			if missingops:	static_blocks["PZ symm"] = (tuple(missingops),)

			missingops = _check.check_PZ(basis,dynamic_list,L)
			if missingops:	dynamic_blocks["PZ symm"] = (tuple(missingops),)

		return static_blocks,dynamic_blocks








def _get_vec_dense(ops,pars,v0,basis,norms,ind_neg,ind_pos,shape,C,L,**blocks):
	dtype=_dtypes[v0.dtype.char]

	a = blocks.get("a")
	kblock = blocks.get("kblock")
	pblock = blocks.get("pblock")
	zblock = blocks.get("zblock")
	zAblock = blocks.get("zAblock")
	zBblock = blocks.get("zBblock")
	pzblock = blocks.get("pzblock")


	c = _np.zeros(basis.shape,dtype=v0.dtype)	
	v = _np.zeros(shape,dtype=v0.dtype)

	bits=" ".join(["{"+str(i)+":0"+str(L)+"b}" for i in range(len(basis))])

	if type(kblock) is int:
		k = 2*_np.pi*kblock*a/L
	else:
		k = 0.0
		a = L

	for r in range(0,L//a):
		C(r,k,c,norms,dtype,ind_neg,ind_pos)	
		vc = (v0.T*c).T
		v[basis[ind_pos]] += vc[ind_pos]
		v[basis[ind_neg]] += vc[ind_neg]

		if type(zAblock) is int:
			ops.py_flip_sublat_A(basis,L,pars)
			v[basis[ind_pos]] += vc[ind_pos]*zAblock
			v[basis[ind_neg]] += vc[ind_neg]*zAblock
			ops.py_flip_sublat_A(basis,L,pars)
		
		if type(zBblock) is int:
			ops.py_flip_sublat_B(basis,L,pars)
			v[basis[ind_pos]] += vc[ind_pos]*zBblock
			v[basis[ind_neg]] += vc[ind_neg]*zBblock
			ops.py_flip_sublat_B(basis,L,pars)
		
		if type(zblock) is int:
			ops.py_flip_all(basis,L,pars)
			v[basis[ind_pos]] += vc[ind_pos]*zblock
			v[basis[ind_neg]] += vc[ind_neg]*zblock
			ops.py_flip_all(basis,L,pars)

		if type(pblock) is int:
			ops.py_fliplr(basis,L,pars)
			v[basis[ind_pos]] += vc[ind_pos]*pblock
			v[basis[ind_neg]] += vc[ind_neg]*pblock
			ops.py_fliplr(basis,L,pars)

		if type(pzblock) is int:
			ops.py_fliplr(basis,L,pars)
			ops.py_flip_all(basis,L,pars)
			v[basis[ind_pos]] += vc[ind_pos]*pzblock
			v[basis[ind_neg]] += vc[ind_neg]*pzblock
			ops.py_fliplr(basis,L,pars)
			ops.py_flip_all(basis,L,pars)
		
		ops.py_shift(basis,a,L,pars)
	
	return v





def _get_vec_sparse(ops,pars,v0,basis,norms,ind_neg,ind_pos,shape,C,L,**blocks):
	dtype=_dtypes[v0.dtype.char]

	a = blocks.get("a")
	kblock = blocks.get("kblock")
	pblock = blocks.get("pblock")
	zblock = blocks.get("zblock")
	zAblock = blocks.get("zAblock")
	zBblock = blocks.get("zBblock")
	pzblock = blocks.get("pzblock")

	m = shape[1]


	
	if ind_neg.shape[0] == 0:
		row_neg = array([],dtype=_np.int64)
		col_neg = array([],dtype=_np.int64)
	else:
		col_neg = _np.arange(0,m,1)
		row_neg = _np.kron(ind_neg,_np.ones_like(col_neg))
		col_neg = _np.kron(_np.ones_like(ind_neg),col_neg)

	if ind_pos.shape[0] == 0:
		row_pos = array([],dtype=_np.int64)
		col_pos = array([],dtype=_np.int64)
	else:
		col_pos = _np.arange(0,m,1)
		row_pos = _np.kron(ind_pos,_np.ones_like(col_pos))
		col_pos = _np.kron(_np.ones_like(ind_pos),col_pos)



	if type(kblock) is int:
		k = 2*_np.pi*kblock*a/L
	else:
		k = 0.0
		a = L

	c = _np.zeros(basis.shape,dtype=v0.dtype)	
	v = _sm.csr_matrix(shape,dtype=v0.dtype)



	for r in range(0,L//a):
		C(r,k,c,norms,dtype,ind_neg,ind_pos)

		vc = (v0.T*c).T
		data_pos = vc[ind_pos].flatten()
		data_neg = vc[ind_neg].flatten()
		v = v + _sm.csr_matrix((data_pos,(basis[row_pos],col_pos)),shape,dtype=v.dtype)
		v = v + _sm.csr_matrix((data_neg,(basis[row_neg],col_neg)),shape,dtype=v.dtype)

		if type(zAblock) is int:
			ops.py_flip_sublat_A(basis,L,pars)
			data_pos *= zAblock
			data_neg *= zAblock
			v = v + _sm.csr_matrix((data_pos,(basis[row_pos],col_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[row_neg],col_neg)),shape,dtype=v.dtype)
			data_pos *= zAblock
			data_neg *= zAblock
			ops.py_flip_sublat_A(basis,L,pars)

		if type(zBblock) is int:
			ops.py_flip_sublat_B(basis,L,pars)
			data_pos *= zBblock
			data_neg *= zBblock
			v = v + _sm.csr_matrix((data_pos,(basis[row_pos],col_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[row_neg],col_neg)),shape,dtype=v.dtype)
			data_pos *= zBblock
			data_neg *= zBblock
			ops.py_flip_sublat_B(basis,L,pars)

		if type(zblock) is int:
			ops.py_flip_all(basis,L,pars)
			data_pos *= zblock
			data_neg *= zblock
			v = v + _sm.csr_matrix((data_pos,(basis[row_pos],col_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[row_neg],col_neg)),shape,dtype=v.dtype)
			data_pos *= zblock
			data_neg *= zblock
			ops.py_flip_all(basis,L,pars)

		if type(pblock) is int:
			ops.py_fliplr(basis,L,pars)
			data_pos *= pblock
			data_neg *= pblock
			v = v + _sm.csr_matrix((data_pos,(basis[row_pos],col_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[row_neg],col_neg)),shape,dtype=v.dtype)
			data_pos *= pblock
			data_neg *= pblock
			ops.py_fliplr(basis,L,pars)

		if type(pzblock) is int:
			ops.py_fliplr(basis,L,pars)
			ops.py_flip_all(basis,L,pars)
			data_pos *= pzblock
			data_neg *= pzblock
			v = v + _sm.csr_matrix((data_pos,(basis[row_pos],col_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[row_neg],col_neg)),shape,dtype=v.dtype)
			data_pos *= pzblock
			data_neg *= pzblock
			ops.py_fliplr(basis,L,pars)
			ops.py_flip_all(basis,L,pars)

		v.sum_duplicates()
		v.eliminate_zeros()
		ops.py_shift(basis,a,L,pars)

	return v




def _get_proj_sparse(ops,pars,basis,norms,ind_neg,ind_pos,dtype,C,L,**blocks):

	a = blocks.get("a")
	kblock = blocks.get("kblock")
	pblock = blocks.get("pblock")
	zblock = blocks.get("zblock")
	zAblock = blocks.get("zAblock")
	zBblock = blocks.get("zBblock")
	pzblock = blocks.get("pzblock")


	if type(kblock) is int:
		k = 2*_np.pi*kblock*a/L
	else:
		k = 0.0
		a = L

	shape = (2**L,basis.shape[0])

	c = _np.zeros(basis.shape,dtype=dtype)	
	v = _sm.csr_matrix(shape,dtype=dtype)


	for r in range(0,L//a):
		C(r,k,c,norms,dtype,ind_neg,ind_pos)
		data_pos = c[ind_pos]
		data_neg = c[ind_neg]
		v = v + _sm.csr_matrix((data_pos,(basis[ind_pos],ind_pos)),shape,dtype=v.dtype)
		v = v + _sm.csr_matrix((data_neg,(basis[ind_neg],ind_neg)),shape,dtype=v.dtype)

		if type(zAblock) is int:
			ops.py_flip_sublat_A(basis,L,pars)
			data_pos *= zAblock
			data_neg *= zAblock
			v = v + _sm.csr_matrix((data_pos,(basis[ind_pos],ind_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[ind_neg],ind_neg)),shape,dtype=v.dtype)
			data_pos *= zAblock
			data_neg *= zAblock
			ops.py_flip_sublat_A(basis,L,pars)

		if type(zBblock) is int:
			ops.py_flip_sublat_B(basis,L,pars)
			data_pos *= zBblock
			data_neg *= zBblock
			v = v + _sm.csr_matrix((data_pos,(basis[ind_pos],ind_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[ind_neg],ind_neg)),shape,dtype=v.dtype)
			data_pos *= zBblock
			data_neg *= zBblock
			ops.py_flip_sublat_B(basis,L,pars)

		if type(zblock) is int:
			ops.py_flip_all(basis,L,pars)
			data_pos *= zblock
			data_neg *= zblock
			v = v + _sm.csr_matrix((data_pos,(basis[ind_pos],ind_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[ind_neg],ind_neg)),shape,dtype=v.dtype)
			data_pos *= zblock
			data_neg *= zblock
			ops.py_flip_all(basis,L,pars)

		if type(pblock) is int:
			ops.py_fliplr(basis,L,pars)
			data_pos *= pblock
			data_neg *= pblock
			v = v + _sm.csr_matrix((data_pos,(basis[ind_pos],ind_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[ind_neg],ind_neg)),shape,dtype=v.dtype)
			data_pos *= pblock
			data_neg *= pblock
			ops.py_fliplr(basis,L,pars)

		if type(pzblock) is int:
			ops.py_fliplr(basis,L,pars)
			ops.py_flip_all(basis,L,pars)
			data_pos *= pzblock
			data_neg *= pzblock
			v = v + _sm.csr_matrix((data_pos,(basis[ind_pos],ind_pos)),shape,dtype=v.dtype)
			v = v + _sm.csr_matrix((data_neg,(basis[ind_neg],ind_neg)),shape,dtype=v.dtype)
			data_pos *= pzblock
			data_neg *= pzblock
			ops.py_fliplr(basis,L,pars)
			ops.py_flip_all(basis,L,pars)

		ops.py_shift(basis,a,L,pars)


	return v



