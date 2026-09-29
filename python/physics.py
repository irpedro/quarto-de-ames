# physics.py
# Toda a matemática de chão, colisão e animação do Quarto de Ames.
# Nenhuma chamada OpenGL aqui — apenas matemática pura (numpy).

import numpy as np
import math

def calcular_altura_chao(x, z):
    """
    Metade direita/frontal do quarto é 100% plana (Y = -2).
    Metade esquerda/fundo é uma rampa contínua.
    A dobra segue a diagonal Frente-Esquerdo -> Fundo-Direito.
    """
    if z >= (-1.25 * x - 7.5):
        return -2.0
    else:
        return (10.0 * x + 8.0 * z - 80.0) / 70.0


def calcular_y_esfera(x, z, r):
    """Amostra 5 pontos sob a esfera e retorna o contato mais alto (+ raio)."""
    margem = r * 0.6
    alturas = [
        calcular_altura_chao(x, z),
        calcular_altura_chao(x - margem, z),
        calcular_altura_chao(x + margem, z),
        calcular_altura_chao(x, z - margem),
        calcular_altura_chao(x, z + margem)
    ]
    return max(alturas) + r + 0.02


def clamp_esfera(x, z, r):
    """Mantém a esfera dentro do quarto respeitando todas as paredes."""
    # Parede direita (ortogonal)
    if x > 2.0 - r:
        x = 2.0 - r

    # Parede frontal (entrada)
    if z > -5.0 - r:
        z = -5.0 - r

    # Parede esquerda (diagonal) - margem 1.1
    t_z = max(0.0, min(1.0, (z - (-5.0)) / (-15.0)))
    parede_x_esq = -2.0 - 2.0 * t_z
    if x < parede_x_esq + (r * 1.1):
        x = parede_x_esq + (r * 1.1)

    # Parede do fundo (diagonal extrema) - margem 2.2
    limite_z_fundo = (5.0 / 3.0) * x - 13.333 + (r * 2.8)
    if z < limite_z_fundo:
        z = limite_z_fundo

    return x, z


def resolver_colisao_esferas(pos_verde, raio_verde, pos_laranja, raio_laranja):
    """
    Se as duas esferas se sobrepõem, empurra a verde para fora.
    Retorna a nova posição (x, z) da esfera verde.
    """
    x_v, z_v = pos_verde
    x_l, z_l = pos_laranja

    dx = x_v - x_l
    dz = z_v - z_l
    dist_sq = dx * dx + dz * dz
    min_dist = raio_verde + raio_laranja

    if dist_sq < min_dist * min_dist and dist_sq > 1e-6:
        dist = math.sqrt(dist_sq)
        overlap = min_dist - dist + 0.01
        x_v += (dx / dist) * overlap
        z_v += (dz / dist) * overlap
        x_v, z_v = clamp_esfera(x_v, z_v, raio_verde)

    return x_v, z_v