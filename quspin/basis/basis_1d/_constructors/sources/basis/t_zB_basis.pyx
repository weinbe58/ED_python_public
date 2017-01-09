cdef state_type make_t_zB_basis_template(shifter shift,bitop flip_sublat_B,ns_type next_state,
											state_type MAX,state_type s,
											int L,int zBblock,int kblock,int a,
											NP_INT8_t*N, NP_INT8_t*m,basis_type*basis): 
	cdef double k 
	cdef state_type Ns
	cdef state_type i
	cdef NP_INT8_t mzB,r
	cdef _np.ndarray[NP_INT8_t,ndim=1] R = _np.zeros(2,dtype=NP_INT8)
	cdef int j
	

	k = 2.0*_np.pi*kblock*a/L
	Ns = 0
	
	for i in range(MAX):
		CheckState_T_ZB_template(shift,flip_sublat_B,kblock,L,s,a,R)
		r = R[0]
		mzB = R[1]

		if r > 0:
			if mzB != -1:
				if 1 + zBblock*cos(k*mzB) == 0:
					r = -1				

			if r > 0:
				m[Ns] = mzB
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1	
		
		s = next_state(s)

	return Ns


"""
def make_m_t_zB_basis(int L,int Nup,int zBblock,int kblock,int a, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[NP_INT8_t,ndim=1] m, _np.ndarray[NP_UINT32_t,ndim=1] basis): 
	cdef double k 
	cdef unsigned int s,Ns
	cdef NP_INT8_t mzB,r
	cdef _np.ndarray[NP_INT8_t,ndim=1] R = _np.zeros(2,dtype=NP_INT8)
	cdef char stp
	

	k = 2.0*_np.pi*kblock*a/L

	cdef int j

	s = 0
	for j in range(Nup):
		s += ( 1ull << j )

	stp = 0
	Ns = 0
	

	while True:
		CheckState_T_ZB_template(shift,flip_sublat_B,kblock,L,s,a,R)
		r = R[0]
		mzB = R[1]

		if r > 0:
			if mzB != -1:
				if 1 + zBblock*cos(k*mzB) == 0:
					r = -1				

			if r > 0:
				m[Ns] = mzB
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1	

		stp = 1 & ( s >> (L-1) ) 
		for i in range(1,Nup):
			stp &= 1 & ( s >> (L-i-1) )

		if stp or (s == 0):
			break
		
		s = next_state(s)
				

	return Ns

def make_t_zB_basis(int L,int zBblock,int kblock,int a, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[NP_INT8_t,ndim=1] m, _np.ndarray[NP_UINT32_t,ndim=1] basis): 
	cdef double k 
	cdef state_type s
	cdef int Ns
	cdef NP_INT8_t mzB,r
	cdef _np.ndarray[NP_INT8_t,ndim=1] R = _np.zeros(2,dtype=NP_INT8)
	cdef char stp

	k = 2.0*_np.pi*kblock*a/L
	stp = 0
	Ns = 0

	for s in range(1ull << L):
		CheckState_T_ZB_template(shift,flip_sublat_B,kblock,L,s,a,R)
		r = R[0]
		mzB = R[1]
		if r > 0:
			if mzB != -1:
				if 1 + zBblock*cos(k*mzB) == 0:
					continue					

			m[Ns] = mzB
			N[Ns] = r			
			basis[Ns] = s
			Ns += 1	


	return Ns
"""