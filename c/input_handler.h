#pragma once
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>

struct CameraOrbital {
    float theta = 0.0f;
    float phi = 0.0f;
    float radius = 35.0f;
    glm::vec3 target_offset = glm::vec3(0.0f);
    
    // Controle interno do mouse
    bool arrastando = false;
    float ultimo_x = 0.0f;
    float ultimo_y = 0.0f;
};

void setup_callbacks(GLFWwindow* window);
void resetar_orbital(CameraOrbital& cam);
glm::vec3 calcular_eye_orbital(glm::vec3 alvo_base, const CameraOrbital& cam);
glm::vec3 calcular_alvo_atual(glm::vec3 alvo_base, const CameraOrbital& cam);
void pan_wasd(CameraOrbital& cam, GLFWwindow* window, float delta_time);