# Quarto de Ames — Python & C++

Implementação interativa da ilusão de ótica do Quarto de Ames, desenvolvida em duas linguagens para explorar diferentes aspectos do pipeline gráfico e da engenharia de software.

## 📁 Estrutura do Repositório

- **[`python/`](python/)** — Protótipo completo em Python (PyOpenGL + NumPy). **Completo e funcional.** Focado na validação rápida da matemática e da física.
- **[`c/`](c/)** — Implementação final em C++ (OpenGL 4.2 Core, GLM, GLFW). **Completo e funcional.** Baseado no template fornecido em sala de aula, com pipeline de rasterização construído do zero.
- **[`docs/`](docs/)** — Documentação técnica aprofundada, incluindo fundamentos matemáticos e visão geral do projeto.

## 🎯 Sobre o Projeto

O Quarto de Ames é uma ilusão de ótica onde um ambiente trapezoidal aparenta ser cúbico de um ponto de vista único. O projeto reproduz essa ilusão em tempo real, com os seguintes recursos:

*   Câmera focal (ilusão) e câmera de revelação orbital (mouse + WASD).
*   Iluminação de Phong com normais calculadas via produto vetorial (*cross product*).
*   Piso quadriculado via *Projective Texture Mapping* (xadrez procedural).
*   Janelas e porta distorcidas (projeção em coordenadas de plano).
*   Duas esferas com troca de posições animada (*Lerp* + onda senoidal).
*   Física de colisão com o chão inclinado e paredes diagonais.

## 📚 Documentação

*   [Visão Geral do Projeto](docs/visao_geral.md) — Arquitetura, decisões de design e integração com o template do professor.
*   [Fundamentos Matemáticos](docs/matematica.md) — Derivação das coordenadas, normais, iluminação, mapeamento de textura e física.
*   [README da Versão Python](python/README.md) — Detalhes específicos da implementação em Python.
*   [README da Versão C++](c/README.md) — Detalhes específicos da implementação em C++.

## 🛠️ Stack Tecnológica

**Python:**
*   PyOpenGL, GLFW, NumPy

**C++:**
*   OpenGL 4.2 Core (GLAD, GLFW)
*   GLM (matemática vetorial e matricial)
*   CMake (build system)

## 🚀 Como Executar

### Versão Python

1.  Navegue até a pasta `python/`.
2.  Crie e ative um ambiente virtual (`python -m venv venv`).
3.  Instale as dependências: `pip install -r requirements.txt`.
4.  Execute: `python main.py`.

### Versão C++

1.  Navegue até a pasta `c/`.
2.  Crie a pasta de build: `mkdir build && cd build`.
3.  Configure com CMake: `cmake -G "MinGW Makefiles" ..` (no Windows com MinGW).
4.  Compile: `cmake --build .`.
5.  Execute o `QuartoAmes.exe`.