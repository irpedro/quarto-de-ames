#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/constants.hpp>
#include <iostream>
#include <cmath>
#include "Shader.h"
#include "geometry.h"
#include "physics.h"
#include "input_handler.h"

const unsigned int SCR_WIDTH = 800;
const unsigned int SCR_HEIGHT = 600;

// Estado Global
bool camera_revelada = false;
bool modo_automatico = false;

// Esferas
float esfera_x = 1.6f, esfera_z = -5.35f;
const float RAIO_ESFERA = 0.35f;
float gemea_x = -2.0f, gemea_z = -14.0f;
const float RAIO_GEMEA = 0.70f;

// Posições Home
const float HOME_GREEN_X = 1.6f, HOME_GREEN_Z = -5.35f;
const float HOME_ORANGE_X = -2.0f, HOME_ORANGE_Z = -14.0f;
const float AUTO_FREQUENCIA = 0.3f;

void framebuffer_size_callback(GLFWwindow* window, int width, int height) {
    glViewport(0, 0, width, height);
}

int main() {
    glfwInit();
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 2);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    
    // --- MSAA 16x ---
    glfwWindowHint(GLFW_SAMPLES, 16);

    GLFWwindow* window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "Quarto de Ames - C++", NULL, NULL);
    if (window == NULL) {
        std::cout << "Falha ao criar janela GLFW" << std::endl;
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);
    glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cout << "Falha ao inicializar GLAD" << std::endl;
        return -1;
    }

    std::cout << "==============================================================" << std::endl;
    std::cout << " CONTROLES:" << std::endl;
    std::cout << "   ESPACO  -> Alternar camera (focal / revelacao)" << std::endl;
    std::cout << "   MOUSE   -> (Revelacao) Arrastar gira, scroll da zoom" << std::endl;
    std::cout << "   WASD    -> (Revelacao) Mover o alvo da camera" << std::endl;
    std::cout << "   T       -> Reset da camera orbital" << std::endl;
    std::cout << "   P       -> Alternar modo automatico (esferas trocam de lugar)" << std::endl;
    std::cout << "   R       -> Resetar posicao das esferas" << std::endl;
    std::cout << "   SETAS   -> Mover a esfera VERDE (manual)" << std::endl;
    std::cout << "   ESC     -> Sair" << std::endl;
    std::cout << "==============================================================" << std::endl;

    // --- Ativar MSAA ---
    glEnable(GL_MULTISAMPLE);

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    glCullFace(GL_BACK);

    // Setup Câmera Orbital
    CameraOrbital camOrbital;
    glfwSetWindowUserPointer(window, &camOrbital);
    setup_callbacks(window);

    Shader shaderProgram("Shaders/common.incl", "Shaders/basico.vs", "Shaders/basico.frag");

    // Carrega geometrias
    Mesh room = createAmesRoomSolid();
    Mesh floor = createAmesFloorGrid(30, 30);
    Mesh molduras = createMolduras(0.22f, 0.015f, 10.0f);
    Mesh decoracao = createJanelasEPorta();
    Mesh sphere = createUnitSphere(30, 30);

    glm::mat4 projection = glm::perspective(glm::radians(45.0f), (float)SCR_WIDTH / (float)SCR_HEIGHT, 0.1f, 100.0f);
    float lastTime = glfwGetTime();

    while (!glfwWindowShouldClose(window)) {
        float currentTime = glfwGetTime();
        float deltaTime = currentTime - lastTime;
        lastTime = currentTime;

        // --- INPUTS DE ESTADO (Teclas de Toggle) ---
        static bool espaco_antes = false, p_antes = false, t_antes = false, r_antes = false;
        
        bool espaco_agora = glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS;
        if (espaco_agora && !espaco_antes) {
            camera_revelada = !camera_revelada;
            std::cout << ">>> Camera " << (camera_revelada ? "REVELADA" : "FOCAL") << std::endl;
        }
        espaco_antes = espaco_agora;

        bool p_agora = glfwGetKey(window, GLFW_KEY_P) == GLFW_PRESS;
        if (p_agora && !p_antes) {
            modo_automatico = !modo_automatico;
            std::cout << ">>> Modo automatico " << (modo_automatico ? "ATIVADO" : "DESATIVADO") << std::endl;
        }
        p_antes = p_agora;

        bool t_agora = glfwGetKey(window, GLFW_KEY_T) == GLFW_PRESS;
        if (t_agora && !t_antes) {
            resetar_orbital(camOrbital);
            std::cout << ">>> Camera orbital resetada (top-down)" << std::endl;
        }
        t_antes = t_agora;

        bool r_agora = glfwGetKey(window, GLFW_KEY_R) == GLFW_PRESS;
        if (r_agora && !r_antes) {
            esfera_x = HOME_GREEN_X; esfera_z = HOME_GREEN_Z;
            gemea_x = HOME_ORANGE_X; gemea_z = HOME_ORANGE_Z;
            modo_automatico = false;
            std::cout << ">>> Esferas resetadas + modo automatico desativado" << std::endl;
        }
        r_antes = r_agora;

        if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) glfwSetWindowShouldClose(window, true);

        // --- LÓGICA DE MOVIMENTO ---
        if (camera_revelada) {
            pan_wasd(camOrbital, window, deltaTime);
        }

        if (modo_automatico) {
            float fator = (sin(currentTime * AUTO_FREQUENCIA * 2.0f * glm::pi<float>()) + 1.0f) / 2.0f;
            esfera_x = HOME_GREEN_X + (HOME_ORANGE_X - HOME_GREEN_X) * fator;
            esfera_z = HOME_GREEN_Z + (HOME_ORANGE_Z - HOME_GREEN_Z) * fator;
            gemea_x = HOME_ORANGE_X + (HOME_GREEN_X - HOME_ORANGE_X) * fator;
            gemea_z = HOME_ORANGE_Z + (HOME_GREEN_Z - HOME_ORANGE_Z) * fator;
            
            glm::vec2 c1 = clamp_esfera(esfera_x, esfera_z, RAIO_ESFERA);
            esfera_x = c1.x; esfera_z = c1.y;
            glm::vec2 c2 = clamp_esfera(gemea_x, gemea_z, RAIO_GEMEA);
            gemea_x = c2.x; gemea_z = c2.y;
        } else {
            // Controle manual com setas
            float velocidade = 4.0f * deltaTime;
            if (glfwGetKey(window, GLFW_KEY_UP) == GLFW_PRESS)    esfera_z -= velocidade;
            if (glfwGetKey(window, GLFW_KEY_DOWN) == GLFW_PRESS)  esfera_z += velocidade;
            if (glfwGetKey(window, GLFW_KEY_LEFT) == GLFW_PRESS)  esfera_x -= velocidade;
            if (glfwGetKey(window, GLFW_KEY_RIGHT) == GLFW_PRESS) esfera_x += velocidade;
            
            glm::vec2 clamped = clamp_esfera(esfera_x, esfera_z, RAIO_ESFERA);
            esfera_x = clamped.x; esfera_z = clamped.y;
            
            glm::vec2 col = resolver_colisao_esferas(glm::vec2(esfera_x, esfera_z), RAIO_ESFERA, glm::vec2(gemea_x, gemea_z), RAIO_GEMEA);
            esfera_x = col.x; esfera_z = col.y;
        }

        float esfera_y = calcular_y_esfera(esfera_x, esfera_z, RAIO_ESFERA);
        float gemea_y = calcular_y_esfera(gemea_x, gemea_z, RAIO_GEMEA);

        // --- CÂMERA ---
        glm::vec3 eye, target, up;
        if (camera_revelada) {
            glm::vec3 alvo_base(-1.0f, 0.0f, -12.0f);
            eye = calcular_eye_orbital(alvo_base, camOrbital);
            target = calcular_alvo_atual(alvo_base, camOrbital);
            up = glm::vec3(0.0f, 0.0f, -1.0f);
        } else {
            eye = glm::vec3(0.0f, 0.0f, 0.0f);
            target = glm::vec3(0.0f, 0.0f, -10.0f);
            up = glm::vec3(0.0f, 1.0f, 0.0f);
        }
        glm::mat4 view = glm::lookAt(eye, target, up);

        // --- RENDERIZAÇÃO ---
        glClearColor(0.15f, 0.15f, 0.15f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

        shaderProgram.use();
        shaderProgram.setMat4("projection", projection);
        shaderProgram.setMat4("view", view);
        shaderProgram.setVec3("lightPos", glm::vec3(0.0f, 1.8f, -8.0f));

        // Chão
        shaderProgram.setInt("enableChecker", 1);
        shaderProgram.setMat4("model", glm::mat4(1.0f));
        glBindVertexArray(floor.VAO);
        glDrawElements(GL_TRIANGLES, floor.indexCount, GL_UNSIGNED_INT, 0);

        // Paredes e Decoração
        shaderProgram.setInt("enableChecker", 0);
        shaderProgram.setVec3("objectColor", glm::vec3(1.0f));
        
        glBindVertexArray(room.VAO);
        glDrawElements(GL_TRIANGLES, room.indexCount, GL_UNSIGNED_INT, 0);
        glBindVertexArray(molduras.VAO);
        glDrawElements(GL_TRIANGLES, molduras.indexCount, GL_UNSIGNED_INT, 0);
        glBindVertexArray(decoracao.VAO);
        glDrawElements(GL_TRIANGLES, decoracao.indexCount, GL_UNSIGNED_INT, 0);

        // Esferas
        glBindVertexArray(sphere.VAO);
        
        glm::mat4 modelLaranja = glm::translate(glm::mat4(1.0f), glm::vec3(gemea_x, gemea_y, gemea_z));
        modelLaranja = glm::scale(modelLaranja, glm::vec3(RAIO_GEMEA));
        shaderProgram.setMat4("model", modelLaranja);
        shaderProgram.setVec3("objectColor", glm::vec3(0.95f, 0.45f, 0.1f));
        glDrawElements(GL_TRIANGLES, sphere.indexCount, GL_UNSIGNED_INT, 0);

        glm::mat4 modelVerde = glm::translate(glm::mat4(1.0f), glm::vec3(esfera_x, esfera_y, esfera_z));
        modelVerde = glm::scale(modelVerde, glm::vec3(RAIO_ESFERA));
        shaderProgram.setMat4("model", modelVerde);
        shaderProgram.setVec3("objectColor", glm::vec3(0.2f, 0.85f, 0.4f));
        glDrawElements(GL_TRIANGLES, sphere.indexCount, GL_UNSIGNED_INT, 0);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwTerminate();
    return 0;
}