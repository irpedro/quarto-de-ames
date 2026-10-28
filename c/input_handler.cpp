#include "input_handler.h"
#include <cmath>
#include <algorithm>
#include <glm/gtc/constants.hpp>

// Constantes de sensibilidade
const float SENSIBILIDADE_BASE = 0.003f;
const float RADIUS_REFERENCIA = 35.0f;
const float RADIUS_MIN = 15.0f;
const float RADIUS_MAX = 80.0f;

void resetar_orbital(CameraOrbital& cam) {
    cam.theta = 0.0f;
    cam.phi = 0.0f;
    cam.radius = 35.0f;
    cam.target_offset = glm::vec3(0.0f);
}

glm::vec3 calcular_eye_orbital(glm::vec3 alvo_base, const CameraOrbital& cam) {
    glm::vec3 alvo = alvo_base + cam.target_offset;
    float phi = std::max(0.05f, std::min(glm::pi<float>() - 0.05f, cam.phi));

    float x = alvo.x + cam.radius * sin(phi) * sin(cam.theta);
    float y = alvo.y + cam.radius * cos(phi);
    float z = alvo.z + cam.radius * sin(phi) * cos(cam.theta);
    return glm::vec3(x, y, z);
}

glm::vec3 calcular_alvo_atual(glm::vec3 alvo_base, const CameraOrbital& cam) {
    return alvo_base + cam.target_offset;
}

void pan_wasd(CameraOrbital& cam, GLFWwindow* window, float delta_time) {
    float velocidade = 6.0f * delta_time;
    float theta = cam.theta;

    glm::vec3 forward(-sin(theta), 0.0f, -cos(theta));
    glm::vec3 right(cos(theta), 0.0f, -sin(theta));

    if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS) cam.target_offset += forward * velocidade;
    if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS) cam.target_offset -= forward * velocidade;
    if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS) cam.target_offset -= right * velocidade;
    if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS) cam.target_offset += right * velocidade;

    cam.target_offset.x = std::max(-8.0f, std::min(8.0f, cam.target_offset.x));
    cam.target_offset.z = std::max(-15.0f, std::min(5.0f, cam.target_offset.z));
}

// --- Callbacks do GLFW ---
static void mouse_button_callback(GLFWwindow* window, int button, int action, int mods) {
    CameraOrbital* cam = (CameraOrbital*)glfwGetWindowUserPointer(window);
    if (button == GLFW_MOUSE_BUTTON_LEFT) {
        if (action == GLFW_PRESS) {
            cam->arrastando = true;
            double x, y;
            glfwGetCursorPos(window, &x, &y);
            cam->ultimo_x = (float)x;
            cam->ultimo_y = (float)y;
        } else if (action == GLFW_RELEASE) {
            cam->arrastando = false;
        }
    }
}

static void cursor_position_callback(GLFWwindow* window, double xpos, double ypos) {
    CameraOrbital* cam = (CameraOrbital*)glfwGetWindowUserPointer(window);
    if (!cam->arrastando) return;

    float dx = (float)xpos - cam->ultimo_x;
    float dy = (float)ypos - cam->ultimo_y;
    cam->ultimo_x = (float)xpos;
    cam->ultimo_y = (float)ypos;

    // Sensibilidade adaptativa
    float fator = cam->radius / RADIUS_REFERENCIA;
    float sensibilidade = SENSIBILIDADE_BASE * fator;

    cam->theta -= dx * sensibilidade;
    cam->phi -= dy * sensibilidade;
}

static void scroll_callback(GLFWwindow* window, double xoffset, double yoffset) {
    CameraOrbital* cam = (CameraOrbital*)glfwGetWindowUserPointer(window);
    cam->radius -= (float)yoffset * 2.0f;
    cam->radius = std::max(RADIUS_MIN, std::min(RADIUS_MAX, cam->radius));
}

void setup_callbacks(GLFWwindow* window) {
    glfwSetMouseButtonCallback(window, mouse_button_callback);
    glfwSetCursorPosCallback(window, cursor_position_callback);
    glfwSetScrollCallback(window, scroll_callback);
}