#include "physics.h"
#include <cmath>
#include <algorithm>

float calcular_altura_chao(float x, float z) {
    if (z >= (-1.25f * x - 7.5f)) {
        return -2.0f;
    } else {
        return (10.0f * x + 8.0f * z - 80.0f) / 70.0f;
    }
}

float calcular_y_esfera(float x, float z, float r) {
    float margem = r * 0.6f;
    float h1 = calcular_altura_chao(x, z);
    float h2 = calcular_altura_chao(x - margem, z);
    float h3 = calcular_altura_chao(x + margem, z);
    float h4 = calcular_altura_chao(x, z - margem);
    float h5 = calcular_altura_chao(x, z + margem);

    float max_h = std::max({h1, h2, h3, h4, h5});
    return max_h + r + 0.02f;
}

glm::vec2 clamp_esfera(float x, float z, float r) {
    // Parede direita
    if (x > 2.0f - r) x = 2.0f - r;

    // Parede frontal
    if (z > -5.0f - r) z = -5.0f - r;

    // Parede esquerda
    float t_z = std::max(0.0f, std::min(1.0f, (z - (-5.0f)) / (-15.0f)));
    float parede_x_esq = -2.0f - 2.0f * t_z;
    if (x < parede_x_esq + (r * 1.1f)) x = parede_x_esq + (r * 1.1f);

    // Parede do fundo
    float limite_z_fundo = (5.0f / 3.0f) * x - 13.333f + (r * 2.8f);
    if (z < limite_z_fundo) z = limite_z_fundo;

    return glm::vec2(x, z);
}

glm::vec2 resolver_colisao_esferas(glm::vec2 pos_verde, float raio_verde, glm::vec2 pos_laranja, float raio_laranja) {
    float dx = pos_verde.x - pos_laranja.x;
    float dz = pos_verde.y - pos_laranja.y;
    float dist_sq = dx * dx + dz * dz;
    float min_dist = raio_verde + raio_laranja;

    if (dist_sq < min_dist * min_dist && dist_sq > 1e-6f) {
        float dist = std::sqrt(dist_sq);
        float overlap = min_dist - dist + 0.01f;
        pos_verde.x += (dx / dist) * overlap;
        pos_verde.y += (dz / dist) * overlap;
        pos_verde = clamp_esfera(pos_verde.x, pos_verde.y, raio_verde);
    }
    return pos_verde;
}