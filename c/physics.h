#pragma once
#include <glm/glm.hpp>

float calcular_altura_chao(float x, float z);
float calcular_y_esfera(float x, float z, float r);
glm::vec2 clamp_esfera(float x, float z, float r);
glm::vec2 resolver_colisao_esferas(glm::vec2 pos_verde, float raio_verde, glm::vec2 pos_laranja, float raio_laranja);