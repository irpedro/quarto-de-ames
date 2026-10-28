# Quarto de Ames - Implementação em C++ (OpenGL)

Esta é a versão final do projeto do Quarto de Ames, implementada em **C++ moderno (C++17)**. O projeto foi originalmente prototipado em Python (para validação rápida das matrizes e física) e posteriormente portado para C++, utilizando o template fornecido em sala de aula como base de infraestrutura.

## 🎯 Visão Geral

O Quarto de Ames é uma ilusão de ótica clássica. Através da deformação geométrica de um hexaedro irregular (trapezoidal), a perspectiva cônica é compensada de tal forma que, a partir de um ponto de vista específico, o ambiente parece ser um cubo perfeito. 

O projeto conta com renderização 3D em tempo real, iluminação dinâmica, texturas procedurais projetadas e simulação física de corpos esféricos.

## 🏗️ Integração e Transição a partir do Template do Professor

O template fornecido em sala de aula foi originalmente construído para uma abordagem de **Raymarching** (renderização baseada em distância de raios, típica de shaders do Shadertoy). Como o projeto do Quarto de Ames exige o pipeline clássico de **Rasterização**, foi necessário fazer uma transição arquitetural significativa.

### 🟢 O que foi Mantido (Infraestrutura Base)
Foi aproveitado do template exatamente o que era necessário para o "chassi" da aplicação rodar no Windows sem erros de configuração:
*   **`glad.c`**: O carregador das funções da API do OpenGL.
*   **Pasta `includes/`**: As bibliotecas essenciais (GLFW para janelas, GLM para matemática vetorial e matricial).
*   **`Shader.h`**: A classe de compilação de shaders. *Nota: foi necessária uma pequena correção na concatenação do `common.incl` para evitar erros de quebra de linha no Windows (CRLF vs LF).*
*   **Estrutura do CMake**: A base do arquivo `CMakeLists.txt`, adaptada para linkar os arquivos da arquitetura modular.

### 🔴 O que foi Removido (Código Específico de Raymarching)
Como o objetivo era construir uma cena 3D poligonal, todo o código voltado para a técnica anterior foi descartado:
*   **Remoção de FBOs (Framebuffers)**: O código do professor usava múltiplos *Framebuffers* (`FBO_0` a `FBO_3`) para pós-processamento de tela cheia. Isso foi removido.
*   **Shaders de Raymarching**: Os shaders `Image.frag`, `BufferA.fs` e as funções de Distância Assinada (SDFs) foram substituídos pelos shaders de Rasterização (Vertex e Fragment).
*   **Biblioteca `stb_image`**: Descartada, pois o Quarto de Ames utiliza texturas procedurais (xadrez gerado matematicamente no shader).

### 🚀 O que foi Implementado do Zero
Sobre a infraestrutura mantida, foi contruído todo o pipeline gráfico e a lógica do projeto:
1.  **Pipeline de Rasterização**: Criação manual de VBOs, VAOs e EBOs para enviar os vértices do quarto e das esferas para a GPU.
2.  **Geometria Procedural**: Todo o cálculo matemático dos vértices do quarto trapezoidal, chão subdividido, janelas e portas.
3.  **Modelo de Iluminação de Phong**: Implementado no Fragment Shader com cálculo de normais via produto vetorial (essencial para as faces inclinadas).
4.  **Câmera Orbital e Física**: Gerenciamento de estados da câmera via mouse/WASD e toda a lógica de colisão com o chão inclinado.

## 📂 Arquitetura Modular

Seguindo as boas práticas de engenharia de software herdadas da versão Python, o código foi dividido em módulos com responsabilidades únicas:

*   `main.cpp`: Orquestrador. Inicializa janelas, gerencia o loop principal, inputs de estado e renderização.
*   `geometry.cpp / .h`: Geração procedural de vértices e índices (Quarto, Chão em Grid, Molduras, Janelas, Porta e Esfera).
*   `physics.cpp / .h`: Matemática pura de colisão (altura do chão trapezoidal, *clamping* de paredes e colisão entre esferas). Zero chamadas OpenGL.
*   `input_handler.cpp / .h`: Gerencia a Câmera Orbital (coordenadas esféricas, zoom e pan via WASD) usando *callbacks* do GLFW.
*   `Shader.h`: Classe do professor para carregamento de shaders.

## ⚙️ Técnicas Gráficas Implementadas

*   **Geometria Trapezoidal:** Vértices posicionados assimetricamente para criar a ilusão de ótica.
*   **Normais Reais:** Calculadas via Produto Vetorial (Cross Product) para superfícies inclinadas.
*   **Iluminação de Phong:** Componentes ambiente e difusa com atenuação quadrática por distância (escurece o fundo do quarto, reforçando a profundidade).
*   **Piso Quadriculado (Projective Texture Mapping):** O xadrez é gerado proceduralmente no *Fragment Shader* projetando os fragmentos em um plano virtual de Y = -2, fazendo com que o trapézio pareça perfeitamente reto.
*   **Decoração Distorcida:** Janelas e porta construídas usando interpolação bilinear em coordenadas de plano (u, v), adaptando-se à inclinação das paredes.
*   **Anti-Aliasing:** MSAA 16x ativado para suavizar as bordas.
*   **Animação Autônoma:** Interpolação Linear (Lerp) guiada por uma onda senoidal para a troca de posições das esferas.

## 🎮 Controles

| Tecla / Ação | Função |
| :--- | :--- |
| **Setas (↑ ↓ ← →)** | Move a esfera verde (controlável) |
| **Espaço** | Alterna entre Câmera Focal (ilusão) e Câmera de Revelação |
| **P** | Ativa/Desativa o modo automático (as esferas trocam de lugar) |
| **R** | Reseta a posição das esferas para o início |
| **T** | Reseta a Câmera Orbital para a visão *top-down* |
| **Mouse (Arrastar)** | (Modo Revelação) Gira a câmera ao redor do quarto |
| **Scroll do Mouse** | (Modo Revelação) Zoom in / Zoom out |
| **W A S D** | (Modo Revelação) Move o alvo da câmera pelo ambiente |
| **ESC** | Fecha a aplicação |

## 🛠️ Como Compilar (Windows)

O projeto usa CMake. Certifique-se de ter o GCC/MinGW e o CMake instalados.

1. Abra o terminal na pasta `c/`.
2. Crie a pasta de build e entre nela:
   ```bash
   mkdir build
   cd build
   ```
3. Configure o projeto:
   ```bash
   cmake -G "MinGW Makefiles" ..
   ```
4. Compile:
   ```bash
   cmake --build .
   ```
5. Execute:
   ```bash
   ./QuartoAmes.exe
   ```

*(Nota: No VS Code, basta utilizar a extensão do CMake Tools e clicar em "Build" e "Run").*