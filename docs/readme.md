# Projeto Interativo: Quarto de Ames em Computação Gráfica (OpenGL)

**Disciplina:** Fundamentos de Computação Gráfica  
**Professor(es):** [Nome dos Professores]  
**Integrantes:** Pedro Gabriel Ruiz  
**Data:** 2026  

## 🎯 Visão Geral do Projeto
O Quarto de Ames é uma ilusão de ótica clássica projetada para distorcer a percepção de profundidade e escala. Quando visto de um ponto de observação específico (o "buraco da fechadura"), o ambiente aparenta ser uma sala cúbica perfeitamente normal. No entanto, a sua geometria real é um hexaedro irregular e trapezoidal. 

Este projeto é uma simulação interativa construída em **Python 3.11**, utilizando **PyOpenGL** (pipeline moderno via Core Profile), **GLFW** (para criação de janelas e captura de *inputs*) e **NumPy** (para operações matriciais vetoriais). O usuário pode visualizar a ilusão, transitar para uma câmera de revelação e controlar manualamente uma esfera no cenário.


## 📐 1. A Matemática da Ilusão (Geometria Base)

Para que a ilusão funcione, a deformação física do modelo 3D compensa perfeitamente a redução de tamanho causada pela perspectiva cônica. A fórmula central da ilusão é a proporção entre tamanho e distância: $Tamanho_{Tela} = Tamanho_{Físico} / Distância (Z)$.

*   **Parede Direita (Referência):** Posicionada em $Z = -10$, com tamanho físico de $X = 2$ e $Y = \pm 2$.
*   **Parede Esquerda (Distorcida):** Empurrada para $Z = -20$. Para não parecer minúscula, sua escala foi multiplicada por dois: $X = -4$ e $Y = \pm 4$. 

Matematicamente, a projeção na tela se iguala:
*   Canto Direito: $2 / 10 = 0.2$
*   Canto Esquerdo: $4 / 20 = 0.2$

> `[INSERIR IMAGEM: Print da câmera focal mostrando o cubo perfeito]`  
> *Figura 1: Visão da câmera principal (A Ilusão).*

> `[INSERIR IMAGEM: Print da câmera de revelação vista de cima]`  
> *Figura 2: Visão da câmera de revelação mostrando a distorção trapezoidal real.*

## 👁️ 2. Pipeline Gráfico e Oclusão (Backface Culling)

Na visão de revelação (isométrica), o teto bloqueava a visão do interior. Remover o teto do código resultaria em erros de memória.
*   **Solução Técnica:** Implementamos o **Backface Culling** (`glEnable(GL_CULL_FACE)`). 
*   **Winding Order:** Para o *culling* funcionar sem ocultar o chão e o fundo acidentalmente, reorganizamos os `indices` da geometria para garantir que todas as faces fossem construídas no sentido **Anti-Horário** (Counter-Clockwise) a partir do interior do quarto.

## 💡 3. Iluminação e a Percepção de Profundidade

O uso de cores sólidas (*Flat Shading*) anulava o volume 3D. Desenvolvemos o **Modelo de Iluminação de Phong** nos shaders para restaurar as pistas visuais de profundidade.

*   **Normais em Superfícies Inclinadas:** Como o quarto é trapezoidal, normais fixas não funcionam. Usamos o **Produto Vetorial** (*Cross Product*) entre as arestas dos triângulos para calcular a normal exata perpendicular à inclinação da parede.
*   **Atenuação Quadrática:** Para forçar o cérebro a ler a profundidade extrema do fundo esquerdo, aplicamos um decaimento de luz por distância: $Atenuação = 1.0 / (1.0 + 0.05d + 0.01d^2)$.

## ⚽ 4. Física, Colisão e o "Problema da Montanha"

A implementação da esfera expôs os limites topológicos do modelo.

1.  **Colisão em Paredes Diagonais:** A parede do fundo não é reta. Deduzimos a equação linear exata da parede ($Z = 5/3X - 13.333$) e a aplicamos no sistema de física para impedir que a esfera *clipasse* a geometria.
2.  **Topologia Não-Coplanar ("A Montanha"):** Os quatro vértices do chão têm alturas distintas ($Y=-2$ e $Y=-4$), forçando o OpenGL a dobrar o chão em dois triângulos. A dobra original criava um "vale" no centro, fazendo a esfera afundar.
3.  **Solução de Level Design:** Invertemos a diagonal nos `indices` (do canto Frente-Esquerdo para o Fundo-Direito). Isso separou o chão perfeitamente: a metade direita virou um plano 100% reto, e a metade esquerda uma rampa lisa e contínua. A função `calcular_y_esfera` amostra 5 pontos sob o raio da bola para garantir que ela role exatamente sobre o relevo.

> `[INSERIR IMAGEM: Desenho ou print demonstrando a diagonal do chão invertida]`  
> *Figura 3: Correção topológica do chão para eliminar artefatos de colisão.*

## ⚖️ 5. Referência Visual de Escala, Colisão e Animação

A ilusão do Quarto de Ames depende de contraste. Sem um ponto de referência estático, uma única esfera encolhendo na tela pode ser interpretada como um simples redimensionamento de objeto. Para ancorar a percepção, adicionamos uma **esfera gêmea estática** e um sistema de colisão dinâmico.

### 5.1. A Esfera Gêmea (Régua Visual)

Uma segunda esfera foi posicionada no canto fundo-esquerdo e permanece **estática**. A sua sacada matemática é que ela é fisicamente muito maior que a esfera controlável, mas está tão distante da câmera que parece do mesmo tamanho na tela:

| Esfera | Raio físico | Posição Z | Tamanho aparente na tela |
|--------|-------------|-----------|--------------------------|
| Verde (controlável) | 0.35 | -5.5 | 0.35 / 5.5 ≈ 0.064 |
| Laranja (referência) | 0.70 | -13.0 | 0.70 / 13.0 ≈ 0.054 |

Quando o usuário move a esfera verde para o fundo, ela parece encolher ao lado da laranja que permanece gigante. **A comparação entre dois objetos idênticos (mesmo que pareçam de tamanhos diferentes) força o cérebro a reconsiderar a profundidade.**

> `[INSERIR IMAGEM: Print mostrando as duas esferas na tela com tamanhos aparentemente iguais]`  
> *Figura 5: Esfera verde (controlável) e esfera laranja (referência estática) no início do programa.*

### 5.2. Colisão entre Esferas (Plano XZ)

Implementamos uma colisão circular em 2D no plano XZ. Se a distância entre os centros for menor que a soma dos raios, a esfera verde é empurrada ao longo do vetor de separação:

$$
\Delta = (R_{verde} + R_{laranja}) - \|P_{verde} - P_{laranja}\|
$$

$$
P_{verde} \leftarrow P_{verde} + \Delta \cdot \frac{P_{verde} - P_{laranja}}{\|P_{verde} - P_{laranja}\|}
$$

Após o empurrão, a função `clamp_esfera` é reaplicada para garantir que a esfera verde não seja empurrada para dentro de uma parede.

### 5.3. Modos de Animação: Manual e Automático

A esfera verde possui dois modos de comportamento, alternados pela tecla **'A'** (com detecção de borda para evitar alternâncias múltiplas em um único pressionamento):

- **Modo Manual (padrão):** Movimentação pelas setas do teclado, com velocidade controlada por `delta_time` para independência da taxa de quadros.
- **Modo Automático:** A esfera verde percorre uma trajetória pré-validada entre o canto frontal-direito (`[1.5, -5.5]`) e o fundo-esquerdo (`[-1.5, -11.5]`) via **Interpolação Linear (Lerp) guiada por uma onda senoidal**:

$$
fator = \frac{\sin(t \cdot f \cdot 2\pi) + 1}{2}
$$

$$
P(t) = P_{início} + (P_{fim} - P_{início}) \cdot fator
$$

Isso satisfaz o requisito de **"Animação com implementação conduzida em aula"**, usando tempo contínuo e movimento autônomo, sem sacrificar a interatividade manual.

> `[INSERIR IMAGEM: Print do modo automático em execução]`  
> *Figura 6: Esfera verde em modo automático, animando entre os dois cantos do quarto.*

## 🏗️ 6. Arquitetura Modular e Otimizações

Conforme o projeto cresceu (esferas, colisão, animação), o `main.py` original tornou-se monolítico e difícil de manter. Refatorei o código em **módulos especializados**, cada um com uma responsabilidade única. Essa separação é uma prática de engenharia de software que também prepara o terreno para features avançadas (Shadow Mapping, texturas).

### 6.1. Estrutura de Arquivos

| Arquivo | Responsabilidade |
|---------|------------------|
| `main.py` | Orquestrador. Inicializa GLFW, cria shaders/VAOs, e contém o loop principal. |
| `camera.py` | Construção das matrizes de Projeção (Perspectiva) e Visão (LookAt). |
| `geometry.py` | Geração procedural dos vértices e índices do quarto e das esferas. |
| `shaders.py` | Código-fonte GLSL e compilação dos shaders. Cache de uniform locations. |
| `physics.py` | Matemática pura: altura do chão, colisão, animação via Lerp/Seno. Zero chamadas OpenGL. |
| `renderer.py` | Funções de desenho reutilizáveis (`desenhar_quarto`, `desenhar_esfera`). |
| `input_handler.py` | *(Placeholder)* Será usado para centralizar input de teclado e mouse (câmera orbital). |

### 6.2. Otimização: Cache de Uniform Locations

**Problema original:** A cada frame (~60 vezes por segundo), o código chamava `glGetUniformLocation(shader_program, "projection")` para buscar o mesmo endereço de memória. Essa operação é uma busca em string na GPU — lenta e desnecessária, pois a localização **nunca muda** após a compilação do shader.

**Solução:** Foi criada a função `shaders.get_uniform_locations()` que busca todos os endereços **uma única vez** na inicialização e os retorna num dicionário. O loop principal agora apenas consulta o dicionário:

    uniforms = shaders.get_uniform_locations(shader_program)  # 1x na inicialização
    # ...
    glUniformMatrix4fv(uniforms['projection'], 1, GL_FALSE, proj_matrix.T)  # rápido

**Impacto:** Ganho estimado de ~5% de FPS no estado atual, mas **essencial** para o Shadow Mapping (que renderiza a cena 2 vezes por frame — o ganho vira ~15%).

### 6.3. Otimização: VAO Único para Esferas + objectColor

**Problema original:** A cor estava "assada" nos vértices da esfera, exigindo criar **um VAO separado para cada esfera** (verde e laranja) — duplicando o uso de VRAM.

**Solução:** Foi criada uma única esfera neutra (`get_unit_sphere`) de raio 1.0 e cor branca. A cor real e o tamanho são passados via uniform e matriz de modelo:

- **Cor:** Uniform `objectColor` no Fragment Shader.
- **Tamanho:** Os três primeiros elementos da diagonal da matriz de modelo (`model[0,0] = raio`, etc.).

No Fragment Shader, a linha final ficou:

    FragColor = vec4((ambient + diffuse) * vertexColor * objectColor, 1.0);

O truque do `vertexColor * objectColor` permite que:

- O **quarto** funcione igual (vertexColor traz as cores, objectColor = branco).
- As **esferas** funcionem com uma cor única (vertexColor = branco, objectColor = cor real).

**Impacto:** Metade do uso de VRAM para as esferas. Adicionar uma terceira esfera agora custa apenas 3 linhas no loop.

### 6.4. Otimização: Funções de Desenho Reutilizáveis

**Problema original:** Toda a lógica de desenho estava *inline* no loop principal, misturando matemática de matriz com chamadas OpenGL.

**Solução:** Extraí as funções `renderer.desenhar_quarto()` e `renderer.desenhar_esfera()` para um módulo próprio. O loop principal ficou 15 linhas mais enxuto e, mais importante, **as funções podem ser reutilizadas pelo Shadow Mapping** (que renderiza a mesma cena do ponto de vista da luz).

### 6.5. Separação entre Física e Renderização

Uma decisão arquitetural importante: `physics.py` **não importa OpenGL**. Ele apenas recebe coordenadas e retorna coordenadas. Isso significa que:

- A lógica de colisão pode ser testada isoladamente (unit tests sem GPU).
- Trocar a engine gráfica não exigiria reescrever a física.
- O código é mais fácil de entender (uma coisa = uma responsabilidade).

> `[INSERIR IMAGEM: Diagrama de blocos mostrando os módulos e suas dependências]`  
> *Figura 7: Arquitetura modular do projeto. `physics.py` é independente de OpenGL.*

## 🧪 7. Experimentos e Decisões de Design

### 7.1. Parede Frontal com Fechadura — Avaliada e Descartada

**Motivação:** Em um Quarto de Ames físico (museus de ilusão), o observador olha através de um pequeno orifício (peephole) na parede frontal. Isso força um ponto de vista único e elimina pistas de profundidade como visão binocular e movimento da cabeça. A hipótese era que reproduzir essa restrição no ambiente virtual reforçaria a ilusão.

**Implementação tentada:** Adicionamos uma geometria de parede frontal (em `Z = -4.95`) composta por quatro retângulos que formavam uma moldura ao redor de um buraco retangular central. A câmera focal ficava posicionada atrás desse buraco, simulando a condição de museu.

**Resultado observado:** A moldura quebrou a sensação de imersão. As paredes laterais (vermelha e azul) eram cortadas pela moldura cinza, e o cérebro passou a interpretar a cena como uma **maquete vista de fora** em vez de um **ambiente no qual se está dentro**.

> `[INSERIR IMAGEM: Print da câmera focal com a parede de fechadura ativa]`  
> *Figura 7a: Tentativa com fechadura — a moldura cinza corta as paredes laterais e destrói a sensação de estar dentro do quarto.*

> `[INSERIR IMAGEM: Print da câmera focal sem a fechadura]`  
> *Figura 7b: Resultado final sem fechadura — as paredes se estendem pelas bordas da tela e o cérebro interpreta a cena como um ambiente contínuo.*

**Análise técnica:** Em ambientes virtuais monoculares (como este projeto), a imersão depende de **pistas visuais contínuas** — paredes que se estendem além das bordas da tela, perspectiva correta, iluminação coerente. A restrição física do peephole funciona em museus porque o observador tem um olho real e um corpo que ancora a percepção. No virtual, a moldura compete com as pistas de continuidade e vence — o cérebro prioriza "moldura cortando parede" como sinal de "objeto exposto" em vez de "janela de observação".

**Decisão:** A parede frontal com fechadura foi **removida do projeto final**. A geometria da parede permanece implementável, mas não é renderizada.

**Alternativas adotadas para reforçar a sensação de "estar dentro de um quarto":**
1. **Piso quadriculado** (ver Seção 8) — pistas de escala e profundidade.
2. **Rodapé e sanca** — faixas decorativas que marcam os encontros entre paredes, chão e teto.
3. **Lâmpada 3D** — objeto físico pendurado no teto, ancorando o ponto de luz na cena.

## 🏁 8. Piso Quadriculado via Projective Texture Mapping

Após a geometria e a iluminação estarem sólidas, o próximo desafio visual foi o **piso quadriculado** — elemento icônico do Quarto de Ames e essencial para ancorar a percepção de escala. Sem ele, o chão cinza uniforme parece plano e a ilusão perde força.

### 8.1. O Problema: Xadrez em Superfície Deformada

O chão do Quarto de Ames **não é plano**. Ele é um trapézio onde o canto fundo-esquerdo desce (`Y = -4`) enquanto os outros três permanecem em `Y = -2`. Se aplicássemos o xadrez usando coordenadas físicas de mundo (`FragPos.x`, `FragPos.z`), o padrão ficaria **esticado** justamente na região onde a geometria é maior. O cérebro detectaria a distorção e a ilusão quebraria.

### 8.2. A Solução: Projeção em Plano Virtual

A solução é uma versão simplificada de **Projective Texture Mapping** calculada inteiramente no Fragment Shader, sem precisar carregar texturas. Para cada fragmento do chão, calculamos o raio que sai da câmera até ele e encontramos onde esse raio intersecta um plano virtual em `Y = -2`:

    vec3 rayDir = FragPos - viewPos;
    float t = (-2.0 - viewPos.y) / rayDir.y;
    vec3 flatPos = viewPos + t * rayDir;

    float checker = mod(floor(flatPos.x * scale) + floor(flatPos.z * scale), 2.0);

As coordenadas `flatPos` (o ponto onde o raio bate no plano virtual) são usadas para desenhar o xadrez. O resultado é que, **do ponto de vista da câmera focal**, o piso parece perfeitamente reto e quadriculado — exatamente como um cômodo real.

### 8.3. Aliasing no Fundo (Fade por Distância)

No fundo do quarto, os quadradinhos do xadrez ficam tão finos em relação ao tamanho do pixel que a GPU não consegue resolvê-los — gerando o clássico efeito **moiré/aliasing**. A solução foi um `smoothstep` que desvanece o xadrez para uma cor sólida conforme a distância à câmera aumenta:

    float distCamera = length(viewPos - FragPos);
    float fade = smoothstep(15.0, 24.0, distCamera);
    baseColor = mix(xadrez, corSolida, fade);

Isso faz a transição do xadrez para cor sólida acontecer de forma suave e imperceptível.

### 8.4. Winding Order do Grid (Chão Invisível)

Na primeira tentativa de gerar o chão como grid subdividido (30x30 células), o chão **desapareceu completamente**. O motivo: com `GL_CULL_FACE` ativado, o OpenGL só desenha triângulos com winding **anti-horário (CCW)** vistos de dentro do quarto. Os índices originais `[a, b, c, b, d, c]` produziam triângulos com o winding invertido, sendo descartados antes de chegar ao shader.

**Correção:** invertemos a ordem para `[a, c, b, b, c, d]`, que produz CCW correto quando visto de cima. O chão reapareceu instantaneamente.

### 8.5. Costura entre Chão e Paredes (MSAA)

Mesmo com o chão subdividido e o xadrez correto, persistia uma **linha fina** na emenda entre o chão e as paredes vermelha/azul. Isso **não era aliasing tradicional** — era um gap de rasterização: o chão e as paredes são VAOs separados, e mesmo que compartilhem vértices idênticos, o rasterizador pode deixar 1 pixel sem cobertura de nenhum dos dois triângulos.

**Tentativas frustradas:**
- **Overlap geométrico de 0.02** (descer os vértices das paredes 2cm abaixo do chão): resolveu parcialmente, mas ficou um resíduo.
- **Overlap geométrico de 0.05** com inversão de ordem (chão → paredes): resolveu a emenda, mas criou o efeito de "chão voando" na borda frontal, onde a parede ficava visivelmente saliente para baixo. **Descartado.**

**Solução final:** MSAA (Multisample Anti-Aliasing) com 16 sub-amostras por pixel. Isso suaviza a borda em vez de tentar cobri-la geometricamente:

    glfw.window_hint(glfw.SAMPLES, 16)
    # após make_context_current:
    glEnable(GL_MULTISAMPLE)

O MSAA 16x resolveu a emenda **sem** os artefatos do overlap geométrico.

### 8.6. Esferas sem Xadrez no Topo

Como o shader decide se aplica xadrez via `norm.y > 0.5` (chão), as esferas também recebiam xadrez no topo — pois o topo de qualquer esfera tem normal apontando para cima. Para resolver, adicionamos o uniform `enableChecker`:

- **Quarto (`enableChecker = 1`):** chão ganha xadrez.
- **Esferas (`enableChecker = 0`):** superfície plana colorida, sem padrão.

    if (enableChecker == 1 && norm.y > 0.5) {
        // xadrez procedural
    } else {
        // cor do vértice * objectColor
    }

> `[INSERIR IMAGEM: Print do piso quadriculado final com MSAA ativo]`  
> *Figura 8: Chão quadriculado com projective mapping e MSAA 16x.*

### 8.7. Referência Fixa para o Xadrez (Ancoragem no Espaço)

Na primeira implementação, o raio era calculado a partir da **câmera atual** (`FragPos - viewPos`). Isso causava um problema sutil: quando o usuário trocava para a câmera de revelação, o xadrez era recalculado do ponto de vista de cima, e o padrão "escorregava" pela superfície dependendo da posição da câmera.

**Correção:** Ancoramos o raio em um ponto de referência **fixo** — a posição da câmera focal original `(0, 0, 0)`:

    vec3 refPos = vec3(0.0, 0.0, 0.0);
    vec3 rayDir = FragPos - refPos;
    float t = (-2.0 - refPos.y) / rayDir.y;
    vec3 flatPos = refPos + t * rayDir;

O resultado é que o xadrez fica **pintado** no piso trapezoidal, independentemente de onde a câmera está. Isso é fiel a um Quarto de Ames real: o padrão é fisicamente pintado no chão distorcido para que, do ponto de vista específico, pareça regular. Do ponto de vista da câmera de revelação, o padrão **revela** a distorção, reforçando o impacto pedagógico do projeto.

> `[INSERIR IMAGEM: Print da câmera de revelação com o chão quadriculado distorcido]`  
> *Figura 8b: Xadrez ancorado em (0,0,0) — pintado no trapézio real, visível na câmera de revelação.*

## 🏛️ 9. Rodapé e Sanca com Escala Proporcional

### 9.1. Motivação

Após o piso quadriculado, o próximo refinamento visual foi adicionar **rodapé** (faixa escura onde as paredes encontram o chão) e **sanca** (faixa clara onde as paredes encontram o teto). Essas faixas arquitetônicas reforçam a sensação de "estar dentro de um cômodo com acabamento" — como discutido na Seção 7.1, a ausência de transições entre superfícies faz o cérebro interpretar a cena como "maquete flutuante" em vez de "ambiente habitável".

### 9.2. Desafio 1: Proporcionalidade da Altura na Tela

**Problema:** A altura na tela de uma faixa vertical é `altura_física / Z`. Se a faixa tem altura fixa no mundo 3D, ela aparece com **espessura diferente** ao longo da parede inclinada:

| Posição | Z | Altura aparente na tela |
|---------|---|-------------------------|
| Canto frontal | -5 | 0.15 / 5 = **0.030** |
| Canto fundo | -20 | 0.15 / 20 = **0.0075** |

Ou seja, a faixa "encolhe" 4x ao percorrer a parede. O cérebro detecta essa mudança e a ilusão do cubo perfeito se enfraquece.

**Solução:** A altura da faixa é **escalada proporcionalmente ao módulo de Z**. Cada vértice da faixa recebe uma altura diferente, calculada em tempo de geometria:

    h1 = altura_base * (abs(z1) / abs(z_ref))
    h2 = altura_base * (abs(z2) / abs(z_ref))

Onde `z_ref = 10.0` é a profundidade de referência. O resultado é que, **do ponto de vista da câmera focal**, todas as faixas têm a mesma espessura aparente — o encolhimento desaparece.

### 9.3. Desafio 2: Winding Order Espelhado

**Problema:** A função `add_faixa` gera os triângulos na ordem `[base, base+1, base+2, base+1, base+3, base+2]`. Isso produz **CCW** (visível) ou **CW** (culled) dependendo do **sentido de p1→p2** e do **sinal de delta_y**. Resultado: os rodapés apareciam nas paredes esquerda e direita, mas **não** na parede do fundo. As sancas apareciam no fundo, mas **não** nas laterais — um padrão espelhado que revelava o bug.

**Solução:** Inverter a ordem de `p1` e `p2` nas chamadas onde o winding estava errado:

    # Rodapés
    add_faixa((-2.0, -2.0,  -5.0), (-4.0, -4.0, -20.0), N_ESQ,  C_RODAPE, +1)  # OK
    add_faixa(( 2.0, -2.0, -10.0), ( 2.0, -2.0,  -5.0), N_DIR,  C_RODAPE, +1)  # OK
    add_faixa((-4.0, -4.0, -20.0), ( 2.0, -2.0, -10.0), N_FUND, C_RODAPE, +1)  # INVERTIDO

### 9.4. Desafio 3: Cores e Contraste

**Problema:** Com a cor marrom escura original (`[0.10, 0.06, 0.04]`), o rodapé se misturava com a sombra natural das paredes (causada pela atenuação da luz). O cérebro não conseguia distingui-lo do gradiente de iluminação.

**Solução:** Ajuste das cores para tons que contrastam com o gradiente natural das paredes:
- **Rodapé:** `[0.35, 0.25, 0.18]` (marrom médio)
- **Sanca:** `[0.92, 0.90, 0.85]` (branco levemente quente)

### 9.5. Implementação Final

A função `get_molduras()` gera três rodapés e três sancas (uma por parede), aplicando:
1. Offset ao longo da normal (evita Z-fighting com a parede — Seção 9.6).
2. Altura proporcional a `|Z|` (mantém espessura aparente constante).
3. Winding correto por face (garante visibilidade com `GL_CULL_FACE`).

> `[INSERIR IMAGEM: Print do rodapé e sanca em todas as três paredes]`  
> *Figura 9: Rodapé e sanca com escala proporcional — espessura uniforme em todas as paredes.*

### 9.6. Z-Fighting e Offset

**Problema:** As faixas, no plano original, são **coplanares** com as paredes. O Z-buffer não consegue decidir qual desenhar na frente — resultado: piscam ou desaparecem.

**Solução:** Deslocar cada faixa **0.01 a 0.025 unidades ao longo da normal da parede**, empurrando-a ligeiramente para dentro do quarto. Isso cria uma separação de profundidade suficiente para o Z-buffer, invisível ao olho humano.

    dx, dy, dz = nx * offset, ny * offset, nz * offset

## 🎥 10. Câmera Orbital (Arcball) no Modo Revelação

Após a ilusão estar completa, o modo de revelação ainda era limitado a uma vista top-down fixa. O usuário via a distorção, mas de um único ângulo. O próximo passo foi transformar o "revelar" em um **instrumento de exploração** — permitindo girar livremente ao redor do quarto e inspecionar a geometria trapezoidal por qualquer ângulo.

### 10.1. Arquitetura da Câmera Orbital

A câmera orbital é definida por **três variáveis** (coordenadas esféricas):

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `theta` | Rotação ao redor do eixo Y (horizontal) | 0.0 |
| `phi` | Inclinação vertical (0 = topo, π/2 = horizonte, π = embaixo) | 0.0 |
| `radius` | Distância até o alvo | 35.0 |

O ponto-alvo é o **centro geométrico do quarto** em `(-1.0, 0.0, -12.0)`. A posição da câmera no espaço 3D é calculada a partir dessas coordenadas:

    x = alvo.x + radius * sin(phi) * sin(theta)
    y = alvo.y + radius * cos(phi)
    z = alvo.z + radius * sin(phi) * cos(theta)

Os valores padrão (`theta=0, phi=0, radius=35`) reproduzem exatamente a vista top-down original da câmera de revelação — garantindo continuidade com o comportamento anterior.

### 10.2. Controles e Interação

O módulo `input_handler.py` centraliza toda a lógica de mouse, registrando três callbacks do GLFW:

| Ação | Efeito |
|------|--------|
| **Arrastar botão esquerdo** | Gira a câmera ao redor do alvo (sensibilidade adaptativa) |
| **Scroll do mouse** | Zoom (radius de 15 a 80 unidades) |
| **WASD** | Move o alvo da câmera (camera-relative) |
| **Tecla T** | Reset da orbital (ângulos, raio e offset do alvo) |

### 10.3. Espaço como Toggle (não Segurar)

**Primeira versão:** Espaço precisava ser **mantido pressionado** para permanecer no modo revelação.

**Problema:** Manter uma tecla apertada enquanto arrasta o mouse é desconfortável e limita a exploração (o usuário precisa usar uma mão para a tecla e outra para o mouse).

**Solução:** Espaço virou **toggle** (com detecção de borda). Um clique entra no modo revelação; outro clique volta ao modo focal. Isso libera ambas as mãos para a exploração orbital.

### 10.4. Ver por Baixo do Quarto

**Primeira versão:** O `phi` era limitado a `[0.05, π/2 - 0.05]`, restringindo a câmera ao hemisfério superior (topo + horizonte).

**Problema:** Não era possível ver o quarto por baixo — o que é pedagogicamente interessante, pois mostra a geometria do chão trapezoidal desde o outro lado.

**Solução:** O limite foi estendido para `[0.05, π - 0.05]`, permitindo que a câmera atravesse o horizonte e alcance o **nadir** (embaixo). Ao girar por baixo, o usuário vê:
- A superfície inferior do chão inclinado
- As paredes por trás (que ficam invisíveis devido ao Backface Culling — efeito didático)
- A estrutura "oca" do hexaedro irregular

### 10.5. Funções Implementadas (`input_handler.py`)

    inicializar_estado_orbital()         # Retorna o dicionário de estado
    resetar_orbital(estado)              # Volta para top-down
    calcular_eye_orbital(alvo, estado)   # Converte esféricas em cartesianas
    configurar_callbacks(window, estado) # Registra mouse button, cursor e scroll

O módulo segue a mesma filosofia de `physics.py`: **não importa nada além de `glfw`, `math`, `numpy`** — nenhuma chamada OpenGL de renderização. Isso mantém a separação entre **lógica de input** e **lógica de desenho**.

> `[INSERIR IMAGEM: Print da câmera orbital em ângulo diagonal]`  
> *Figura 10: Câmera orbital — o usuário gira ao redor do quarto para explorar a distorção.*

> `[INSERIR IMAGEM: Print da câmera orbital vista por baixo do quarto]`  
> *Figura 10b: Vista inferior — o chão trapezoidal e a "casca" do hexaedro irregular.*

### 10.6. Considerações Técnicas

- **Gimbal lock:** O clamp de `phi` em `[0.05, π - 0.05]` evita os polos (onde a rotação em torno de Y se torna ambígua), mas ainda permite ver praticamente todo o hemisfério.
- **Up vector:** Mantido em `(0, 0, -1)` (consistente com o top-down original). Isso faz o "norte" da tela permanecer apontando para o fundo do quarto em qualquer ângulo.
- **Ordem de transformações:** A posição orbital é calculada **antes** da chamada a `create_lookat_matrix`, que recebe `eye`, `target` e `up` já resolvidos. Isso mantém `camera.py` completamente independente da lógica orbital.

### 10.7. Sensibilidade Adaptativa do Mouse

**Problema:** A sensibilidade do arrasto era **fixa** (0.003 rad/pixel). Quando o usuário fazia zoom in (radius pequeno), a câmera girava muito rápido — 100 pixels de arrasto podiam virar 100° de rotação. Isso tornava impossível inspecionar detalhes de perto.

**Solução:** A sensibilidade agora **escala com o `radius`**:

    fator = radius / RADIUS_REFERENCIA       # ex: 15/35 ≈ 0.43
    sensibilidade = SENSIBILIDADE_BASE * fator

Quando o usuário está no zoom máximo (`radius = 15`), a sensibilidade cai para **43% do valor base** — giros finos e controlados. No zoom mínimo (`radius = 80`), sobe para 229% — giros rápidos para ver o quarto inteiro.

O `RADIUS_MIN` foi elevado de 8 para **15** — evitando o efeito de "camuflagem" que acontecia quando a câmera ficava muito próxima do ponto-alvo.

### 10.8. Pan com WASD (Movimento do Alvo)

**Motivação:** O arrasto do mouse orbital gira a câmera **ao redor** do alvo, mas não permite **explorar** o quarto caminhando por ele. Adicionamos WASD para mover o **ponto-alvo** — a câmera acompanha, orbitando em volta do novo alvo.

O deslocamento é guardado em `target_offset`, um vetor acumulado em `(0,0,0)` que é somado ao `alvo_base` antes de calcular o `eye`:

    alvo = alvo_base + target_offset
    eye = alvo + radius * (sin(phi)*sin(theta), cos(phi), sin(phi)*cos(theta))

**Direção camera-relative:** As teclas W/S/A/D movem o alvo **na direção em que a câmera está olhando**, não em direção fixa ao mundo. Isso significa que após girar 90°, W continua indo "para frente na tela":

    forward = (-sin(theta), 0, -cos(theta))
    right   = ( cos(theta), 0, -sin(theta))

Os limites do `target_offset` são `[-8, 8]` em X e `[-15, 5]` em Z — o suficiente para explorar todo o quarto sem sair dele.

O reset (tecla **T**) também zera o `target_offset`, voltando à vista top-down original.

### 10.9. Reorganização das Teclas

O modo automático das esferas estava mapeado na tecla **A**, mas isso entrou em conflito com o **A** do WASD (que move o alvo da câmera para a esquerda). A tecla foi movida para **P** (Play/Pause):

| Tecla | Ação |
|-------|------|
| **W A S D** | (Revelação) Move o alvo da câmera |
| **P** | Alterna modo automático das esferas |
| **T** | Reset da câmera orbital |
| **R** | Reset das esferas |
| **Espaço** | Alterna câmera focal/revelação |
| **Setas** | Move a esfera verde (manual) |
| **Esc** | Sair |

## 🚪 11. Janelas e Porta Distorcidas

Após a câmera orbital e o modo automático estarem funcionando, o próximo passo foi **enriquecer o ambiente** com elementos arquitetônicos que servem como **âncoras visuais de profundidade**. Sem eles, o quarto tinha apenas paredes lisas — o cérebro não tinha referências para julgar a escala da esfera em movimento.

### 11.1. Motivação

A literatura sobre o Quarto de Ames real confirma: **"as paredes (exceto aquela por onde se olha) são trapézios, assim como as janelas na sala"**. Ou seja, as janelas distorcidas não são decoração — são **parte do sistema de enganação visual**. O mesmo vale para portas, quadros e rodapés.

A pesquisa sobre design de ilusão também aponta que **"os indícios visuais para perspectiva — o escalonamento das janelas, o padrão no chão e a convergência das arestas — são todos deliberadamente distorcidos"** para compensar a geometria trapezoidal. Isso é exatamente o que implementamos: **a janela é geometricamente um trapézio, mas projeta-se como um retângulo perfeito do ponto de vista da câmera focal**.

### 11.2. Coordenadas de Plano (u, v)

Toda a decoração (janelas, porta) é definida em **coordenadas do plano da parede**, parametrizadas por:

- **u = 0** → canto frontal (perto da câmera)
- **u = 1** → canto do fundo (distante)
- **v = 0** → base da parede (chão)
- **v = 1** → topo da parede (teto)

Dado um ponto `(u, v)` e os quatro cantos do plano da parede (`P00`, `P10`, `P11`, `P01`), a posição 3D é obtida por **interpolação bilinear**:

    def ponto(u, v):
        b = P00 + (P10 - P00) * u
        t = P01 + (P11 - P01) * u
        return b + (t - b) * v

Isso garante que a decoração **siga a inclinação da parede**, ao contrário de um quad colado diretamente na geometria (que ficaria visualmente desconectado).

### 11.3. Janela: Moldura + Vidro + Cruz

Cada janela é composta por **4 quads sobrepostos**, em offsets progressivos da parede:

| Componente | Offset | Cor | Função |
|------------|--------|-----|--------|
| **Moldura** (4 faixas finas) | 0.030 | Marrom escuro | Caixilho externo |
| **Vidro** (recessado) | 0.015 | Azul escuro | Superfície interna |
| **Mullion vertical** | 0.035 | Marrom escuro | Cruz central (vertical) |
| **Mullion horizontal** | 0.035 | Marrom escuro | Cruz central (horizontal) |

A **cruz central** é o elemento mais importante para a percepção. Sem ela, o cérebro interpreta o quad como um "adesivo" colado na parede. Com ela, o cérebro reconhece **"isto é uma janela"** e passa a usá-la como referência de profundidade.

O vidro é **recessado atrás da moldura** (offset 0.015 < 0.030) — fisicamente correto para uma janela real, e cria uma sombra sutil que reforça a tridimensionalidade.

### 11.4. Winding Order por Parede

Assim como o piso e as paredes, as janelas e a porta também sofrem com o **Backface Culling**. As paredes esquerda, direita e de fundo têm normais em direções diferentes, e a mesma ordem de vértices (`p0, p1, p2, p3`) produz winding CCW em uma parede mas CW em outra.

**Solução:** inverter a ordem dos cantos do plano (`P00 ↔ P10` e `P01 ↔ P11`) nas paredes direita e do fundo. Como consequência, a parametrização `u` também é invertida — o valor `u0` antigo vira `1 - u0`, e assim por diante.

| Parede | Winding original | Ação |
|--------|-----------------|------|
| Esquerda | CCW correto | Nenhuma |
| Direita | CW (culled) | Inverter `P00 ↔ P10` e `P01 ↔ P11` |
| Fundo | CW (culled) | Inverter `P00 ↔ P10` e `P01 ↔ P11` |

### 11.5. Porta com Rebaixo e Puxador

A porta usa uma variante da função de janela, sem o mullion em cruz. Em vez disso:

- **Moldura de topo + 2 laterais** (sem base — a porta vai até o chão).
- **Painel único** de madeira, sem subdivisões.
- **Rebaixo decorativo** (madeira mais escura) na região central, criando a aparência de uma porta com almofada.
- **Puxador dourado** do lado direito do rebaixo.

O resultado é uma porta que parece **parte da arquitetura**, em vez de um quad marrom colado.

### 11.6. Compensação de Perspectiva no Rebaixo da Porta

A parede do fundo é **fortemente inclinada**, e sua projeção comprime a parte traseira (lado esquerdo da porta) e expande a parte frontal (lado direito). Como consequência, o rebaixo central da porta — mesmo geometricamente centrado em `(u, v)` — parecia **deslocado para a esquerda** do ponto de vista da câmera focal.

**Solução:** deslocar o rebaixo **para a direita em coordenadas do plano** (aumentar o `u` central), compensando a assimetria de projeção:

    deslocamento = (u1 - u0) * 0.04

Isso faz o rebaixo parecer **centralizado na tela**, mesmo não sendo geometricamente simétrico na parede.

### 11.7. Resultado Final

As duas janelas (esquerda e direita) e a porta (fundo) criam uma **grade visual de referências** que o cérebro usa para ancorar a profundidade. Quando o usuário move a esfera verde, o tamanho dela é agora comparado automaticamente contra:
1. O piso quadriculado (escala horizontal).
2. As janelas laterais (escala média, mesma altura nas duas paredes).
3. A porta no fundo (escala vertical, referência central).

Isso transforma o "encolhimento" da esfera em um **efeito dramático e imediato**, sem precisar de fantasmas ou animações.

> `[INSERIR IMAGEM: Print da câmera focal com janelas e porta]`  
> *Figura 11: Janelas e porta distorcidas — âncoras visuais que reforçam a ilusão.*

> `[INSERIR IMAGEM: Print da câmera de revelação mostrando as janelas distorcidas]`  
> *Figura 11b: As janelas são fisicamente trapézios, mas parecem retângulos da câmera focal.*

## 🚀 Conclusão e Trabalhos Futuros

O projeto atingiu com sucesso o objetivo de simular a distorção espacial do Quarto de Ames em tempo real, aliando a matemática de projeção ortográfica/perspectiva a um pipeline robusto de iluminação (Phong) e física de colisão baseada em equações lineares dinâmicas. O sistema de controle de estado comprova a viabilidade de mesclar interatividade e animação conduzida por tempo contínuo (*delta time*).

**Trabalhos Futuros propostos:**
1.  **Shadow Mapping:** Geração de sombras projetadas no chão a partir de um *framebuffer* de profundidade na posição da luz, ancorando fisicamente as esferas no cenário.
2.  **Lâmpada 3D:** Substituir o ponto de luz invisível por um modelo geométrico (uma esfera luminosa ou um lustre) pendurado no teto, ancorando visualmente a fonte de luz na cena.
3.  **HUD de Instruções:** Texto na tela com os controles e as instruções, exibido no início da execução.
4.  **Modelos Complexos:** Substituição das esferas por modelos assimétricos (como o Utah Teapot) para intensificar a percepção de escala em objetos com geometria não-simétrica.