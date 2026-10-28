#pragma once
#include <glad/glad.h>
#include <glm/glm.hpp>
#include <vector>

struct Mesh {
    GLuint VAO, VBO, EBO;
    GLsizei indexCount;
};

Mesh createAmesRoomSolid();
Mesh createAmesFloorGrid(int n_cols = 30, int n_rows = 30);
Mesh createMolduras(float altura = 0.22f, float offset = 0.015f, float z_ref = 10.0f);
Mesh createJanelasEPorta();
Mesh createUnitSphere(int sectors = 30, int stacks = 30);