

# magnetization 
def spin_m_basis(int L, int Nup, state_type Ns,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef int j
    cdef state_type MAX = comb(L,Nup,exact=True)
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )



    make_n_basis_template[basis_type](next_state_pcon_hcb,NULL,MAX,s,&basis[0])


# parity 
def spin_m_p_basis(int L,int Nup,int pblock,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j

    s = 0
    for j in range(Nup):
        s += ( 1ull << j )

    return make_p_basis_template[basis_type](fliplr,next_state_pcon_hcb,NULL,MAX,s,L,pblock,&N[0],&basis[0])

    
def spin_p_basis(int L,int pblock,_np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s = 0
    cdef state_type MAX=1ull<<L

    return make_p_basis_template[basis_type](fliplr,next_state_inc_1,NULL,MAX,s,L,pblock,&N[0],&basis[0])


# parity-spin inversion
def spin_m_p_z_basis(int L, int Nup, int pblock, int zblock, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )

    return make_p_z_basis_template[basis_type](fliplr,flip_all,next_state_pcon_hcb,NULL,MAX,s,L,pblock,zblock,&N[0],&basis[0])
    

def spin_p_z_basis(int L, int pblock, int zblock, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L

    return make_p_z_basis_template[basis_type](fliplr,flip_all,next_state_inc_1,NULL,MAX,s,L,pblock,zblock,&N[0],&basis[0])


# (parity)*(spin inversion)
def spin_m_pz_basis(int L, int Nup, int pzblock, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_pz_basis_template[basis_type](fliplr,flip_all,next_state_pcon_hcb,NULL,MAX,s,L,pzblock,&N[0],&basis[0])
    

def spin_pz_basis(int L, int pzblock, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_pz_basis_template[basis_type](fliplr,flip_all,next_state_inc_1,NULL,MAX,s,L,pzblock,&N[0],&basis[0])


# translation
def spin_m_t_basis(int L, int Nup, int kblock,int a, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_t_basis_template[basis_type](shift,next_state_pcon_hcb,NULL,MAX,s,L,kblock,a,&N[0],&basis[0])


def spin_t_basis(int L, int kblock,int a, _np.ndarray[NP_INT8_t,ndim=1] N, _np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_t_basis_template[basis_type](shift,next_state_inc_1,NULL,MAX,s,L,kblock,a,&N[0],&basis[0])


# translation-parity
def spin_m_t_p_basis(int L, int Nup,int pblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_t_p_basis_template[basis_type](shift,fliplr,next_state_pcon_hcb,NULL,MAX,s,L,pblock,kblock,a,&N[0],&m[0],&basis[0])


def spin_t_p_basis(int L,int pblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_t_p_basis_template[basis_type](shift,fliplr,next_state_inc_1,NULL,MAX,s,L,pblock,kblock,a,&N[0],&m[0],&basis[0])




# translation-parity-spin inversion
def spin_m_t_p_z_basis(int L, int Nup,int pblock,int zblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT16_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_t_p_z_basis_template[basis_type](shift,fliplr,next_state_pcon_hcb,NULL,MAX,s,L,pblock,zblock,kblock,a,&N[0],&m[0],&basis[0])
    

def spin_t_p_z_basis(int L,int pblock,int zblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT16_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_t_p_z_basis_template[basis_type](shift,fliplr,next_state_inc_1,NULL,MAX,s,L,pblock,zblock,kblock,a,&N[0],&m[0],&basis[0])




# translation-(parity)*(spin inversion)
def spin_m_t_pz_basis(int L, int Nup,int pzblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_t_pz_basis_template[basis_type](shift,fliplr,flip_all,next_state_pcon_hcb,NULL,MAX,s,L,pzblock,kblock,a,&N[0],&m[0],&basis[0])
    

def spin_t_pz_basis(int L,int pzblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_t_pz_basis_template[basis_type](shift,fliplr,flip_all,next_state_inc_1,NULL,MAX,s,L,pzblock,kblock,a,&N[0],&m[0],&basis[0])


# translation-spin inversion
def spin_m_t_z_basis(int L,int Nup,int zblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_t_z_basis_template[basis_type](shift,flip_all,next_state_pcon_hcb,NULL,MAX,s,L,zblock,kblock,a,&N[0],&m[0],&basis[0])


def spin_t_z_basis(int L,int zblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_t_z_basis_template[basis_type](shift,flip_all,next_state_inc_1,NULL,MAX,s,L,zblock,kblock,a,&N[0],&m[0],&basis[0])




# translation-spin inversion A
def spin_m_t_zA_basis(int L, int Nup,int zAblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_t_zA_basis_template[basis_type](shift,flip_sublat_A,next_state_pcon_hcb,NULL,MAX,s,L,zAblock,kblock,a,&N[0],&m[0],&basis[0])


def spin_t_zA_basis(int L,int zAblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_t_zA_basis_template[basis_type](shift,flip_sublat_A,next_state_inc_1,NULL,MAX,s,L,zAblock,kblock,a,&N[0],&m[0],&basis[0])



# translation-spin inversion B
def spin_m_t_zB_basis(int L, int Nup,int zBblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_t_zB_basis_template[basis_type](shift,flip_sublat_B,next_state_pcon_hcb,NULL,MAX,s,L,zBblock,kblock,a,&N[0],&m[0],&basis[0])
    

def spin_t_zB_basis(int L,int zBblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT8_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_t_zB_basis_template[basis_type](shift,flip_sublat_B,next_state_inc_1,NULL,MAX,s,L,zBblock,kblock,a,&N[0],&m[0],&basis[0])




# translation-spin inversion A-spin inversion B
def spin_m_t_zA_zB_basis(int L,int Nup,int zAblock,int zBblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT16_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )


def spin_t_zA_zB_basis(int L,int zAblock,int zBblock,int kblock,int a,_np.ndarray[NP_INT8_t,ndim=1] N,_np.ndarray[NP_INT16_t,ndim=1] m,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_t_zA_zB_basis_template[basis_type](shift,flip_sublat_A,flip_sublat_B,flip_all,next_state_inc_1,NULL,MAX,s,L,zAblock,zBblock,kblock,a,&N[0],&m[0],&basis[0])





# spin inversion
def spin_m_z_basis(int L,int Nup,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_z_basis_template[basis_type](flip_all,next_state_pcon_hcb,NULL,MAX,s,L,&basis[0])


def spin_z_basis(int L,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_z_basis_template[basis_type](flip_all,next_state_inc_1,NULL,MAX,s,L,&basis[0])




# spin inversion A
def spin_m_zA_basis(int L,int Nup,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_zA_basis_template[basis_type](flip_sublat_A,next_state_pcon_hcb,NULL,MAX,s,L,&basis[0])


def spin_zA_basis(int L,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_zA_basis_template[basis_type](flip_sublat_A,next_state_inc_1,NULL,MAX,s,L,&basis[0])




# spin inversion B
def spin_m_zB_basis(int L,int Nup,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_zB_basis_template[basis_type](flip_sublat_B,next_state_pcon_hcb,NULL,MAX,s,L,&basis[0])

    

def spin_zB_basis(int L,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_zB_basis_template[basis_type](flip_sublat_B,next_state_inc_1,NULL,MAX,s,L,&basis[0])



# spin inversion A-spin inversion B
def spin_m_zA_zB_basis(int L,int Nup,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s
    cdef state_type MAX=comb(L,Nup,exact=True)
    cdef int j
    s = 0
    for j in range(Nup):
        s += ( 1ull << j )
    return make_zA_zB_basis_template[basis_type](flip_sublat_A,flip_sublat_B,flip_all,next_state_pcon_hcb,NULL,MAX,s,L,&basis[0])
    

def spin_zA_zB_basis(int L,_np.ndarray[basis_type,ndim=1] basis):
    cdef state_type s=0
    cdef state_type MAX=1ull<<L
    return make_zA_zB_basis_template[basis_type](flip_sublat_A,flip_sublat_B,flip_all,next_state_inc_1,NULL,MAX,s,L,&basis[0])

    