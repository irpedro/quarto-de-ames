import math
import glfw
from OpenGL.GL import *
import shaders
import numpy as np
import camera
import geometry
import physics
import renderer
import input_handler

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# --- ESTADO GLOBAL ---
camera_revelada = False

# Esfera controlável (verde) - no canto frontal-direito
esfera_x = 1.6
esfera_z = -5.35
RAIO_ESFERA = 0.35

# Esfera estática (laranja) - GRANDE, no fundo esquerdo
# r=0.80 faz a laranja parecer do MESMO tamanho da verde no início
gemea_x = -2.0
gemea_z = -14
RAIO_GEMEA = 0.70

# Animação automática (toggle com 'P')
modo_automatico = False
tecla_p_pressionada_antes = False   
tecla_t_pressionada_antes = False
tecla_espaco_antes = False
tecla_r_pressionada_antes = False

# Posições "home" das esferas
HOME_GREEN  = np.array([1.6, -5.35])
HOME_ORANGE = np.array([-2.0, -14])

# Frequência do vai-e-vem automático
AUTO_FREQUENCIA = 0.3  # Hz

def process_input(window, delta_time, current_time, estado_orbital):
    global camera_revelada, esfera_x, esfera_z, gemea_x, gemea_z
    global modo_automatico, tecla_p_pressionada_antes
    global tecla_t_pressionada_antes, tecla_espaco_antes, tecla_r_pressionada_antes

    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    # --- Toggle da câmera de revelação (ESPAÇO) ---
    tecla_espaco_agora = glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS
    if tecla_espaco_agora and not tecla_espaco_antes:
        camera_revelada = not camera_revelada
        estado_str = "REVELADA" if camera_revelada else "FOCAL"
        print(f">>> Camera {estado_str}")
    tecla_espaco_antes = tecla_espaco_agora

    # --- Toggle do modo automático (P de Play/Pause) ---
    tecla_p_agora = glfw.get_key(window, glfw.KEY_P) == glfw.PRESS
    if tecla_p_agora and not tecla_p_pressionada_antes:
        modo_automatico = not modo_automatico
        estado = "ATIVADO" if modo_automatico else "DESATIVADO"
        print(f">>> Modo automatico {estado}")
    tecla_p_pressionada_antes = tecla_p_agora

    # --- Reset orbital (T) ---
    tecla_t_agora = glfw.get_key(window, glfw.KEY_T) == glfw.PRESS
    if tecla_t_agora and not tecla_t_pressionada_antes:
        input_handler.resetar_orbital(estado_orbital)
        print(">>> Camera orbital resetada (top-down)")
    tecla_t_pressionada_antes = tecla_t_agora

    # --- Reset das esferas (R) --- NOVO
    tecla_r_agora = glfw.get_key(window, glfw.KEY_R) == glfw.PRESS
    if tecla_r_agora and not tecla_r_pressionada_antes:
        esfera_x, esfera_z = HOME_GREEN[0], HOME_GREEN[1]
        gemea_x,  gemea_z  = HOME_ORANGE[0], HOME_ORANGE[1]
        modo_automatico = False
        print(">>> Esferas resetadas + modo automatico desativado")
    tecla_r_pressionada_antes = tecla_r_agora

    # --- Pan da câmera orbital com WASD (só no modo revelação) ---
    if camera_revelada:
        input_handler.pan_wasd(estado_orbital, window, delta_time)

    # --- Modo Automático: as DUAS esferas trocam de posição ---
    if modo_automatico:
        fator = (math.sin(current_time * AUTO_FREQUENCIA * 2.0 * math.pi) + 1.0) / 2.0
        # Verde: HOME_GREEN → HOME_ORANGE
        esfera_x = HOME_GREEN[0] + (HOME_ORANGE[0] - HOME_GREEN[0]) * fator
        esfera_z = HOME_GREEN[1] + (HOME_ORANGE[1] - HOME_GREEN[1]) * fator
        # Laranja: HOME_ORANGE → HOME_GREEN (oposto)
        gemea_x = HOME_ORANGE[0] + (HOME_GREEN[0] - HOME_ORANGE[0]) * fator
        gemea_z = HOME_ORANGE[1] + (HOME_GREEN[1] - HOME_ORANGE[1]) * fator

        # As esferas são "clampadas" para não atravessar paredes
        esfera_x, esfera_z = physics.clamp_esfera(esfera_x, esfera_z, RAIO_ESFERA)
        gemea_x, gemea_z = physics.clamp_esfera(gemea_x, gemea_z, RAIO_GEMEA)
        return

    # --- Modo Manual da esfera verde ---
    velocidade = 4.0 * delta_time
    novo_x = esfera_x
    novo_z = esfera_z

    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:    novo_z -= velocidade
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:  novo_z += velocidade
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:  novo_x -= velocidade
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS: novo_x += velocidade

    esfera_x, esfera_z = physics.clamp_esfera(novo_x, novo_z, RAIO_ESFERA)


def main():
    global esfera_x, esfera_z, gemea_x, gemea_z
    if not glfw.init():
        print("Falha ao inicializar o GLFW")
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.SAMPLES, 16)   # MSAA 16x

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Projeto - Quarto de Ames", None, None)
    if not window:
        print("Falha ao criar janela GLFW")
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glEnable(GL_MULTISAMPLE)   # ativa o MSAA
    glfw.swap_interval(1)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    shader_program = shaders.create_shader_program()
    uniforms = shaders.get_uniform_locations(shader_program)
    glClearColor(0.15, 0.15, 0.15, 1.0)

    print("=" * 62)
    print(" CONTROLES:")
    print("   ESPACO  -> Alternar camera (focal / revelacao)")
    print("   MOUSE   -> (Revelacao) Arrastar gira, scroll da zoom")
    print("   WASD    -> (Revelacao) Mover o alvo da camera")
    print("   T       -> Reset da camera orbital")
    print("   P       -> Alternar modo automatico (esferas trocam de lugar)")
    print("   R       -> Resetar posicao das esferas")
    print("   SETAS   -> Mover a esfera VERDE (manual)")
    print("   ESC     -> Sair")
    print("=" * 62)

    #Carregamento de geometria e buffers OpenGL
    # Paredes + teto (sem o chão — removemos a linha de índices do chão em geometry.py)
    vert_paredes, ind_paredes = geometry.get_ames_room_solid()
    vao_paredes = geometry.setup_buffers(vert_paredes, ind_paredes)
    qtd_ind_paredes = len(ind_paredes)   # Agora são 24 índices

    # Chão em grid (com xadrez procedural)
    vert_chao, ind_chao = geometry.get_ames_floor_grid(n_cols=30, n_rows=30)
    vao_chao = geometry.setup_buffers(vert_chao, ind_chao)
    qtd_ind_chao = len(ind_chao)

    # Molduras (rodapé + sanca)
    vert_molduras, ind_molduras = geometry.get_molduras(altura=0.22, offset=0.015)
    vao_molduras = geometry.setup_buffers(vert_molduras, ind_molduras)
    qtd_ind_molduras = len(ind_molduras)

    # Janelas + Porta (decoração distorcida)
    vert_janelas, ind_janelas = geometry.get_janelas_e_porta()
    vao_janelas = geometry.setup_buffers(vert_janelas, ind_janelas)
    qtd_ind_janelas = len(ind_janelas)

    # --- Esfera única (raio 1.0, será escalada pela matriz de modelo) ---
    vert_esfera, ind_esfera = geometry.get_unit_sphere()
    vao_esfera, qtd_indices_esfera = geometry.setup_sphere_buffers(vert_esfera, ind_esfera)

    # Estado da câmera orbital (para o modo revelação)
    estado_orbital = input_handler.inicializar_estado_orbital()
    input_handler.configurar_callbacks(window, estado_orbital)

    # Loop principal
    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time

        process_input(window, delta_time, current_time, estado_orbital)

        # Colisão entre esferas — apenas quando NÃO estiver em modo automático
        # (no auto mode as esferas se cruzam de propósito)
        if not modo_automatico:
            esfera_x, esfera_z = physics.resolver_colisao_esferas(
                (esfera_x, esfera_z), RAIO_ESFERA,
                (gemea_x, gemea_z), RAIO_GEMEA
        )

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader_program)

        proj_matrix = camera.create_perspective_matrix(45.0, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)

        if camera_revelada:
            alvo_base = np.array([-1.0, 0.0, -12.0])
            eye = input_handler.calcular_eye_orbital(alvo_base, estado_orbital)
            target = input_handler.calcular_alvo_atual(alvo_base, estado_orbital)
            up = np.array([0.0, 0.0, -1.0])
        else:
            eye = np.array([0.0, 0.0, 0.0])
            target = np.array([0.0, 0.0, -10.0])
            up = np.array([0.0, 1.0, 0.0])

        view_matrix = camera.create_lookat_matrix(eye, target, up)

        glUniformMatrix4fv(uniforms['projection'], 1, GL_FALSE, proj_matrix.T)
        glUniformMatrix4fv(uniforms['view'], 1, GL_FALSE, view_matrix.T)
        glUniform3f(uniforms['lightPos'], 0.0, 1.8, -8.0)

        # Quarto
        renderer.desenhar_malha(uniforms, vao_chao, qtd_ind_chao)
        renderer.desenhar_malha(uniforms, vao_paredes, qtd_ind_paredes)
        renderer.desenhar_malha(uniforms, vao_molduras, qtd_ind_molduras)
        # Janelas e porta (decoração distorcida)
        renderer.desenhar_malha(uniforms, vao_janelas, qtd_ind_janelas)


        # Parede frontal com fechadura (por cima, na frente), NÃO USADO
        #renderer.desenhar_malha(uniforms, vao_parede, qtd_indices_parede)

        # Laranja (referência estática)
        gemea_y = physics.calcular_y_esfera(gemea_x, gemea_z, RAIO_GEMEA)
        renderer.desenhar_esfera(uniforms, vao_esfera, qtd_indices_esfera,
                                gemea_x, gemea_y, gemea_z, RAIO_GEMEA, (0.95, 0.45, 0.1))

        # Verde (controlável)
        esfera_y = physics.calcular_y_esfera(esfera_x, esfera_z, RAIO_ESFERA)
        renderer.desenhar_esfera(uniforms, vao_esfera, qtd_indices_esfera,
                                esfera_x, esfera_y, esfera_z, RAIO_ESFERA, (0.2, 0.85, 0.4))

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()