in vec3 FragPos;
in vec3 Normal;
in vec3 vertexColor;

out vec4 FragColor;

uniform vec3 lightPos;
uniform vec3 objectColor; // <-- NOVO
uniform int  enableChecker;

void main() {
    // Iluminação Phong
    float ambientStrength = 0.5;
    vec3 ambient = ambientStrength * vec3(1.0, 1.0, 1.0);

    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);
    float diff = max(dot(norm, lightDir), 0.0);

    float distance = length(lightPos - FragPos);
    float attenuation = 1.0 / (1.0 + 0.05 * distance + 0.01 * (distance * distance));

    vec3 diffuse = diff * vec3(1.0, 1.0, 1.0) * attenuation;

    // Cor base
    vec3 baseColor;
    if (enableChecker == 1 && norm.y > 0.5) {
        // Projeção do chão (mantém igual)
        vec3 refPos = vec3(0.0, 0.0, 0.0);
        vec3 rayDir = FragPos - refPos;
        float t = (-2.0 - refPos.y) / rayDir.y;
        vec3 flatPos = refPos + t * rayDir;

        float scale = 1.0;
        float checker = mod(floor(flatPos.x * scale) + floor(flatPos.z * scale), 2.0);
        vec3 corEscura = vec3(0.12, 0.12, 0.12);
        vec3 corClara  = vec3(0.82, 0.82, 0.82);
        vec3 xadrez = mix(corEscura, corClara, checker);

        float distCamera = length(FragPos.xz);
        float fade = smoothstep(15.0, 24.0, distCamera);
        vec3 corSolida = vec3(0.45, 0.45, 0.45);
        baseColor = mix(xadrez, corSolida, fade);
    } else {
        // Paredes e Esferas
        baseColor = vertexColor * objectColor;
    }

    FragColor = vec4((ambient + diffuse) * baseColor, 1.0);
}