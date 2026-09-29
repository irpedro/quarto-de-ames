# Quarto de Ames — Python → C

Implementação interativa da ilusão de ótica do Quarto de Ames.

## 📁 Estrutura

- [`python/`](python/) — Protótipo em Python (PyOpenGL + NumPy). **Completo e funcional.**
- [`c/`](c/) — Implementação final em C (OpenGL puro). *Em desenvolvimento.*
- [`docs/`](docs/) — Documentação técnica e matemática.

## 🎯 Sobre o projeto

O Quarto de Ames é uma ilusão de ótica onde um ambiente trapezoidal
aparenta ser cúbico de um ponto de vista único. Aqui, a ilusão é
reproduzida em tempo real, com:

- Câmera focal + câmera de revelação orbital
- Iluminação de Phong com normais calculadas via cross product
- Piso quadriculado via projective texture mapping
- Janelas e porta distorcidas (projeção em coordenadas de plano)
- Duas esferas com troca de posições animada

## 📖 Documentação

- [Visão completa do projeto](docs/README_completo.md)
- [Fundamentos matemáticos](docs/matematica.md)

## 🛠️ Stack

**Python:** PyOpenGL, GLFW, NumPy
**C:** OpenGL 3.3 Core, [template do professor]