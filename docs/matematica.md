# Fundamentos Matemáticos e Algoritmos

Este documento é uma referência técnica das fórmulas e algoritmos matemáticos utilizados no projeto, independentes da linguagem de programação. Todo o código em Python e C++ baseia-se nestas derivações.

## 1. A Projeção Perspectiva e a Ilusão
A base da ilusão depende da divisão de perspectiva do pipeline gráfico:
`Tamanho_na_Tela = Tamanho_Físico / Distância (Z)`

Para que o canto esquerdo (distante) pareça idêntico ao direito (próximo), sua escala física deve ser dobrada:
*   Canto Direito: `X = 2`, `Z = -10` → Projeção = `2 / 10 = 0.2`
*   Canto Esquerdo: `X = 4`, `Z = -20` → Projeção = `4 / 20 = 0.2`

## 2. Cálculo das Normais (Produto Vetorial)
Em superfícies trapezoidais, normais fixas não funcionam. A normal de cada face é calculada usando o produto vetorial entre duas arestas do triângulo:

```cpp
glm::vec3 v1 = p2 - p1;
glm::vec3 v2 = p3 - p1;
glm::vec3 normal = glm::normalize(glm::cross(v1, v2));
```

## 3. Iluminação de Phong com Atenuação
A iluminação calcula a incidência da luz baseada no ângulo entre a normal e a direção da luz, com decaimento pela distância:

*   **Luz Ambiente:** `ambient = 0.5 * cor_luz`
*   **Luz Difusa:** `diffuse = max(dot(normal, direcao_luz), 0.0) * cor_luz * atenuacao`
*   **Atenuação:** `atenuacao = 1.0 / (1.0 + 0.05 * distancia + 0.01 * (distancia * distancia))`

## 4. Física do Chão Inclinado (A Montanha)
O chão é dividido em dois planos. A função retorna a altura `Y` exata para qualquer coordenada `(X, Z)`:
*   **Metade Direita (Plana):** `Y = -2.0`
*   **Metade Esquerda (Rampa):** `Y = (10.0 * X + 8.0 * Z - 80.0) / 70.0`
*   **Amostragem:** A altura da esfera testa 5 pontos sob o seu raio (centro, frente, trás, esquerda, direita) e usa a altura máxima para não afundar.

## 5. Colisão com Paredes Diagonais
As paredes são delimitadas por equações de reta.
*   **Parede do Fundo:** A reta é `Z = (5.0 / 3.0) * X - 13.333`. A esfera é impedida de cruzar esse valor.
*   **Parede Esquerda:** A reta varia com Z, e a colisão aplica uma margem de segurança baseada no raio da esfera.

## 6. Piso Quadriculado (Projective Texture Mapping)
Para evitar a distorção do xadrez no trapézio, o padrão é projetado em um plano virtual (Y = -2). Para cada fragmento do chão, calcula-se o raio da câmera original `(0,0,0)` até ele, e a interseção no plano:

```glsl
vec3 rayDir = FragPos - refPos;
float t = (-2.0 - refPos.y) / rayDir.y;
vec3 flatPos = refPos + t * rayDir;

float checker = mod(floor(flatPos.x * scale) + floor(flatPos.z * scale), 2.0);
```

## 7. Coordenadas de Plano para Janelas e Portas (Interpolação Bilinear)
Para que janelas e portas sigam a inclinação da parede, suas posições são calculadas em coordenadas `(u, v)` e interpoladas entre os quatro cantos da parede (`P00`, `P10`, `P11`, `P01`):

```glsl
vec3 b = P00 + (P10 - P00) * u;
vec3 t = P01 + (P11 - P01) * u;
vec3 pontoFinal = b + (t - b) * v;
```

## 8. Animação (Lerp + Onda Senoidal)
A troca de posição das esferas usa uma onda senoidal para criar um `fator` que varia suavemente entre 0 e 1, e então interpola a posição (Lerp):

```cpp
float fator = (sin(tempo * frequencia * 2.0 * PI) + 1.0) / 2.0;
float posicaoAtual = posicaoInicio + (posicaoFim - posicaoInicio) * fator;
```

## 9. Câmera Orbital (Coordenadas Esféricas)
A câmera de revelação calcula sua posição cartesiana baseada em três ângulos em relação a um ponto alvo:

```cpp
x = alvo.x + raio * sin(phi) * sin(theta);
y = alvo.y + raio * cos(phi);
z = alvo.z + raio * sin(phi) * cos(theta);
```
A sensibilidade do mouse é adaptativa: quanto menor o `raio` (zoom in), menor a sensibilidade para permitir giros precisos.