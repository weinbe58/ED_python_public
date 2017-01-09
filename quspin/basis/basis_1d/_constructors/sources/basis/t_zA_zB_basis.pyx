
cdef state_type make_t_zA_zB_basis_template(shifter shift,bitop flip_sublat_A,bitop flip_sublat_B,
												bitop flip_all,ns_type next_state,
												state_type MAX,state_type s,
												int L,int zAblock,int zBblock,int kblock,int a,
												NP_INT8_t*N,NP_INT16_t*m,basis_type*basis): 
	cdef double k 
	cdef state_type Ns
	cdef NP_INT8_t mzA,mzB,mz,r
	cdef state_type i
	cdef _np.ndarray[NP_INT8_t,ndim=1] R = _np.zeros(4,dtype=NP_INT8)
	cdef int j
	
	k = 2.0*_np.pi*kblock*a/L
	Ns = 0
	
	for i in range(MAX):
		CheckState_T_ZA_ZB_template(shift,flip_sublat_A,flip_sublat_B,flip_all,kblock,L,s,a,R)
		r = R[0]
		mzA = R[1]
		mzB = R[2]
		mz = R[3]

		if r > 0:
			if mzA == -1 and mzB == -1 and mz == -1:
				m[Ns] = (L+1)
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1	

			if mzA != -1 and mzB == -1 and mz == -1:
				if 1 + zAblock*cos(k*mzA) != 0:			
					m[Ns] = mzA + 2*(L+1)
					N[Ns] = r			
					basis[Ns] = s
					Ns += 1	

			if mzA == -1 and mzB != -1 and mz == -1:
				if 1 + zBblock*cos(k*mzB) != 0:		
					m[Ns] = mzB + 3*(L+1)
					N[Ns] = r			
					basis[Ns] = s
					Ns += 1

			if mzA == -1 and mzB == -1 and mz != -1:
				if 1 + zAblock*zBblock*cos(k*mz) != 0:					
					m[Ns] = mz + 4*(L+1)
					N[Ns] = r			
					basis[Ns] = s
					Ns += 1
		
		s = next_state(s)
				
	return Ns


"""
def make_m_t_zA_zB_basis(int L,int Nup,int zAblock,int zBblock,int kblock,int a, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[NP_INT16_t,ndim=1] m, _np.ndarray[NP_UINT32_t,ndim=1] basis): 
	cdef double k 
	cdef unsigned int Ns,s
	cdef NP_INT8_t mzA,mzB,mz,r
	cdef _np.ndarray[NP_INT8_t,ndim=1] R = _np.zeros(4,dtype=NP_INT8)
	cdef char stp
	

	k = 2.0*_np.pi*kblock*a/L

	cdef int j

	s = 0
	for j in range(Nup):
		s += ( 1ull << j )

	stp = 0
	Ns = 0
	

	while True:

		CheckState_T_ZA_ZB_template(shift,flip_sublat_A,flip_sublat_B,flip_all,kblock,L,s,a,R)
		r = R[0]
		mzA = R[1]
		mzB = R[2]
		mz = R[3]

		if r > 0:
			if mzA == -1 and mzB == -1 and mz == -1:
				m[Ns] = (L+1)
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1	

			if mzA != -1 and mzB == -1 and mz == -1:
				if 1 + zAblock*cos(k*mzA) == 0:
					continue					
				m[Ns] = mzA + 2*(L+1)
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1	

			if mzA == -1 and mzB != -1 and mz == -1:
				if 1 + zBblock*cos(k*mzB) == 0:
					continue					
				m[Ns] = mzB + 3*(L+1)
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1


			if mzA == -1 and mzB == -1 and mz != -1:
				if 1 + zAblock*zBblock*cos(k*mz) == 0:
					continue					
				m[Ns] = mz + 4*(L+1)
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


def make_t_zA_zB_basis(int L,int zAblock,int zBblock,int kblock,int a, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[NP_INT16_t,ndim=1] m, _np.ndarray[NP_UINT32_t,ndim=1] basis): 
	cdef double k 
	cdef state_type s
	cdef int Ns
	cdef NP_INT8_t mzA,mzB,mz,r
	cdef _np.ndarray[NP_INT8_t,ndim=1] R = _np.zeros(4,dtype=NP_INT8)
	cdef char stp

	k = 2.0*_np.pi*kblock*a/L
	stp = 0
	Ns = 0

	for s in range(1ull << L):

		CheckState_T_ZA_ZB_template(shift,flip_sublat_A,flip_sublat_B,flip_all,kblock,L,s,a,R)
		r = R[0]
		mzA = R[1]
		mzB = R[2]
		mz = R[3]

		if r > 0:
			if mzA == -1 and mzB == -1 and mz == -1:
				m[Ns] = (L+1)
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1	

			if mzA != -1 and mzB == -1 and mz == -1:
				if 1 + zAblock*cos(k*mzA) == 0:
					continue					
				m[Ns] = mzA + 2*(L+1)
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1	

			if mzA == -1 and mzB != -1 and mz == -1:
				if 1 + zBblock*cos(k*mzB) == 0:
					continue					
				m[Ns] = mzB + 3*(L+1)
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1


			if mzA == -1 and mzB == -1 and mz != -1:
				if 1 + zAblock*zBblock*cos(k*mz) == 0:
					continue					
				m[Ns] = mz + 4*(L+1)
				N[Ns] = r			
				basis[Ns] = s
				Ns += 1
	return Ns
"""