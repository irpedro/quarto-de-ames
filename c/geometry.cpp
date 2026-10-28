#include "geometry.h"
#include <iostream>
#include <glm/gtc/constants.hpp>

glm::vec3 calculateNormal(glm::vec3 p1, glm::vec3 p2, glm::vec3 p3) {
    glm::vec3 v1 = p2 - p1;
    glm::vec3 v2 = p3 - p1;
    return glm::normalize(glm::cross(v1, v2));
}

Mesh createAmesRoomSolid() {
    std::vector<float> vertices;
    std::vector<unsigned int> indices;

    // Cores base
    glm::vec3 C_TETO(0.8f, 0.8f, 0.8f);
    glm::vec3 C_ESQ(0.8f, 0.2f, 0.2f);
    glm::vec3 C_DIR(0.2f, 0.2f, 0.8f);
    glm::vec3 C_FUND(0.8f, 0.8f, 0.2f);
    glm::vec3 C_CHAO(0.3f, 0.3f, 0.3f); 

    // Cálculo das Normais
    glm::vec3 N_TETO = calculateNormal({2.0f, 2.0f, -5.0f}, {-2.0f, 2.0f, -5.0f}, {-4.0f, 4.0f, -20.0f});
    glm::vec3 N_ESQ = calculateNormal({-2.0f, -2.0f, -5.0f}, {-4.0f, -4.0f, -20.0f}, {-4.0f, 4.0f, -20.0f});
    glm::vec3 N_DIR = calculateNormal({2.0f, -2.0f, -10.0f}, {2.0f, -2.0f, -5.0f}, {2.0f, 2.0f, -5.0f});
    glm::vec3 N_FUND = calculateNormal({2.0f, -2.0f, -10.0f}, {2.0f, 2.0f, -10.0f}, {-4.0f, 4.0f, -20.0f});

    // Função auxiliar para adicionar vértice (Posição, Cor, Normal)
    auto addVertex = [&](glm::vec3 pos, glm::vec3 color, glm::vec3 normal) {
        vertices.insert(vertices.end(), {pos.x, pos.y, pos.z, color.x, color.y, color.z, normal.x, normal.y, normal.z});
    };

    // Chão (0-3) - mantido apenas para os índices baterem com o Python
    addVertex({ 2.0f, -2.0f,  -5.0f}, C_CHAO, N_TETO);
    addVertex({-2.0f, -2.0f,  -5.0f}, C_CHAO, N_TETO);
    addVertex({-4.0f, -4.0f, -20.0f}, C_CHAO, N_TETO);
    addVertex({ 2.0f, -2.0f, -10.0f}, C_CHAO, N_TETO);

    // Teto (4-7)
    addVertex({ 2.0f,  2.0f,  -5.0f}, C_TETO, N_TETO);
    addVertex({-2.0f,  2.0f,  -5.0f}, C_TETO, N_TETO);
    addVertex({-4.0f,  4.0f, -20.0f}, C_TETO, N_TETO);
    addVertex({ 2.0f,  2.0f, -10.0f}, C_TETO, N_TETO);

    // Parede Esquerda (8-11)
    addVertex({-2.0f, -2.0f,  -5.0f}, C_ESQ, N_ESQ);
    addVertex({-4.0f, -4.0f, -20.0f}, C_ESQ, N_ESQ);
    addVertex({-4.0f,  4.0f, -20.0f}, C_ESQ, N_ESQ);
    addVertex({-2.0f,  2.0f,  -5.0f}, C_ESQ, N_ESQ);

    // Parede Direita (12-15)
    addVertex({ 2.0f, -2.0f, -10.0f}, C_DIR, N_DIR);
    addVertex({ 2.0f, -2.0f,  -5.0f}, C_DIR, N_DIR);
    addVertex({ 2.0f,  2.0f,  -5.0f}, C_DIR, N_DIR);
    addVertex({ 2.0f,  2.0f, -10.0f}, C_DIR, N_DIR);

    // Parede Fundo (16-19)
    addVertex({ 2.0f, -2.0f, -10.0f}, C_FUND, N_FUND);
    addVertex({-4.0f, -4.0f, -20.0f}, C_FUND, N_FUND);
    addVertex({-4.0f,  4.0f, -20.0f}, C_FUND, N_FUND);
    addVertex({ 2.0f,  2.0f, -10.0f}, C_FUND, N_FUND);

    // Índices (Paredes + Teto, sem o chão)
    indices = {
        4, 5, 6,    4, 6, 7,       // Teto 
        8, 9, 10,   8, 10, 11,     // Esquerda
        12, 13, 14, 12, 14, 15,    // Direita
        16, 19, 18, 16, 18, 17     // Fundo
    };

    // Configuração OpenGL
    Mesh mesh;
    glGenVertexArrays(1, &mesh.VAO);
    glGenBuffers(1, &mesh.VBO);
    glGenBuffers(1, &mesh.EBO);

    glBindVertexArray(mesh.VAO);

    glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    // Atributo 0: Posição
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);

    // Atributo 1: Cor
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);

    // Atributo 2: Normal (não usada agora, mas preparamos o terreno)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(6 * sizeof(float)));
    glEnableVertexAttribArray(2);

    glBindVertexArray(0);

    mesh.indexCount = indices.size();
    return mesh;
}

Mesh createAmesFloorGrid(int n_cols, int n_rows) {
    std::vector<float> vertices;
    std::vector<unsigned int> indices;

    glm::vec3 C_CHAO(0.3f, 0.3f, 0.3f);
    glm::vec3 N_CHAO = calculateNormal({-2.0f, -2.0f, -5.0f}, {2.0f, -2.0f, -10.0f}, {-4.0f, -4.0f, -20.0f});

    glm::vec3 C0( 2.0f, -2.0f,  -5.0f);
    glm::vec3 C1(-2.0f, -2.0f,  -5.0f);
    glm::vec3 C2(-4.0f, -4.0f, -20.0f);
    glm::vec3 C3( 2.0f, -2.0f, -10.0f);

    auto addVertex = [&](glm::vec3 pos, glm::vec3 color, glm::vec3 normal) {
        vertices.insert(vertices.end(), {pos.x, pos.y, pos.z, color.x, color.y, color.z, normal.x, normal.y, normal.z});
    };

    // Gerar grade de vértices
    for (int i = 0; i <= n_rows; i++) {
        float v = (float)i / n_rows;
        for (int j = 0; j <= n_cols; j++) {
            float u = (float)j / n_cols;
            glm::vec3 frente = C0 * (1.0f - u) + C1 * u;
            glm::vec3 fundo  = C3 * (1.0f - u) + C2 * u;
            glm::vec3 ponto  = frente * (1.0f - v) + fundo * v;
            addVertex(ponto, C_CHAO, N_CHAO);
        }
    }

    // Índices
    for (int i = 0; i < n_rows; i++) {
        for (int j = 0; j < n_cols; j++) {
            unsigned int  a = i * (n_cols + 1) + j;
            unsigned int  b = a + 1;
            unsigned int  c = a + (n_cols + 1);
            unsigned int  d = c + 1;
            indices.insert(indices.end(), {a, c, b, b, c, d});
        }
    }

    Mesh mesh;
    glGenVertexArrays(1, &mesh.VAO);
    glGenBuffers(1, &mesh.VBO);
    glGenBuffers(1, &mesh.EBO);

    glBindVertexArray(mesh.VAO);
    glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(6 * sizeof(float)));
    glEnableVertexAttribArray(2);

    glBindVertexArray(0);
    mesh.indexCount = indices.size();
    return mesh;
}

Mesh createMolduras(float altura, float offset, float z_ref) {
    std::vector<float> vertices;
    std::vector<unsigned int> indices;

    glm::vec3 C_RODAPE(0.35f, 0.25f, 0.18f);
    glm::vec3 C_SANCA(0.92f, 0.90f, 0.85f);

    glm::vec3 N_ESQ  = calculateNormal({-2.0f, -2.0f, -5.0f}, {-4.0f, -4.0f, -20.0f}, {-4.0f, 4.0f, -20.0f});
    glm::vec3 N_DIR  = calculateNormal({2.0f, -2.0f, -10.0f}, {2.0f, -2.0f, -5.0f}, {2.0f, 2.0f, -5.0f});
    glm::vec3 N_FUND = calculateNormal({2.0f, -2.0f, -10.0f}, {2.0f, 2.0f, -10.0f}, {-4.0f, 4.0f, -20.0f});

    auto addVertex = [&](glm::vec3 pos, glm::vec3 color, glm::vec3 normal) {
        vertices.insert(vertices.end(), {pos.x, pos.y, pos.z, color.x, color.y, color.z, normal.x, normal.y, normal.z});
    };

    auto add_faixa = [&](glm::vec3 p1, glm::vec3 p2, glm::vec3 normal, glm::vec3 cor, float sinal_y) {
        glm::vec3 d = normal * offset;
        float h1 = altura * (std::abs(p1.z) / std::abs(z_ref));
        float h2 = altura * (std::abs(p2.z) / std::abs(z_ref));

        unsigned int base = vertices.size() / 9;

        addVertex(p1 + d, cor, normal);
        addVertex(p2 + d, cor, normal);
        addVertex(glm::vec3(p1.x, p1.y + sinal_y * h1, p1.z) + d, cor, normal);
        addVertex(glm::vec3(p2.x, p2.y + sinal_y * h2, p2.z) + d, cor, normal);

        indices.insert(indices.end(), {base, base + 1, base + 2, base + 1, base + 3, base + 2});
    };

    // Rodapés (sinal +1 = sobe)
    add_faixa({-2.0f, -2.0f,  -5.0f}, {-4.0f, -4.0f, -20.0f}, N_ESQ,  C_RODAPE, +1.0f);
    add_faixa({ 2.0f, -2.0f, -10.0f}, { 2.0f, -2.0f,  -5.0f}, N_DIR,  C_RODAPE, +1.0f);
    add_faixa({-4.0f, -4.0f, -20.0f}, { 2.0f, -2.0f, -10.0f}, N_FUND, C_RODAPE, +1.0f);

    // Sancas (sinal -1 = desce)
    add_faixa({-4.0f,  4.0f, -20.0f}, {-2.0f,  2.0f,  -5.0f}, N_ESQ,  C_SANCA, -1.0f);
    add_faixa({ 2.0f,  2.0f,  -5.0f}, { 2.0f,  2.0f, -10.0f}, N_DIR,  C_SANCA, -1.0f);
    add_faixa({ 2.0f,  2.0f, -10.0f}, {-4.0f,  4.0f, -20.0f}, N_FUND, C_SANCA, -1.0f);

    Mesh mesh;
    glGenVertexArrays(1, &mesh.VAO);
    glGenBuffers(1, &mesh.VBO);
    glGenBuffers(1, &mesh.EBO);

    glBindVertexArray(mesh.VAO);
    glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(6 * sizeof(float)));
    glEnableVertexAttribArray(2);

    glBindVertexArray(0);
    mesh.indexCount = indices.size();
    return mesh;
}

Mesh createJanelasEPorta() {
    std::vector<float> vertices;
    std::vector<unsigned int> indices;

    glm::vec3 C_MOLDURA(0.12f, 0.06f, 0.04f);
    glm::vec3 C_VIDRO_ESQ(0.10f, 0.22f, 0.45f);
    glm::vec3 C_VIDRO_DIR(0.15f, 0.32f, 0.55f);
    glm::vec3 C_PORTA(0.40f, 0.22f, 0.10f);

    glm::vec3 N_ESQ  = calculateNormal({-2.0f, -2.0f, -5.0f}, {-4.0f, -4.0f, -20.0f}, {-4.0f, 4.0f, -20.0f});
    glm::vec3 N_DIR  = calculateNormal({2.0f, -2.0f, -10.0f}, {2.0f, -2.0f, -5.0f}, {2.0f, 2.0f, -5.0f});
    glm::vec3 N_FUND = calculateNormal({2.0f, -2.0f, -10.0f}, {2.0f, 2.0f, -10.0f}, {-4.0f, 4.0f, -20.0f});

    auto addVertex = [&](glm::vec3 pos, glm::vec3 color, glm::vec3 normal) {
        vertices.insert(vertices.end(), {pos.x, pos.y, pos.z, color.x, color.y, color.z, normal.x, normal.y, normal.z});
    };

    auto add_quad = [&](glm::vec3 p0, glm::vec3 p1, glm::vec3 p2, glm::vec3 p3, glm::vec3 cor, glm::vec3 normal, float offset) {
        glm::vec3 d = normal * offset;
        unsigned int base = vertices.size() / 9;
        addVertex(p0 + d, cor, normal);
        addVertex(p1 + d, cor, normal);
        addVertex(p2 + d, cor, normal);
        addVertex(p3 + d, cor, normal);
        indices.insert(indices.end(), {base, base + 1, base + 2, base, base + 2, base + 3});
    };

    auto pontoUV = [](glm::vec3 p00, glm::vec3 p10, glm::vec3 p11, glm::vec3 p01, float u, float v) {
        glm::vec3 b = p00 + (p10 - p00) * u;
        glm::vec3 t = p01 + (p11 - p01) * u;
        return b + (t - b) * v;
    };

    auto add_janela = [&](glm::vec3 p00, glm::vec3 p10, glm::vec3 p11, glm::vec3 p01, 
                          float u0, float u1, float v0, float v1, glm::vec3 cor_vidro, glm::vec3 normal) {
        float esp = 0.022f;
        float ov = esp * 0.5f;
        float gap = esp * 0.35f;
        float off_frame = 0.030f;
        float off_glass = 0.015f;
        float off_mullion = 0.035f;

        // Moldura Superior
        add_quad(pontoUV(p00,p10,p11,p01, u0-esp, v1), pontoUV(p00,p10,p11,p01, u1+esp, v1),
                 pontoUV(p00,p10,p11,p01, u1+esp, v1+esp), pontoUV(p00,p10,p11,p01, u0-esp, v1+esp), C_MOLDURA, normal, off_frame);
        // Moldura Inferior
        add_quad(pontoUV(p00,p10,p11,p01, u0-esp, v0-esp), pontoUV(p00,p10,p11,p01, u1+esp, v0-esp),
                 pontoUV(p00,p10,p11,p01, u1+esp, v0), pontoUV(p00,p10,p11,p01, u0-esp, v0), C_MOLDURA, normal, off_frame);
        // Moldura Esquerda
        add_quad(pontoUV(p00,p10,p11,p01, u0-esp, v0-ov), pontoUV(p00,p10,p11,p01, u0, v0-ov),
                 pontoUV(p00,p10,p11,p01, u0, v1+ov), pontoUV(p00,p10,p11,p01, u0-esp, v1+ov), C_MOLDURA, normal, off_frame);
        // Moldura Direita
        add_quad(pontoUV(p00,p10,p11,p01, u1, v0-ov), pontoUV(p00,p10,p11,p01, u1+esp, v0-ov),
                 pontoUV(p00,p10,p11,p01, u1+esp, v1+ov), pontoUV(p00,p10,p11,p01, u1, v1+ov), C_MOLDURA, normal, off_frame);

        // Vidro
        add_quad(pontoUV(p00,p10,p11,p01, u0-gap, v0-gap), pontoUV(p00,p10,p11,p01, u1+gap, v0-gap),
                 pontoUV(p00,p10,p11,p01, u1+gap, v1+gap), pontoUV(p00,p10,p11,p01, u0-gap, v1+gap), cor_vidro, normal, off_glass);

        // Mullion Vertical
        float mu = (u0 + u1) * 0.5f;
        float m_u = (u1 - u0) * 0.030f;
        add_quad(pontoUV(p00,p10,p11,p01, mu-m_u, v0+gap*0.5f), pontoUV(p00,p10,p11,p01, mu+m_u, v0+gap*0.5f),
                 pontoUV(p00,p10,p11,p01, mu+m_u, v1-gap*0.5f), pontoUV(p00,p10,p11,p01, mu-m_u, v1-gap*0.5f), C_MOLDURA, normal, off_mullion);

        // Mullion Horizontal
        float mv = (v0 + v1) * 0.5f;
        float m_v = (v1 - v0) * 0.030f;
        add_quad(pontoUV(p00,p10,p11,p01, u0+gap*0.5f, mv-m_v), pontoUV(p00,p10,p11,p01, u1-gap*0.5f, mv-m_v),
                 pontoUV(p00,p10,p11,p01, u1-gap*0.5f, mv+m_v), pontoUV(p00,p10,p11,p01, u0+gap*0.5f, mv+m_v), C_MOLDURA, normal, off_mullion);
    };

    auto add_porta = [&](glm::vec3 p00, glm::vec3 p10, glm::vec3 p11, glm::vec3 p01, 
                         float u0, float u1, float v0, float v1, glm::vec3 cor_porta, glm::vec3 normal) {
        float esp = 0.022f;
        float ov = esp * 0.5f;
        float gap = esp * 0.35f;
        float off_frame = 0.045f;
        float off_painel = 0.030f;
        float off_detail = 0.055f;

        // Moldura Topo
        add_quad(pontoUV(p00,p10,p11,p01, u0-esp, v1), pontoUV(p00,p10,p11,p01, u1+esp, v1),
                 pontoUV(p00,p10,p11,p01, u1+esp, v1+esp), pontoUV(p00,p10,p11,p01, u0-esp, v1+esp), C_MOLDURA, normal, off_frame);
        // Moldura Esquerda
        add_quad(pontoUV(p00,p10,p11,p01, u0-esp, v0), pontoUV(p00,p10,p11,p01, u0, v0),
                 pontoUV(p00,p10,p11,p01, u0, v1+ov), pontoUV(p00,p10,p11,p01, u0-esp, v1+ov), C_MOLDURA, normal, off_frame);
        // Moldura Direita
        add_quad(pontoUV(p00,p10,p11,p01, u1, v0), pontoUV(p00,p10,p11,p01, u1+esp, v0),
                 pontoUV(p00,p10,p11,p01, u1+esp, v1+ov), pontoUV(p00,p10,p11,p01, u1, v1+ov), C_MOLDURA, normal, off_frame);

        // Painel
        add_quad(pontoUV(p00,p10,p11,p01, u0-gap, v0-0.01f), pontoUV(p00,p10,p11,p01, u1+gap, v0-0.01f),
                 pontoUV(p00,p10,p11,p01, u1+gap, v1+gap), pontoUV(p00,p10,p11,p01, u0-gap, v1+gap), cor_porta, normal, off_painel);

        // Rebaixo
        glm::vec3 cor_escura = cor_porta * 0.55f;
        float du = (u1-u0) * 0.18f;
        float dv = (v1-v0) * 0.06f;
        float deslocamento = (u1-u0) * 0.04f;
        add_quad(pontoUV(p00,p10,p11,p01, u0+du+deslocamento, v0+dv), pontoUV(p00,p10,p11,p01, u1-du+deslocamento, v0+dv),
                 pontoUV(p00,p10,p11,p01, u1-du+deslocamento, v1-dv), pontoUV(p00,p10,p11,p01, u0+du+deslocamento, v1-dv), cor_escura, normal, off_detail);

        // Puxador
        float pr = (u1-u0) * 0.055f;
        float pu = u1 - (u1-u0) * 0.20f;
        float pv = (v0+v1) * 0.48f;
        add_quad(pontoUV(p00,p10,p11,p01, pu-pr, pv-pr), pontoUV(p00,p10,p11,p01, pu+pr, pv-pr),
                 pontoUV(p00,p10,p11,p01, pu+pr, pv+pr), pontoUV(p00,p10,p11,p01, pu-pr, pv+pr), glm::vec3(0.85f, 0.65f, 0.15f), normal, off_detail + 0.015f);
    };

    // JANELA ESQUERDA
    add_janela({-2.0f, -2.0f, -5.0f}, {-4.0f, -4.0f, -20.0f}, {-4.0f, 4.0f, -20.0f}, {-2.0f, 2.0f, -5.0f},
               0.12f, 0.36f, 0.40f, 0.75f, C_VIDRO_ESQ, N_ESQ);

    // JANELA DIREITA
    add_janela({2.0f, -2.0f, -10.0f}, {2.0f, -2.0f, -5.0f}, {2.0f, 2.0f, -5.0f}, {2.0f, 2.0f, -10.0f},
               0.474f, 0.784f, 0.40f, 0.75f, C_VIDRO_DIR, N_DIR);

    // PORTA
    add_porta({-4.0f, -4.0f, -20.0f}, {2.0f, -2.0f, -10.0f}, {2.0f, 2.0f, -10.0f}, {-4.0f, 4.0f, -20.0f},
              0.58f, 0.76f, 0.00f, 0.72f, C_PORTA, N_FUND);

    Mesh mesh;
    glGenVertexArrays(1, &mesh.VAO);
    glGenBuffers(1, &mesh.VBO);
    glGenBuffers(1, &mesh.EBO);

    glBindVertexArray(mesh.VAO);
    glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(6 * sizeof(float)));
    glEnableVertexAttribArray(2);

    glBindVertexArray(0);
    mesh.indexCount = indices.size();
    return mesh;
}

Mesh createUnitSphere(int sectors, int stacks) {
    std::vector<float> vertices;
    std::vector<unsigned int> indices;

    for (int i = 0; i <= stacks; i++) {
        float V = (float)i / stacks;
        float phi = V * glm::pi<float>();

        for (int j = 0; j <= sectors; j++) {
            float U = (float)j / sectors;
            float theta = U * 2.0f * glm::pi<float>();

            float x = cos(theta) * sin(phi);
            float y = cos(phi);
            float z = sin(theta) * sin(phi);

            // Cor branca (1,1,1) para ser multiplicada pelo objectColor
            vertices.insert(vertices.end(), {x, y, z, 1.0f, 1.0f, 1.0f, x, y, z});
        }
    }

    for (int i = 0; i < stacks; i++) {
        for (int j = 0; j < sectors; j++) {
            unsigned int p1 = i * (sectors + 1) + j;
            unsigned int p2 = p1 + sectors + 1;
            indices.insert(indices.end(), {p1, p2, p1 + 1, p1 + 1, p2, p2 + 1});
        }
    }

    Mesh mesh;
    glGenVertexArrays(1, &mesh.VAO);
    glGenBuffers(1, &mesh.VBO);
    glGenBuffers(1, &mesh.EBO);

    glBindVertexArray(mesh.VAO);
    glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
    glBufferData(GL_ARRAY_BUFFER, vertices.size() * sizeof(float), vertices.data(), GL_STATIC_DRAW);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.EBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(float), (void*)(6 * sizeof(float)));
    glEnableVertexAttribArray(2);

    glBindVertexArray(0);
    mesh.indexCount = indices.size();
    return mesh;
}