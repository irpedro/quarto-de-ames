import numpy as np
from OpenGL.GL import *
import ctypes

def get_ames_room_solid():
    C_CHAO = [0.3, 0.3, 0.3]; C_TETO = [0.8, 0.8, 0.8]; C_ESQ = [0.8, 0.2, 0.2]; C_DIR = [0.2, 0.2, 0.8]; C_FUND = [0.8, 0.8, 0.2]
    
    # Cálculo das Normais Reais (usando 3 vértices de cada face)
    # Chão: Agora calcula a normal baseada na rampa (Frente-Esq, Fundo-Dir, Fundo-Esq)
    N_CHAO = calculate_normal([-2.0, -2.0, -5.0], [2.0, -2.0, -10.0], [-4.0, -4.0, -20.0])
    
    # Teto: vértices 4, 5 e 6 (Frente Direita, Frente Esquerda, Fundo Esquerdo)
    N_TETO = calculate_normal([2.0, 2.0, -5.0], [-2.0, 2.0, -5.0], [-4.0, 4.0, -20.0])
    
    # Parede Esquerda: vértices 8, 9 e 10 (Frente Baixo, Fundo Baixo, Fundo Cima)
    N_ESQ = calculate_normal([-2.0, -2.0, -5.0], [-4.0, -4.0, -20.0], [-4.0, 4.0, -20.0])
    
    # Parede Direita: vértices 12, 13 e 14 (Fundo Baixo, Frente Baixo, Frente Cima)
    N_DIR = calculate_normal([2.0, -2.0, -10.0], [2.0, -2.0, -5.0], [2.0, 2.0, -5.0])
    
    # Parede Fundo: vértices 16, 17 e 18 (Direito Baixo, Esquerdo Baixo, Esquerdo Cima)
    N_FUND = calculate_normal([2.0, -2.0, -10.0], [2.0, 2.0, -10.0], [-4.0, 4.0, -20.0])

    # Estrutura: X, Y, Z, R, G, B, NX, NY, NZ
    vertices = np.array([
        # CHÃO
         2.0, -2.0,  -5.0, *C_CHAO, *N_CHAO, # 0
        -2.0, -2.0,  -5.0, *C_CHAO, *N_CHAO, # 1
        -4.0, -4.0, -20.0, *C_CHAO, *N_CHAO, # 2
         2.0, -2.0, -10.0, *C_CHAO, *N_CHAO, # 3
        # TETO
         2.0,  2.0,  -5.0, *C_TETO, *N_TETO, # 4
        -2.0,  2.0,  -5.0, *C_TETO, *N_TETO, # 5
        -4.0,  4.0, -20.0, *C_TETO, *N_TETO, # 6
         2.0,  2.0, -10.0, *C_TETO, *N_TETO, # 7
        # PAREDE ESQUERDA
        -2.0, -2.0,  -5.0, *C_ESQ, *N_ESQ,   # 8
        -4.0, -4.0, -20.0, *C_ESQ, *N_ESQ,   # 9
        -4.0,  4.0, -20.0, *C_ESQ, *N_ESQ,   # 10
        -2.0,  2.0,  -5.0, *C_ESQ, *N_ESQ,   # 11
        # PAREDE DIREITA
         2.0, -2.0, -10.0, *C_DIR, *N_DIR,   # 12
         2.0, -2.0,  -5.0, *C_DIR, *N_DIR,   # 13
         2.0,  2.0,  -5.0, *C_DIR, *N_DIR,   # 14
         2.0,  2.0, -10.0, *C_DIR, *N_DIR,   # 15
        # PAREDE FUNDO
         2.0, -2.0, -10.0, *C_FUND, *N_FUND, # 16
        -4.0, -4.0, -20.0, *C_FUND, *N_FUND, # 17
        -4.0,  4.0, -20.0, *C_FUND, *N_FUND, # 18
         2.0,  2.0, -10.0, *C_FUND, *N_FUND  # 19
    ], dtype=np.float32)

    # Índices com o culling perfeitamente validado
    indices = np.array([
        4, 5, 6,    4, 6, 7,       # Teto 
        8, 9, 10,   8, 10, 11,     # Esquerda
        12, 13, 14, 12, 14, 15,    # Direita
        16, 19, 18, 16, 18, 17     # Fundo
    ], dtype=np.uint32)
    
    return vertices, indices

def setup_buffers(vertices, indices):
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)
    
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    
    # Stride aumentou para 9 floats (36 bytes)
    stride = 9 * vertices.itemsize
    
    # Atributo 0: Posição (XYZ)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    # Atributo 1: Cor (RGB)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    # Atributo 2: Normal (NX, NY, NZ) - Começa após o 6º float
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * vertices.itemsize))
    glEnableVertexAttribArray(2)
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return VAO

def calculate_normal(p1, p2, p3):
    """Calcula a normal de um triângulo usando o produto vetorial."""
    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(p3) - np.array(p1)
    normal = np.cross(v1, v2)
    norm = np.linalg.norm(normal)
    return normal / norm if norm > 0 else normal

def get_sphere(radius=0.5, sectors=30, stacks=30, color=[0.9, 0.3, 0.1]):
    """Gera os vértices e índices de uma esfera."""
    vertices = []
    indices = []
    
    for i in range(stacks + 1):
        V = i / stacks
        phi = V * np.pi
        
        for j in range(sectors + 1):
            U = j / sectors
            theta = U * 2 * np.pi
            
            # Coordenadas esféricas para XYZ
            x = radius * np.cos(theta) * np.sin(phi)
            y = radius * np.cos(phi)
            z = radius * np.sin(theta) * np.sin(phi)
            
            # A normal de uma esfera na origem é apenas o seu ponto normalizado
            nx, ny, nz = x / radius, y / radius, z / radius
            
            # XYZ, RGB, NX, NY, NZ (9 floats)
            vertices.extend([x, y, z, *color, nx, ny, nz])
            
    for i in range(stacks):
        for j in range(sectors):
            p1 = i * (sectors + 1) + j
            p2 = p1 + sectors + 1
            
            # Dois triângulos por quadrante
            indices.extend([p1, p2, p1 + 1, p1 + 1, p2, p2 + 1])
            
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def setup_sphere_buffers(vertices, indices):
    """Cria os buffers específicos para a esfera."""
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)
    
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    
    stride = 9 * vertices.itemsize
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * vertices.itemsize))
    glEnableVertexAttribArray(2)
    
    glBindVertexArray(0)
    return VAO, len(indices)

def get_unit_sphere(sectors=30, stacks=30):
    """
    Esfera de raio 1.0 na origem, cor branca (1,1,1).
    A cor real é definida via uniform objectColor no main.py.
    """
    return get_sphere(radius=1.0, sectors=sectors, stacks=stacks, color=[1.0, 1.0, 1.0])


def get_ames_floor_grid(n_cols=20, n_rows=20):
    """
    Gera o chão do Quarto de Ames como um grid subdividido.
    Resolve a costura visível entre os dois triângulos gigantes.
    
    A superfície é bilinear: interpola Y entre os 4 cantos,
    e o xadrez procedural é calculado no shader a partir de X, Z.
    """
    C_CHAO = [0.3, 0.3, 0.3]
    N_CHAO = calculate_normal([-2.0, -2.0, -5.0], [2.0, -2.0, -10.0], [-4.0, -4.0, -20.0])

    # Os 4 cantos do chão (frente-dir, frente-esq, fundo-esq, fundo-dir)
    C0 = np.array([ 2.0, -2.0,  -5.0])  # frente direita
    C1 = np.array([-2.0, -2.0,  -5.0])  # frente esquerda
    C2 = np.array([-4.0, -4.0, -20.0])  # fundo esquerdo
    C3 = np.array([ 2.0, -2.0, -10.0])  # fundo direito

    vertices = []
    indices = []

    # Gerar grade de vértices
    for i in range(n_rows + 1):
        v = i / n_rows
        for j in range(n_cols + 1):
            u = j / n_cols
            # Interpolação bilinear das 4 arestas
            frente = C0 * (1 - u) + C1 * u
            fundo  = C3 * (1 - u) + C2 * u
            ponto  = frente * (1 - v) + fundo * v
            x, y, z = ponto
            vertices.extend([x, y, z, *C_CHAO, *N_CHAO])

    # Índices (2 triângulos por célula)
    for i in range(n_rows):
        for j in range(n_cols):
            a = i * (n_cols + 1) + j
            b = a + 1
            c = a + (n_cols + 1)
            d = c + 1
            indices.extend([a, c, b, b, c, d])

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def get_molduras(altura=0.15, offset=0.01, z_ref=10.0):
    """
    altura: altura desejada NA TELA (referência em z_ref = -10).
    z_ref: profundidade de referência onde 'altura' vale exatamente.
    """
    C_RODAPE = [0.35, 0.25, 0.18]
    C_SANCA  = [0.92, 0.90, 0.85]

    N_ESQ  = calculate_normal([-2.0, -2.0, -5.0], [-4.0, -4.0, -20.0], [-4.0, 4.0, -20.0])
    N_DIR  = calculate_normal([2.0, -2.0, -10.0], [2.0, -2.0, -5.0], [2.0, 2.0, -5.0])
    N_FUND = calculate_normal([2.0, -2.0, -10.0], [2.0, 2.0, -10.0], [-4.0, 4.0, -20.0])

    vertices = []
    indices = []

    def add_faixa(p1, p2, normal, cor, sinal_y):
        nx, ny, nz = normal
        dx, dy, dz = nx * offset, ny * offset, nz * offset

        x1, y1, z1 = p1
        x2, y2, z2 = p2

        # Altura proporcional ao Z (em módulo)
        h1 = altura * (abs(z1) / abs(z_ref))
        h2 = altura * (abs(z2) / abs(z_ref))

        base = len(vertices) // 9
        vertices.extend([x1 + dx, y1 + dy,                z1 + dz, *cor, *normal])
        vertices.extend([x2 + dx, y2 + dy,                z2 + dz, *cor, *normal])
        vertices.extend([x1 + dx, y1 + sinal_y * h1 + dy, z1 + dz, *cor, *normal])
        vertices.extend([x2 + dx, y2 + sinal_y * h2 + dy, z2 + dz, *cor, *normal])
        indices.extend([base, base + 1, base + 2,
                        base + 1, base + 3, base + 2])

    # Rodapés (sinal +1 = sobe)
    add_faixa((-2.0, -2.0,  -5.0), (-4.0, -4.0, -20.0), N_ESQ,  C_RODAPE, +1)
    add_faixa(( 2.0, -2.0, -10.0), ( 2.0, -2.0,  -5.0), N_DIR,  C_RODAPE, +1)
    add_faixa((-4.0, -4.0, -20.0), ( 2.0, -2.0, -10.0), N_FUND, C_RODAPE, +1)

    # Sancas (sinal -1 = desce)
    add_faixa((-4.0, 4.0, -20.0), (-2.0, 2.0,  -5.0), N_ESQ,  C_SANCA, -1)
    add_faixa(( 2.0, 2.0,  -5.0), ( 2.0, 2.0, -10.0), N_DIR,  C_SANCA, -1)
    add_faixa(( 2.0, 2.0, -10.0), (-4.0, 4.0, -20.0), N_FUND, C_SANCA, -1)

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def get_janelas_e_porta():
    """
    Janelas com moldura fina + vidro + cruz (mullion).
    Tudo definido em coordenadas do plano da parede (u, v):
      u = 0 (frente) a 1 (fundo)
      v = 0 (baixo)  a 1 (cima)
    As bordas seguem a inclinação da parede (paralelas à sanca/rodapé).
    """
    C_MOLDURA = [0.12, 0.06, 0.04]
    C_VIDRO_ESQ = [0.10, 0.22, 0.45]
    C_VIDRO_DIR = [0.15, 0.32, 0.55]
    C_PORTA = [0.40, 0.22, 0.10]

    N_ESQ  = calculate_normal([-2.0, -2.0, -5.0], [-4.0, -4.0, -20.0], [-4.0, 4.0, -20.0])
    N_DIR  = calculate_normal([2.0, -2.0, -10.0], [2.0, -2.0, -5.0], [2.0, 2.0, -5.0])
    N_FUND = calculate_normal([2.0, -2.0, -10.0], [2.0, 2.0, -10.0], [-4.0, 4.0, -20.0])

    vertices = []
    indices = []

    def add_quad(p0, p1, p2, p3, cor, normal, offset):
        nx, ny, nz = normal
        dx, dy, dz = nx * offset, ny * offset, nz * offset
        base = len(vertices) // 9
        for p in [p0, p1, p2, p3]:
            x, y, z = p
            vertices.extend([x + dx, y + dy, z + dz, *cor, *normal])
        indices.extend([base, base + 1, base + 2,
                        base, base + 2, base + 3])

    def add_janela(p00, p10, p11, p01, u0, u1, v0, v1, cor_vidro, normal):
        """Moldura fina, vidro recessado e cruz. Com overlap anti-gap."""
        def ponto(u, v):
            b = p00 + (p10 - p00) * u
            t = p01 + (p11 - p01) * u
            return b + (t - b) * v

        esp = 0.022          # espessura da moldura em (u,v)
        ov  = esp * 0.5      # sobreposição nas quinas
        gap = esp * 0.35     # extensão do vidro para dentro da moldura

        # ---- OFFSETS ----
        # Moldura na FRENTE (mais próxima da câmera)
        # Vidro ATRÁS (recessado, como janela real)
        off_frame   = 0.030
        off_glass   = 0.015
        off_mullion = 0.035

        # 1) Moldura: 4 faixas com sobreposição nas quinas
        # Superior
        add_quad(ponto(u0-esp, v1),
                 ponto(u1+esp, v1),
                 ponto(u1+esp, v1+esp),
                 ponto(u0-esp, v1+esp),
                 C_MOLDURA, normal, off_frame)
        # Inferior
        add_quad(ponto(u0-esp, v0-esp),
                 ponto(u1+esp, v0-esp),
                 ponto(u1+esp, v0),
                 ponto(u0-esp, v0),
                 C_MOLDURA, normal, off_frame)
        # Esquerda
        add_quad(ponto(u0-esp, v0-ov),
                 ponto(u0, v0-ov),
                 ponto(u0, v1+ov),
                 ponto(u0-esp, v1+ov),
                 C_MOLDURA, normal, off_frame)
        # Direita
        add_quad(ponto(u1, v0-ov),
                 ponto(u1+esp, v0-ov),
                 ponto(u1+esp, v1+ov),
                 ponto(u1, v1+ov),
                 C_MOLDURA, normal, off_frame)

        # 2) Vidro: um pouco maior que o vão, para cobrir a emenda
        add_quad(ponto(u0-gap, v0-gap),
                 ponto(u1+gap, v0-gap),
                 ponto(u1+gap, v1+gap),
                 ponto(u0-gap, v1+gap),
                 cor_vidro, normal, off_glass)

        # 3) Mullion vertical (na frente do vidro)
        mu = (u0 + u1) * 0.5
        m_u = (u1 - u0) * 0.030
        add_quad(ponto(mu-m_u, v0+gap*0.5),
                 ponto(mu+m_u, v0+gap*0.5),
                 ponto(mu+m_u, v1-gap*0.5),
                 ponto(mu-m_u, v1-gap*0.5),
                 C_MOLDURA, normal, off_mullion)

        # 4) Mullion horizontal (na frente do vidro)
        mv = (v0 + v1) * 0.5
        m_v = (v1 - v0) * 0.030
        add_quad(ponto(u0+gap*0.5, mv-m_v),
                 ponto(u1-gap*0.5, mv-m_v),
                 ponto(u1-gap*0.5, mv+m_v),
                 ponto(u0+gap*0.5, mv+m_v),
                 C_MOLDURA, normal, off_mullion)


    def add_porta(p00, p10, p11, p01, u0, u1, v0, v1, cor_porta, normal):
        """Porta: moldura topo + laterais, painel único, rebaixo e puxador."""
        def ponto(u, v):
            b = p00 + (p10 - p00) * u
            t = p01 + (p11 - p01) * u
            return b + (t - b) * v

        esp = 0.022
        ov  = esp * 0.5
        gap = esp * 0.35

        off_frame   = 0.045
        off_painel  = 0.030
        off_detail  = 0.055

        # 1) Moldura: topo + 2 laterais (SEM base — porta vai até o chão)
        add_quad(ponto(u0-esp, v1),
                 ponto(u1+esp, v1),
                 ponto(u1+esp, v1+esp),
                 ponto(u0-esp, v1+esp),
                 C_MOLDURA, normal, off_frame)
        add_quad(ponto(u0-esp, v0),
                 ponto(u0, v0),
                 ponto(u0, v1+ov),
                 ponto(u0-esp, v1+ov),
                 C_MOLDURA, normal, off_frame)
        add_quad(ponto(u1, v0),
                 ponto(u1+esp, v0),
                 ponto(u1+esp, v1+ov),
                 ponto(u1, v1+ov),
                 C_MOLDURA, normal, off_frame)

        # 2) Painel da porta (madeira)
        add_quad(ponto(u0-gap, v0-0.01),
                 ponto(u1+gap, v0-0.01),
                 ponto(u1+gap, v1+gap),
                 ponto(u0-gap, v1+gap),
                 cor_porta, normal, off_painel)

        # 3) Rebaixo decorativo (madeira mais escura)
        cor_escura = [c * 0.55 for c in cor_porta]
        du = (u1-u0) * 0.18                # largura do rebaixo
        dv = (v1-v0) * 0.06                # altura do rebaixo
        # Compensação de perspectiva: empurra o rebaixo para a direita (frente)
        deslocamento = (u1-u0) * 0.04

        add_quad(ponto(u0+du+deslocamento, v0+dv),
                 ponto(u1-du+deslocamento, v0+dv),
                 ponto(u1-du+deslocamento, v1-dv),
                 ponto(u0+du+deslocamento, v1-dv),
                 cor_escura, normal, off_detail)

        # 4) Puxador dourado (do lado direito)
        pr = (u1-u0) * 0.055
        pu = u1 - (u1-u0) * 0.20
        pv = (v0+v1) * 0.48
        add_quad(ponto(pu-pr, pv-pr),
                 ponto(pu+pr, pv-pr),
                 ponto(pu+pr, pv+pr),
                 ponto(pu-pr, pv+pr),
                 [0.85, 0.65, 0.15], normal, off_detail + 0.015)

    # ============ JANELA ESQUERDA ============
    # Cantos do plano da parede esquerda
    P00 = np.array([-2.0, -2.0,  -5.0])
    P10 = np.array([-4.0, -4.0, -20.0])
    P11 = np.array([-4.0,  4.0, -20.0])
    P01 = np.array([-2.0,  2.0,  -5.0])

    # Janela pequena, no terço central-superior da parede
    add_janela(P00, P10, P11, P01,
               u0=0.12, u1=0.36,   # era 0.08, 0.32
               v0=0.40, v1=0.75,
               cor_vidro=C_VIDRO_ESQ, normal=N_ESQ)

    # ============ JANELA DIREITA ============
    # Invertemos P00 ↔ P10 e P01 ↔ P11 para consertar o winding
    # (parede direita tem normal em -X, o oposto da esquerda)
    P00 = np.array([2.0, -2.0, -10.0])   # back-bottom  (antes era -5)
    P10 = np.array([2.0, -2.0,  -5.0])   # front-bottom (antes era -10)
    P11 = np.array([2.0,  2.0,  -5.0])   # front-top    (antes era -10)
    P01 = np.array([2.0,  2.0, -10.0])   # back-top     (antes era -5)

    # Como u agora vai do fundo (0) para frente (1), invertemos u0/u1
    # Old u: 0=frente, 1=fundo  →  New u: 0=fundo, 1=frente
    # Portanto new_u = 1 - old_u →  [0.474, 0.784]
    add_janela(P00, P10, P11, P01,
               u0=0.474, u1=0.784,
               v0=0.40, v1=0.75,
               cor_vidro=C_VIDRO_DIR, normal=N_DIR)


    # ============ PORTA (parede do fundo) ============
    # u=0 é o fundo (X=-4), u=1 é a frente (X=2)
    P00 = np.array([-4.0, -4.0, -20.0])
    P10 = np.array([ 2.0, -2.0, -10.0])
    P11 = np.array([ 2.0,  2.0, -10.0])
    P01 = np.array([-4.0,  4.0, -20.0])

    add_porta(P00, P10, P11, P01,
              u0=0.58, u1=0.76,    # mais larga (era 0.59–0.74)
              v0=0.00, v1=0.72,    # começa no chão (era 0.05) e mais alta
              cor_porta=C_PORTA, normal=N_FUND)

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)