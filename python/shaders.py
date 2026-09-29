from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

VERTEX_SHADER_SOURCE = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
layout (location = 2) in vec3 aNormal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 FragPos;
out vec3 Normal;
out vec3 vertexColor;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    FragPos = vec3(model * vec4(aPos, 1.0));
    Normal = mat3(transpose(inverse(model))) * aNormal;
    vertexColor = aColor;
}
"""

FRAGMENT_SHADER_SOURCE = """
#version 330 core
in vec3 FragPos;
in vec3 Normal;
in vec3 vertexColor;

out vec4 FragColor;

uniform vec3 lightPos;
uniform vec3 objectColor;
uniform int  enableChecker;   // 1 = chão com xadrez, 0 = superfícies normais

void main() {
    // --- Iluminação Phong ---
    float ambientStrength = 0.5;
    vec3 ambient = ambientStrength * vec3(1.0, 1.0, 1.0);

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);

    float distance = length(lightPos - FragPos);
    float attenuation = 1.0 / (1.0 + 0.05 * distance + 0.01 * (distance * distance));

    vec3 diffuse = diff * vec3(1.0, 1.0, 1.0) * attenuation;

    // --- Cor base ---
    vec3 baseColor;
    if (enableChecker == 1 && norm.y > 0.5) {
        // Projetar o fragmento em um piso virtual plano em Y = -2.
        // Isso faz o xadrez parecer pintado em um piso reto do ponto de vista
        // da câmera, escondendo a geometria trapezoidal.
        vec3 refPos = vec3(0.0, 0.0, 0.0);
        vec3 rayDir = FragPos - refPos;
        float t = (-2.0 - refPos.y) / rayDir.y;
        vec3 flatPos = refPos + t * rayDir;

        float scale = 1;
        float checker = mod(floor(flatPos.x * scale) + floor(flatPos.z * scale), 2.0);
        vec3 corEscura = vec3(0.12, 0.12, 0.12);
        vec3 corClara  = vec3(0.82, 0.82, 0.82);
        vec3 xadrez = mix(corEscura, corClara, checker);

        // Fade com a distância para suavizar aliasing no fundo
        float distCamera = length(FragPos.xz);
        float fade = smoothstep(15.0, 24.0, distCamera);
        vec3 corSolida = vec3(0.45, 0.45, 0.45);
        baseColor = mix(xadrez, corSolida, fade);
    } else {
        // PAREDES, TETO E ESFERAS
        baseColor = vertexColor * objectColor;
    }

    FragColor = vec4((ambient + diffuse) * baseColor, 1.0);
}
"""

def create_shader_program():
    return compileProgram(
        compileShader(VERTEX_SHADER_SOURCE, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER_SOURCE, GL_FRAGMENT_SHADER)
    )

def get_uniform_locations(shader_program):
    """Busca todas as localizações de uniform UMA VEZ. Retorna um dicionário."""
    return {
        'projection': glGetUniformLocation(shader_program, "projection"),
        'view':       glGetUniformLocation(shader_program, "view"),
        'model':      glGetUniformLocation(shader_program, "model"),
        'lightPos':   glGetUniformLocation(shader_program, "lightPos"),
        'objectColor': glGetUniformLocation(shader_program, "objectColor"),
        'enableChecker': glGetUniformLocation(shader_program, "enableChecker"),
    }