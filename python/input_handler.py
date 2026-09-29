# input_handler.py
# Gerencia os callbacks de mouse para a câmera orbital no modo revelação.

import math
import numpy as np
import glfw

# Sensibilidade base (radianos por pixel) — quando radius = RADIUS_REFERENCIA
SENSIBILIDADE_BASE = 0.003
RADIUS_REFERENCIA  = 35.0
RADIUS_MIN         = 15.0
RADIUS_MAX         = 80.0


def inicializar_estado_orbital():
    """Estado inicial da câmera orbital (top-down original)."""
    return {
        'theta': 0.0,
        'phi': 0.0,
        'radius': 35.0,
        'target_offset': np.array([0.0, 0.0, 0.0], dtype=np.float32),
        'arrastando': False,
        'ultimo_x': 0.0,
        'ultimo_y': 0.0,
    }


def resetar_orbital(estado):
    estado['theta'] = 0.0
    estado['phi'] = 0.0
    estado['radius'] = 35.0
    estado['target_offset'] = np.array([0.0, 0.0, 0.0], dtype=np.float32)


def calcular_eye_orbital(alvo_base, estado):
    theta = estado['theta']
    phi = estado['phi']
    radius = estado['radius']

    alvo = np.array(alvo_base) + estado['target_offset']
    phi = max(0.05, min(math.pi - 0.05, phi))

    x = alvo[0] + radius * math.sin(phi) * math.sin(theta)
    y = alvo[1] + radius * math.cos(phi)
    z = alvo[2] + radius * math.sin(phi) * math.cos(theta)
    return np.array([x, y, z], dtype=np.float32)


def calcular_alvo_atual(alvo_base, estado):
    return np.array(alvo_base) + estado['target_offset']


def pan_wasd(estado, window, delta_time):
    """Move o target_offset com WASD, relativo à direção da câmera."""
    velocidade = 6.0 * delta_time
    theta = estado['theta']

    forward = np.array([-math.sin(theta), 0.0, -math.cos(theta)], dtype=np.float32)
    right   = np.array([ math.cos(theta), 0.0, -math.sin(theta)], dtype=np.float32)

    offset = estado['target_offset']

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:  offset += forward * velocidade
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:  offset -= forward * velocidade
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:  offset -= right   * velocidade
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:  offset += right   * velocidade

    offset[0] = max(-8.0, min(8.0, offset[0]))
    offset[2] = max(-15.0, min(5.0, offset[2]))


def configurar_callbacks(window, estado_orbital):
    """Registra callbacks do mouse."""

    def on_mouse_button(win, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                estado_orbital['arrastando'] = True
                estado_orbital['ultimo_x'], estado_orbital['ultimo_y'] = glfw.get_cursor_pos(win)
            elif action == glfw.RELEASE:
                estado_orbital['arrastando'] = False

    def on_cursor_pos(win, xpos, ypos):
        if not estado_orbital['arrastando']:
            return
        dx = xpos - estado_orbital['ultimo_x']
        dy = ypos - estado_orbital['ultimo_y']
        estado_orbital['ultimo_x'] = xpos
        estado_orbital['ultimo_y'] = ypos

        # Sensibilidade adaptativa: quanto menor o radius, mais fino o giro
        radius = estado_orbital['radius']
        fator = radius / RADIUS_REFERENCIA
        sensibilidade = SENSIBILIDADE_BASE * fator

        estado_orbital['theta'] -= dx * sensibilidade
        estado_orbital['phi']   -= dy * sensibilidade

    def on_scroll(win, xoffset, yoffset):
        estado_orbital['radius'] -= yoffset * 2.0
        estado_orbital['radius'] = max(RADIUS_MIN, min(RADIUS_MAX, estado_orbital['radius']))

    glfw.set_mouse_button_callback(window, on_mouse_button)
    glfw.set_cursor_pos_callback(window, on_cursor_pos)
    glfw.set_scroll_callback(window, on_scroll)