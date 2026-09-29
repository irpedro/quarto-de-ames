# renderer.py
# Funções de desenho reutilizáveis. Serão chamadas pela câmera principal
# E pelo Shadow Mapping (que renderiza a cena do ponto de vista da luz).

import numpy as np
from OpenGL.GL import *

def desenhar_malha(uniforms, vao, qtd_indices):
    """Desenha qualquer malha estática (quarto, parede) com objectColor branco."""
    glUniform3f(uniforms['objectColor'], 1.0, 1.0, 1.0)
    glUniform1i(uniforms['enableChecker'], 1)
    model = np.identity(4, dtype=np.float32)
    glUniformMatrix4fv(uniforms['model'], 1, GL_FALSE, model.T)
    glBindVertexArray(vao)
    glDrawElements(GL_TRIANGLES, qtd_indices, GL_UNSIGNED_INT, None)


def desenhar_esfera(uniforms, vao_esfera, qtd_indices, x, y, z, raio, cor):
    """Desenha uma esfera com escala (raio), posição e cor."""
    glUniform1i(uniforms['enableChecker'], 0)
    model = np.identity(4, dtype=np.float32)
    model[0, 0] = raio
    model[1, 1] = raio
    model[2, 2] = raio
    model[0, 3] = x
    model[1, 3] = y
    model[2, 3] = z
    glUniform3f(uniforms['objectColor'], *cor)
    glUniformMatrix4fv(uniforms['model'], 1, GL_FALSE, model.T)
    glBindVertexArray(vao_esfera)
    glDrawElements(GL_TRIANGLES, qtd_indices, GL_UNSIGNED_INT, None)