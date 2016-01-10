from exact_diag_py.spins import hamiltonian
from exact_diag_py.basis import basis1d
import numpy as np
from scipy.linalg import norm
from numpy.random import random,seed

seed()
np.set_printoptions(precision=3,suppress=True, linewidth=100000)


def check_opstr(Lmax):
	for dtype in (np.float32,np.float64,np.complex64,np.complex128):
		for L in xrange(2,Lmax+1):
			h=[[2.0*random()-1.0,i] for i in xrange(L)]
			J1=[[2.0*random()-1.0,i,(i+1)%L] for i in xrange(L)]
			J2=[[2.0*random()-1.0,i,(i+1)%L] for i in xrange(L)]
			J3=[[J2[i][0]*0.5,i,(i+1)%L] for i in xrange(L)]

			static1=[["zz",J1],["yy",J2],["xx",J2],["x",h]]
			static2=[["zz",J1],["+-",J3],["-+",J3],["x",h]]

			eps=np.finfo(dtype).eps

			H1=hamiltonian(static1,[],L,dtype=dtype)
			H2=hamiltonian(static2,[],L,dtype=dtype) 

			if norm(H1.todense()-H2.todense()) > eps:
				raise Exception( "test failed opstr at L={0:3d} with dtype {1}".format(L,np.dtype(dtype)) )






def check_m(Lmax):
	for dtype in (np.float32,np.float64,np.complex64,np.complex128):
		for L in xrange(2,Lmax+1):
			h=[[2.0*random()-1.0,i] for i in xrange(L)]
			J1=[[2.0*random()-1.0,i,(i+1)%L] for i in xrange(L)]
			J2=[[2.0*random()-1.0,i,(i+1)%L] for i in xrange(L)]

			static=[["zz",J1],["yy",J2],["xx",J2],["z",h]]

			H=hamiltonian(static,[],L,dtype=dtype)
			Ns=H.Ns
			E=H.eigvalsh()

			Em=[]
			for Nup in xrange(L+1):
				H=hamiltonian(static,[],L,Nup=Nup,dtype=dtype)
				Etemp=H.eigvalsh()
				Em.append(Etemp)

			Em=np.concatenate(Em)
			Em.sort()
			
			eps=np.finfo(dtype).eps
			if np.sum(np.abs(Em-E))/Ns > 100*eps:
				raise Exception( "test failed m symmetry at L={0:3d} with dtype {1}".format(L,np.dtype(dtype)) )


def check_z(L,dtype,Nup=None):
	if type(Nup) is int:
		J1=[[2.0*random()-1.0,i,(i+1)%L] for i in xrange(L-1)]
		J2=[[2.0*random()-1.0,i,(i+1)%L] for i in xrange(L-1)]
		static=[["zz",J1],["yy",J2],["xx",J2]]
	else:
		h=[[2.0*random()-1.0,i] for i in xrange(L)]
		J1=[[2.0*random()-1.0,i,(i+1)%L] for i in xrange(L-1)]
		J2=[[2.0*random()-1.0,i,(i+1)%L] for i in xrange(L-1)]
		static=[["zz",J1],["x",h]]


	

	H=hamiltonian(static,[],L,Nup=Nup,dtype=dtype)
	Ns=H.Ns
	E=H.eigvalsh()

	H1=hamiltonian(static,[],L,Nup=Nup,zblock=1,dtype=dtype)
	H2=hamiltonian(static,[],L,Nup=Nup,zblock=-1,dtype=dtype)


	E1=H1.eigvalsh()
	E2=H2.eigvalsh()
	
	Ez=np.concatenate((E1,E2))
	Ez.sort()

	eps=np.finfo(dtype).eps
	if np.sum(np.abs(Ez-E))/Ns > 100*eps:
		raise Exception( "test failed z symmetry at L={0:3d} with dtype {1} and Nup={2}".format(L,np.dtype(dtype),Nup) )



def check_p(L,dtype,Nup=None):
	hr=[2.0*random()-1.0 for i in xrange(int(L/2))]
	hi=[hr[i] for i in xrange(int(L/2))]
	hi.reverse()
	hi.extend(hr)
	
	h=[[hi[i],i] for i in xrange(L)]
	J=[[1.0,i,(i+1)%L] for i in xrange(L-1)]

	if type(Nup) is int:
		static=[["zz",J],["yy",J],["xx",J],["z",h]]
	else:
		static=[["zz",J],["x",h]]

	H=hamiltonian(static,[],L,Nup=Nup,dtype=dtype)
	Ns=H.Ns
	E=H.eigvalsh()

	H1=hamiltonian(static,[],L,Nup=Nup,pblock=1,dtype=dtype)
	H2=hamiltonian(static,[],L,Nup=Nup,pblock=-1,dtype=dtype)

	E1=H1.eigvalsh()
	E2=H2.eigvalsh()
	
	Ep=np.concatenate((E1,E2))
	Ep.sort()

	eps=np.finfo(dtype).eps
	if np.sum(np.abs(Ep-E)/Ns) > 100*eps:
		raise Exception( "test failed p symmetry at L={0:3d} with dtype {1} and Nup={2}".format(L,np.dtype(dtype),Nup) )




def check_pz(L,dtype,Nup=None):
	hr=[(i+0.1)**2/float(L**2) for i in xrange(int(L/2))]
	hi=[-(i+0.1)**2/float(L**2) for i in xrange(int(L/2))]
	hi.reverse()
	hi.extend(hr)

	h=[[hi[i],i] for i in xrange(L)]
	J=[[1.0,i,(i+1)%L] for i in xrange(L-1)]

	static=[["zz",J],["yy",J],["xx",J],["z",h]]

	H=hamiltonian(static,[],L,Nup=Nup,dtype=dtype)
	Ns=H.Ns
	E=H.eigvalsh()

	H1=hamiltonian(static,[],L,Nup=Nup,pzblock=1,dtype=dtype)
	H2=hamiltonian(static,[],L,Nup=Nup,pzblock=-1,dtype=dtype)

	E1=H1.eigvalsh()
	E2=H2.eigvalsh()
	
	Epz=np.concatenate((E1,E2))
	Epz.sort()

	eps=np.finfo(dtype).eps
	if np.sum(np.abs(Epz-E)/Ns) > 100*eps:
		raise Exception( "test failed pz symmetry at L={0:3d} with dtype {1} and Nup={2:2d}".format(L,np.dtype(dtype),Nup) )




def check_p_z(L,dtype,Nup=None):
	h=[[1.0,i] for i in xrange(L)]
	J=[[1.0,i,(i+1)%L] for i in xrange(L-1)]

	if type(Nup) is int:
		static=[["zz",J],["yy",J],["xx",J],["z",h]]
	else:
		static=[["zz",J],["x",h]]

	H=hamiltonian(static,[],L,Nup=Nup,dtype=dtype)
	Ns=H.Ns
	E=H.eigvalsh()

	H1=hamiltonian(static,[],L,Nup=Nup,pblock=1,zblock=1,dtype=dtype)
	H2=hamiltonian(static,[],L,Nup=Nup,pblock=-1,zblock=1,dtype=dtype)
	H3=hamiltonian(static,[],L,Nup=Nup,pblock=1,zblock=-1,dtype=dtype)
	H4=hamiltonian(static,[],L,Nup=Nup,pblock=-1,zblock=-1,dtype=dtype)

	E1=H1.eigvalsh()
	E2=H2.eigvalsh()
	E3=H3.eigvalsh()
	E4=H4.eigvalsh()

	
	Epz=np.concatenate((E1,E2,E3,E4))
	Epz.sort()

	eps=np.finfo(dtype).eps
	if np.sum(np.abs(Epz-E)/Ns) > 100*eps:
		raise Exception( "test failed p z symmetry at L={0:3d} with dtype {1} and Nup {2:2d}".format(L,np.dtype(dtype),Nup) )










def check_obc(Lmax):
	for dtype in (np.float32,np.float64,np.complex64,np.complex128):
		for L in xrange(2,Lmax+1,2):
			check_z(L,dtype,Nup=L/2)
			check_z(L,dtype)

	for dtype in (np.float32,np.float64,np.complex64,np.complex128):
		for L in xrange(2,Lmax+1,2):
			check_p(L,dtype,Nup=L/2)
			check_p(L,dtype)

	for dtype in (np.float32,np.float64,np.complex64,np.complex128):
		for L in xrange(2,Lmax+1,2):
			check_pz(L,dtype,Nup=L/2)
			check_pz(L,dtype)

	for dtype in (np.float32,np.float64,np.complex64,np.complex128):
		for L in xrange(2,Lmax+1,2):
			check_p_z(L,dtype,Nup=L/2)
			check_p_z(L,dtype) 



def check_t(L,dtype,Nup=None):
	if type(Nup) is int:
		J1=[[1.0,i,(i+1)%L] for i in xrange(L)]
		J2=[[1.0,i,(i+1)%L] for i in xrange(L)]
		static=[["zz",J1],["yy",J2],["xx",J2]]
	else:
		h=[[1.0,i] for i in xrange(L)]
		J1=[[1.0,i,(i+1)%L] for i in xrange(L)]
		J2=[[1.0,i,(i+1)%L] for i in xrange(L)]
		static=[["zz",J1],["x",h]]


	

	H=hamiltonian(static,[],L,Nup=Nup,dtype=dtype)
	Ns=H.Ns
	E=H.eigvalsh()

	Et=np.array([])
	for kblock in xrange(-L/2+1,L/2+1):
		Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock)
		Et=np.append(Et,Hk.eigvalsh())
	
	Et.sort()
	

	eps=np.finfo(dtype).eps
	if np.sum(np.abs(Et-E))/Ns > 1000*eps:
		raise Exception( "test failed t symmetry at L={0:3d} with dtype {1} and Nup={2}".format(L,np.dtype(dtype),Nup) )





def check_t_z(L,dtype,Nup=None):
	if type(Nup) is int:
		J1=[[1.0,i,(i+1)%L] for i in xrange(L)]
		J2=[[1.0,i,(i+1)%L] for i in xrange(L)]
		static=[["zz",J1],["yy",J2],["xx",J2]]
	else:
		h=[[1.0,i] for i in xrange(L)]
		J1=[[1.0,i,(i+1)%L] for i in xrange(L)]
		J2=[[1.0,i,(i+1)%L] for i in xrange(L)]
		static=[["zz",J1],["x",h]]

	eps=np.finfo(dtype).eps

	for kblock in xrange(-L/2+1,L/2+1):
		Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock)
		Ns=Hk.Ns
		Ek=Hk.eigvalsh()

		Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,zblock=+1)
		Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,zblock=-1)	
		Ek1=Hk1.eigvalsh()
		Ek2=Hk2.eigvalsh()
		Ekz=np.append(Ek1,Ek2)
		Ekz.sort()


		if np.sum(np.abs(Ek-Ekz))/Ns > 1000*eps:
			raise Exception( "test failed t z symmetry at L={0:3d} with dtype {1} and Nup={2}".format(L,np.dtype(dtype),Nup) )




def check_t_p(L,dtype,Nup=None):
	if type(Nup) is int:
		J1=[[1.0,i,(i+1)%L] for i in xrange(L)]
		J2=[[1.0,i,(i+1)%L] for i in xrange(L)]
		static=[["zz",J1],["+-",J2],["-+",J2]] # 
	else:
		h=[[1.0,i] for i in xrange(L)]
		J1=[[1.0,i,(i+1)%L] for i in xrange(L)]
		J2=[[1.0,i,(i+1)%L] for i in xrange(L)]
		static=[["zz",J1],["x",h]]

	eps=1000*np.finfo(dtype).eps

	for kblock in xrange(-L/2+1,0):
		Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock)
		Ns=Hk.Ns
		Ek=Hk.eigvalsh()

		Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=+1) 

		Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=-1)	

		Ek1=Hk1.eigvalsh()
		Ek2=Hk2.eigvalsh()
		
		if np.sum(np.abs(Ek-Ek1)) > Ns*eps:
			raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )

		if np.sum(np.abs(Ek-Ek2)) > Ns*eps:
			raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )

	Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=0)
	Ns=Hk.Ns
	Ek=Hk.eigvalsh()

	Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=0,pblock=+1)
	Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=0,pblock=-1)	
	Ek1=Hk1.eigvalsh()
	Ek2=Hk2.eigvalsh()
	Ekp=np.append(Ek1,Ek2)
	Ekp.sort()


	if np.sum(np.abs(Ek-Ekp)) > Ns*eps:
			raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,0,np.dtype(dtype),Nup) )


	if L%2 == 0:	
		for kblock in xrange(1,L/2):
			Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock)
			Ns=Hk.Ns
			Ek=Hk.eigvalsh()
	
			Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=+1) 
	
			Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=-1)	
	
			Ek1=Hk1.eigvalsh()
			Ek2=Hk2.eigvalsh()
	
			if np.sum(np.abs(Ek-Ek1)) > Ns*eps:
				raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )
	
			if np.sum(np.abs(Ek-Ek2)) > Ns*eps:
				raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )

	
		Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=L/2)
		Ns=Hk.Ns
		Ek=Hk.eigvalsh()

		Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=L/2,pblock=+1)
		Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=L/2,pblock=-1)	
		Ek1=Hk1.eigvalsh()
		Ek2=Hk2.eigvalsh()
		Ekp=np.append(Ek1,Ek2)
		Ekp.sort()

		if np.sum(np.abs(Ek-Ekp)) > Ns*eps:
				raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,L/2,np.dtype(dtype),Nup) )

	else:
		for kblock in xrange(1,L/2+1):
			Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock)
			Ns=Hk.Ns
			Ek=Hk.eigvalsh()
	
			Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=+1) 
	
			Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=-1)	
	
			Ek1=Hk1.eigvalsh()
			Ek2=Hk2.eigvalsh()
	
			if np.sum(np.abs(Ek-Ek1)) > Ns*eps:
				raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )
	
			if np.sum(np.abs(Ek-Ek2)) > Ns*eps:
				raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )
	




def check_t_pz(L,dtype,Nup=None):
	J1=[[1.0,i,(i+1)%L] for i in xrange(L)]
	h1=[[1.0,i] for i in xrange(L)]
	h2=[[1.0*(-1)**i,i] for i in xrange(L)]

	if type(Nup) is int:
		static=[["zz",J1],["xx",J1],["yy",J1],['z',h2]] 
	else:
		static=[["x",h1],['z',h2],['zz',J1]]

	eps=1000*np.finfo(dtype).eps
	
	a=2
	for kblock in xrange(-L/(a*2)+1,0):
		Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,a=a)
		Ns=Hk.Ns
		Ek=Hk.eigvalsh()

		Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pzblock=+1,a=a) 
		Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pzblock=-1,a=a)
		Ek1=Hk1.eigvalsh()
		Ek2=Hk2.eigvalsh()
		
		if np.sum(np.abs(Ek-Ek1)) > Ns*eps:
			print np.abs(Ek-Ek1)
			raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )

		if np.sum(np.abs(Ek-Ek2)) > Ns*eps:
			raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )

	Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=0,a=a)
	Ns=Hk.Ns
	Ek=Hk.eigvalsh()

	Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=0,pzblock=+1,a=a)
	Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=0,pzblock=-1,a=a)	
	Ek1=Hk1.eigvalsh()
	Ek2=Hk2.eigvalsh()
	Ekp=np.append(Ek1,Ek2)
	Ekp.sort()


	if np.sum(np.abs(Ek-Ekp)) > Ns*eps:
			raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,0,np.dtype(dtype),Nup) )

	if((L/a)%2 == 0):
		for kblock in xrange(1,L/(a*2)):
			Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,a=a)
			Ns=Hk.Ns
			Ek=Hk.eigvalsh()
	
			Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pzblock=+1,a=a) 
	
			Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pzblock=-1,a=a)	
	
			Ek1=Hk1.eigvalsh()
			Ek2=Hk2.eigvalsh()
	
			if np.sum(np.abs(Ek-Ek1)) > Ns*eps:
				raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )
	
			if np.sum(np.abs(Ek-Ek2)) > Ns*eps:
				raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )

		Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=L/(a*2),a=a)
		Ns=Hk.Ns
		Ek=Hk.eigvalsh()

		Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=L/(a*2),pzblock=+1,a=a)
		Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=L/(a*2),pzblock=-1,a=a)	
		Ek1=Hk1.eigvalsh()
		Ek2=Hk2.eigvalsh()
		Ekp=np.append(Ek1,Ek2)
		Ekp.sort()

		if np.sum(np.abs(Ek-Ekp)) > Ns*eps:
				raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,L/2,np.dtype(dtype),Nup) )
	else:
		for kblock in xrange(1,L/(a*2)+1):
			Hk=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,a=a)
			Ns=Hk.Ns
			Ek=Hk.eigvalsh()
	
			Hk1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pzblock=+1,a=a) 
	
			Hk2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pzblock=-1,a=a)	
	
			Ek1=Hk1.eigvalsh()
			Ek2=Hk2.eigvalsh()
	
			if np.sum(np.abs(Ek-Ek1)) > Ns*eps:
				raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )
	
			if np.sum(np.abs(Ek-Ek2)) > Ns*eps:
				raise Exception( "test failed t p- symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )





def check_t_p_z(L,dtype,Nup=None):
	if type(Nup) is int:
		J1=[[1.0,i,(i+1)%L] for i in xrange(L)]
		J2=[[1.0,i,(i+1)%L] for i in xrange(L)]
		static=[["zz",J1],["+-",J2],["-+",J2]] # 
	else:
		h=[[1.0,i] for i in xrange(L)]
		J1=[[1.0,i,(i+1)%L] for i in xrange(L)]
		J2=[[1.0,i,(i+1)%L] for i in xrange(L)]
		static=[["zz",J1],["x",h]]

	eps=1000*np.finfo(dtype).eps

	for kblock in xrange(-L/2+1,L/2+1):
		Hkp1=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=+1)
		Hkp2=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=-1)
		Ns=Hkp1.Ns
		Ekp1=Hkp1.eigvalsh()
		Ekp2=Hkp2.eigvalsh()

		Hkpz11=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=+1,zblock=+1) 
		Hkpz12=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=+1,zblock=-1)	
		Ekpz11=Hkpz11.eigvalsh()
		Ekpz12=Hkpz12.eigvalsh()

		Ekpz1=np.concatenate((Ekpz11,Ekpz12))
		Ekpz1.sort()

		Hkpz21=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=-1,zblock=+1) 
		Hkpz22=hamiltonian(static,[],L,Nup=Nup,dtype=dtype,kblock=kblock,pblock=-1,zblock=-1)	
		Ekpz21=Hkpz21.eigvalsh()
		Ekpz22=Hkpz22.eigvalsh()

		Ekpz2=np.concatenate((Ekpz21,Ekpz22))
		Ekpz2.sort()
			
		if np.sum(np.abs(Ekp1-Ekpz1)) > Ns*eps:
			raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )

		if np.sum(np.abs(Ekp2-Ekpz2)) > Ns*eps:
			raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )

		if(kblock not in [0,L/2]):
			if np.sum(np.abs(Ekp2-Ekpz1)) > Ns*eps:
				raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )

			if np.sum(np.abs(Ekp1-Ekpz2)) > Ns*eps:
				raise Exception( "test failed t p+ symmetry at L={0:3d} kblock={1:3d} with dtype {2} and Nup={3}".format(L,kblock,np.dtype(dtype),Nup) )






#check_m(10)
#check_opstr(10)
#check_obc(10)
L=10
check_t(L,np.complex128,Nup=None)
check_t(L,np.complex128,Nup=L/2)
check_t_z(L,np.complex128,Nup=None)
check_t_z(L,np.complex128,Nup=L/2)
check_t_p(L,np.complex128,Nup=None)
check_t_p(L,np.complex128,Nup=L/2)
check_t_pz(L,np.complex128,Nup=L/2)
check_t_pz(L,np.complex128,Nup=None)
check_t_p_z(L,np.complex128,Nup=L/2)
check_t_p_z(L,np.float32,Nup=None)






