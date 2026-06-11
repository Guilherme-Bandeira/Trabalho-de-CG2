import glfw
from OpenGL.GL import *
import numpy as np
from PIL import Image
import ctypes
import math

WIDTH, HEIGHT = 1000, 700

sun_scale = 5.0

# Ângulo de rotação do sol ao redor do piso (ciclo dia/noite)
sun_angle = 90.0       # Começa em 90 para o sol iniciar no topo do céu (meio do dia)
sun_auto_rotate = True # rotação automática ligada por padrão
sun_speed = 1.0        # multiplicador de velocidade do sol (teclas CTRL+5 / CTRL+6)

obj4_angle = 180.0

obj5_pos = np.array([30.0, 0.0, 28.0], dtype=np.float32)

wireframe = False

# ============================================================
# CONTROLES DE ILUMINAÇÃO
# ============================================================
sun_intensity = 3.0
tv_intensity = 15.0    
lamp_intensity = 4.0   
ambient_intensity = 0.35
diffuse_intensity = 1.2 
specular_intensity = 1.0 

sun_on = True
tv_on = True
ambient_on = True
lamp_on = True         
diffuse_on = True      
specular_on = True     

# ================= CAMERA =================
camera_pos   = np.array([0.0, 2.0, 6.0],  dtype=np.float32)
camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
camera_up    = np.array([0.0, 1.0, 0.0],  dtype=np.float32)
camera_pos[1] = 2.0
speed = 0.09

yaw   = -90.0
pitch =   0.0
lastX = WIDTH  / 2
lastY = HEIGHT / 2
first_mouse = True

# ================= MATRIZES =================
def perspective(fov, aspect, near, far):
    f = 1.0 / math.tan(fov / 2)
    return np.array([
        [f/aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
        [0, 0, -1, 0]
    ], dtype=np.float32)

def lookAt(eye, center, up):
    f = (center - eye); f /= np.linalg.norm(f)
    s = np.cross(f, up); s /= np.linalg.norm(s)
    u = np.cross(s, f)
    result = np.identity(4, dtype=np.float32)
    result[0][0:3] = s
    result[1][0:3] = u
    result[2][0:3] = -f
    result[0][3] = -np.dot(s, eye)
    result[1][3] = -np.dot(u, eye)
    result[2][3] =  np.dot(f, eye)
    return result

# ================= INPUT =================
def key_callback(window, key, scancode, action, mods):
    global wireframe
    global sun_intensity, tv_intensity, ambient_intensity, tv_on, lamp_on, lamp_intensity, sun_on, ambient_on, diffuse_on, specular_on
    global sun_auto_rotate, sun_speed, diffuse_intensity, specular_intensity

    if action not in (glfw.PRESS, glfw.REPEAT):
        return

    if key == glfw.KEY_P and action == glfw.PRESS:
        wireframe = not wireframe
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if wireframe else GL_FILL)

    # ---- Liga/Desliga Toggles ----
    if key == glfw.KEY_O and action == glfw.PRESS:
        sun_on = not sun_on
        print(f"Sol: {'LIGADO' if sun_on else 'DESLIGADO'}")

    if key == glfw.KEY_T and action == glfw.PRESS:
        tv_on = not tv_on
        print(f"TV (Emissão de Luz): {'LIGADO' if tv_on else 'DESLIGADO'}")
        
    if key == glfw.KEY_L and action == glfw.PRESS: 
        lamp_on = not lamp_on
        print(f"Lâmpada Amarela: {'LIGADO' if lamp_on else 'DESLIGADO'}")

    if key == glfw.KEY_M and action == glfw.PRESS:
        ambient_on = not ambient_on
        print(f"Luz Ambiente: {'LIGADO' if ambient_on else 'DESLIGADO'}")

    if key == glfw.KEY_H and action == glfw.PRESS:
        diffuse_on = not diffuse_on
        print(f"Reflexão Difusa: {'LIGADA' if diffuse_on else 'DESLIGADA'}")

    if key == glfw.KEY_K and action == glfw.PRESS:
        specular_on = not specular_on
        print(f"Reflexão Especular: {'LIGADA' if specular_on else 'DESLIGADA'}")

    # ---- Intensidades das luzes ----
    if key == glfw.KEY_1:
        sun_intensity = max(0.0, sun_intensity - 0.2)
        print(f"Intensidade do Sol: {sun_intensity:.1f}")
    if key == glfw.KEY_2:
        sun_intensity += 0.2
        print(f"Intensidade do Sol: {sun_intensity:.1f}")

    if key == glfw.KEY_3:
        tv_intensity = max(0.0, tv_intensity - 1.0)
        print(f"Intensidade da TV: {tv_intensity:.1f}")
    if key == glfw.KEY_4 and mods != glfw.MOD_CONTROL:
        tv_intensity += 1.0
        print(f"Intensidade da TV: {tv_intensity:.1f}")

    if key == glfw.KEY_U:
        lamp_intensity = max(0.0, lamp_intensity - 0.4)
        print(f"Intensidade da Lâmpada: {lamp_intensity:.1f}")
    if key == glfw.KEY_I:
        lamp_intensity += 0.4
        print(f"Intensidade da Lâmpada: {lamp_intensity:.1f}")

    if key == glfw.KEY_5 and mods == glfw.MOD_CONTROL:
        sun_speed = max(0.1, sun_speed - 0.5)
        print(f"Velocidade do sol: {sun_speed:.1f}x")
    if key == glfw.KEY_6 and mods == glfw.MOD_CONTROL:
        sun_speed = min(20.0, sun_speed + 0.5)
        print(f"Velocidade do sol: {sun_speed:.1f}x")

    if key == glfw.KEY_4 and action == glfw.PRESS and mods == glfw.MOD_CONTROL:
        sun_auto_rotate = not sun_auto_rotate
        print(f"Rotação do sol: {'AUTO' if sun_auto_rotate else 'MANUAL'}")

    if key == glfw.KEY_7:
        ambient_intensity = max(0.0, ambient_intensity - 0.02)
        print(f"Ambiente: {ambient_intensity:.2f}")
    if key == glfw.KEY_8:
        ambient_intensity = min(1.0, ambient_intensity + 0.02)
        print(f"Ambiente: {ambient_intensity:.2f}")

    if key == glfw.KEY_9:
        diffuse_intensity = max(0.0, diffuse_intensity - 0.05)
        print(f"Ganho Difuso Global: {diffuse_intensity:.2f}")
    if key == glfw.KEY_0:
        diffuse_intensity = min(3.0, diffuse_intensity + 0.05)
        print(f"Ganho Difuso Global: {diffuse_intensity:.2f}")

    if key == glfw.KEY_MINUS:
        specular_intensity = max(0.0, specular_intensity - 0.05)
        print(f"Especular Global: {specular_intensity:.2f}")
    if key == glfw.KEY_EQUAL:
        specular_intensity = min(4.0, specular_intensity + 0.05)
        print(f"Especular Global: {specular_intensity:.2f}")

def process_input(window):
    global camera_pos, sun_scale, obj4_angle, obj5_pos, sun_angle, sun_speed

    front_flat = np.array([camera_front[0], 0, camera_front[2]])
    norm = np.linalg.norm(front_flat)
    if norm > 0:
        front_flat /= norm
    right = np.cross(front_flat, camera_up)

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera_pos += speed * front_flat
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera_pos -= speed * front_flat
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera_pos -= right * speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera_pos += right * speed
    if glfw.get_key(window, glfw.KEY_Z) == glfw.PRESS:
        camera_pos[1] += speed
    if glfw.get_key(window, glfw.KEY_X) == glfw.PRESS:
        camera_pos[1] -= speed

    if glfw.get_key(window, glfw.KEY_C) == glfw.PRESS:
        sun_scale += 0.05
    if glfw.get_key(window, glfw.KEY_V) == glfw.PRESS:
        sun_scale = max(0.1, sun_scale - 0.05)

    if glfw.get_key(window, glfw.KEY_Q) == glfw.PRESS:
        sun_angle += 0.5
    if glfw.get_key(window, glfw.KEY_E) == glfw.PRESS:
        sun_angle -= 0.5

    if glfw.get_key(window, glfw.KEY_B) == glfw.PRESS:
        obj4_angle += 1.0
    if glfw.get_key(window, glfw.KEY_N) == glfw.PRESS:
        obj4_angle -= 1.0

    move_speed = 0.1
    if glfw.get_key(window, glfw.KEY_UP)    == glfw.PRESS: obj5_pos[2] -= move_speed
    if glfw.get_key(window, glfw.KEY_DOWN)  == glfw.PRESS: obj5_pos[2] += move_speed
    if glfw.get_key(window, glfw.KEY_LEFT)  == glfw.PRESS: obj5_pos[0] -= move_speed
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS: obj5_pos[0] += move_speed

    lim = 200
    camera_pos[0] = max(-lim, min(lim, camera_pos[0]))
    camera_pos[2] = max(-lim, min(lim, camera_pos[2]))
    camera_pos[1] = max(0.0,  min(120.0, camera_pos[1]))

def mouse_callback(window, xpos, ypos):
    global lastX, lastY, first_mouse, yaw, pitch, camera_front

    if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) != glfw.PRESS:
        first_mouse = True
        return
    if first_mouse:
        lastX, lastY = xpos, ypos
        first_mouse = False

    xoffset = (xpos - lastX) * 0.1
    yoffset = (lastY - ypos) * 0.1
    lastX, lastY = xpos, ypos

    yaw   += xoffset
    pitch  = max(-89, min(89, pitch + yoffset))

    front = np.array([
        math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)),
        math.sin(math.radians(pitch)),
        math.sin(math.radians(yaw)) * math.cos(math.radians(pitch)),
    ], dtype=np.float32)
    camera_front = front / np.linalg.norm(front)

def create_shader(vs, fs):
    v = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(v, vs); glCompileShader(v)
    if not glGetShaderiv(v, GL_COMPILE_STATUS):
        print("ERRO vertex shader:", glGetShaderInfoLog(v).decode())

    f = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(f, fs); glCompileShader(f)
    if not glGetShaderiv(f, GL_COMPILE_STATUS):
        print("ERRO fragment shader:", glGetShaderInfoLog(f).decode())

    s = glCreateProgram()
    glAttachShader(s, v); glAttachShader(s, f)
    glLinkProgram(s)
    if not glGetProgramiv(s, GL_LINK_STATUS):
        print("ERRO link:", glGetProgramInfoLog(s).decode())
    return s

def load_texture(path):
    try:
        img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        data = np.array(img, dtype=np.uint8)
        tex  = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0,
                     GL_RGB, GL_UNSIGNED_BYTE, data)
        glGenerateMipmap(GL_TEXTURE_2D)
        return tex
    except Exception as e:
        print(f"Erro ao carregar textura {path}: {e}")
        return None

def load_cubemap(paths):
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, tex)
    for i, p in enumerate(paths):
        img  = Image.open(p).resize((1024, 1024))
        data = np.array(img)
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB,
                     1024, 1024, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    return tex

def load_obj(path):
    vertices  = []
    texcoords = []
    normals   = []
    final     = []

    with open(path, 'r') as f:
        for line in f:
            if   line.startswith('v '):
                vertices.append(list(map(float, line.split()[1:4])))
            elif line.startswith('vt '):
                texcoords.append(list(map(float, line.split()[1:3])))
            elif line.startswith('vn '):
                normals.append(list(map(float, line.split()[1:4])))
            elif line.startswith('f '):
                parts = line.split()[1:]
                for i in range(1, len(parts) - 1):
                    for p in (parts[0], parts[i], parts[i+1]):
                        vals = p.split('/')
                        v  = vertices[int(vals[0]) - 1]
                        vt = texcoords[int(vals[1]) - 1] if len(vals) > 1 and vals[1] else [0.0, 0.0]
                        vn = normals[int(vals[2]) - 1]   if len(vals) > 2 and vals[2] else [0.0, 1.0, 0.0]
                        final.extend(v + vt + vn)
    return np.array(final, dtype=np.float32)

def load_mtl(mtl_path):
    import os
    materials   = {}
    current_mat = None
    base_dir    = os.path.dirname(mtl_path)
    try:
        with open(mtl_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('newmtl '):
                    current_mat = line.split(None, 1)[1].strip()
                    materials[current_mat] = {'tex': None, 'kd': (0.8, 0.8, 0.8)}
                elif current_mat:
                    if line.startswith('Kd '):
                        vals = line.split()[1:]
                        materials[current_mat]['kd'] = tuple(float(v) for v in vals[:3])
                    elif line.startswith('map_Kd '):
                        tex_file   = line.split(None, 1)[1].strip().lstrip('/\\')
                        candidate1 = os.path.normpath(os.path.join(base_dir, tex_file))
                        candidate2 = os.path.normpath(tex_file)
                        if os.path.exists(candidate1):
                            materials[current_mat]['tex'] = candidate1
                        elif os.path.exists(candidate2):
                            materials[current_mat]['tex'] = candidate2
                        else:
                            print(f"Textura não encontrada: {tex_file}")
    except Exception as e:
        print(f"Erro ao carregar MTL {mtl_path}: {e}")
    return materials

def _make_solid_texture(r, g, b):
    if r == 0.0 and g == 0.0 and b == 0.0:
        r, g, b = 0.7, 0.7, 0.7
    data = np.array([[[int(r*255), int(g*255), int(b*255)]]], dtype=np.uint8)
    tex  = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 1, 1, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tex

def _triangulate_face(parts):
    tris = []
    for i in range(1, len(parts) - 1):
        tris.extend([parts[0], parts[i], parts[i+1]])
    return tris

def load_obj_mtl(obj_path):
    import os
    vertices  = []
    texcoords = []
    normals   = []
    mtl_file  = None
    base_dir  = os.path.dirname(obj_path)
    groups      = {}
    current_mat = "__default__"
    groups[current_mat] = []

    with open(obj_path, 'r') as f:
        for line in f:
            line = line.strip()
            if   line.startswith('v '):
                vertices.append(list(map(float, line.split()[1:4])))
            elif line.startswith('vt '):
                texcoords.append(list(map(float, line.split()[1:3])))
            elif line.startswith('vn '):
                normals.append(list(map(float, line.split()[1:4])))
            elif line.startswith('mtllib '):
                mtl_file = os.path.join(base_dir, line.split(None, 1)[1].strip())
            elif line.startswith('usemtl '):
                current_mat = line.split(None, 1)[1].strip()
                if current_mat not in groups:
                    groups[current_mat] = []
            elif line.startswith('f '):
                parts    = line.split()[1:]
                tri_parts = _triangulate_face(parts)
                for p in tri_parts:
                    vals = p.split('/')
                    v  = vertices[int(vals[0]) - 1]
                    vt = texcoords[int(vals[1]) - 1] if len(vals) > 1 and vals[1] else [0.0, 0.0]
                    vn = normals[int(vals[2]) - 1]   if len(vals) > 2 and vals[2] else [0.0, 1.0, 0.0]
                    groups[current_mat].extend(v + vt + vn)

    mat_info = load_mtl(mtl_file) if mtl_file and os.path.exists(mtl_file) else {}
    result   = []
    for mat_name, floats in groups.items():
        if not floats:
            continue
        data = np.array(floats, dtype=np.float32)
        info = mat_info.get(mat_name, {'tex': None, 'kd': (0.8, 0.8, 0.8)})
        result.append((data, mat_name, info))
    return result

def create_vao(data, stride=8):
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    stride_bytes = stride * 4
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)
    if stride == 8:
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride_bytes, ctypes.c_void_p(20))
        glEnableVertexAttribArray(2)
    glBindVertexArray(0)
    return VAO

def create_vao_mtl(groups):
    vaos = []
    for (data, mat_name, info) in groups:
        VAO = create_vao(data, stride=8)
        tex = load_texture(info['tex']) if info['tex'] else None
        if tex is None:
            r, g, b = info.get('kd', (0.8, 0.8, 0.8))
            tex = _make_solid_texture(r, g, b)
        vaos.append((VAO, len(data) // 8, tex))
    return vaos

def draw_obj_mtl(vaos, shader, model_matrix):
    glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_TRUE, model_matrix)
    glActiveTexture(GL_TEXTURE0)
    for (VAO, n_verts, tex) in vaos:
        if tex is None:
            continue
        glBindVertexArray(VAO)
        glBindTexture(GL_TEXTURE_2D, tex)
        glDrawArrays(GL_TRIANGLES, 0, n_verts)


# ================= MAIN =================
def main():
    global sun_angle, sun_auto_rotate

    glfw.init()
    window = glfw.create_window(WIDTH, HEIGHT, "FINAL CG", None, None)
    glfw.make_context_current(window)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)
    glEnable(GL_DEPTH_TEST)

    # ============================================================
    # SHADOW MAP
    # ============================================================
    SHADOW_W, SHADOW_H = 2048, 2048

    depth_fbo = glGenFramebuffers(1)
    depth_tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, depth_tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, SHADOW_W, SHADOW_H,
                 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
    
    glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR,
                     np.array([1,1,1,1], dtype=np.float32))
    glBindFramebuffer(GL_FRAMEBUFFER, depth_fbo)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth_tex, 0)
    glDrawBuffer(GL_NONE)
    glReadBuffer(GL_NONE)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    depth_shader = create_shader("""
    #version 330 core
    layout(location=0) in vec3 aPos;
    layout(location=1) in vec2 aTex;
    layout(location=2) in vec3 aNormal;
    uniform mat4 lightSpaceMatrix;
    uniform mat4 model;
    void main(){
        gl_Position = lightSpaceMatrix * model * vec4(aPos, 1.0);
    }""",
    """
    #version 330 core
    void main(){ }
    """)

    # ============================================================
    # SHADER PRINCIPAL — Mascara de Iluminação por Orientação de Normais
    # ============================================================
    shader = create_shader(
    # ---- VERTEX SHADER ----
    """
    #version 330 core
    layout(location=0) in vec3 aPos;
    layout(location=1) in vec2 aTex;
    layout(location=2) in vec3 aNormal;

    out vec2  TexCoord;
    out vec3  FragPos;
    out vec3  Normal;
    out vec4  FragPosLightSpace;

    uniform mat4 model, view, projection;
    uniform mat4 lightSpaceMatrix;

    void main() {
        vec4 worldPos    = model * vec4(aPos, 1.0);
        FragPos          = worldPos.xyz;
        Normal           = normalize(mat3(transpose(inverse(model))) * aNormal);
        TexCoord         = aTex;
        FragPosLightSpace = lightSpaceMatrix * worldPos;
        gl_Position      = projection * view * worldPos;
    }
    """,
    # ---- FRAGMENT SHADER ----
    """
    #version 330 core
    in vec2  TexCoord;
    in vec3  FragPos;
    in vec3  Normal;
    in vec4  FragPosLightSpace;

    out vec4 FragColor;

    uniform sampler2D tex;
    uniform sampler2D shadowMap;

    uniform vec3  cameraPos;

    // Sol
    uniform vec3  sunPos;
    uniform float sunIntensity;

    // TV — spotlight
    uniform vec3  tvPos;
    uniform vec3  tvDir;
    uniform float tvCutoffInner;
    uniform float tvCutoffOuter;
    uniform float tvIntensity;

    // Lâmpada — Luz Radial Amarela
    uniform vec3  lampPos;
    uniform float lampIntensity;

    uniform float ambientStrength;
    uniform float globalDiffuseIntensity;  
    uniform float globalSpecularIntensity;

    uniform float matDiffuse;    
    uniform float matSpecular;   
    uniform float matShininess;  

    uniform int   isInterior;

    float calcShadow(vec4 fragPosLS, vec3 norm, vec3 lightDir) {
        vec3 projCoords = fragPosLS.xyz / fragPosLS.w;
        projCoords = projCoords * 0.5 + 0.5;
        if (projCoords.z > 1.0) return 1.0; 

        float bias = max(0.0015 * (1.0 - dot(norm, lightDir)), 0.0005);
        float shadow = 0.0;
        vec2  texelSize = 1.0 / textureSize(shadowMap, 0);
        for (int x = -1; x <= 1; x++) {
            for (int y = -1; y <= 1; y++) {
                float pcfDepth = texture(shadowMap, projCoords.xy + vec2(x, y) * texelSize).r;
                shadow += (projCoords.z - bias) > pcfDepth ? 1.0 : 0.0;
            }
        }
        return shadow / 9.0;
    }

    vec3 calcSunLight(vec3 lightPos, vec3 lightColor, float strength,
                      vec3 norm, vec3 fragPos, vec3 viewDir, vec3 texColor) {
        vec3  lightDir    = normalize(lightPos - fragPos);
        float dist        = length(lightPos - fragPos);
        float attenuation = 1.0 / (1.0 + 0.0001 * dist + 0.000001 * dist * dist);

        float diff    = max(dot(norm, lightDir), 0.0);
        vec3  diffuse = matDiffuse * diff * texColor * lightColor * strength * globalDiffuseIntensity * attenuation;

        vec3  halfDir  = normalize(lightDir + viewDir);
        float spec     = pow(max(dot(norm, halfDir), 0.0), matShininess);
        vec3  specular = matSpecular * spec * lightColor * strength * globalSpecularIntensity * attenuation;

        return (diffuse + specular);
    }

    vec3 calcSpotLight(vec3 lightPos, vec3 spotDir, float cutInner, float cutOuter,
                       vec3 lightColor, float strength,
                       vec3 norm, vec3 fragPos, vec3 viewDir, vec3 texColor) {
        vec3  lightDir = normalize(lightPos - fragPos);
        float dist     = length(lightPos - fragPos);
        float attenuation = 1.0 / (1.0 + 0.02 * dist + 0.001 * dist * dist);

        float theta   = dot(lightDir, normalize(-spotDir));
        float epsilon = cutInner - cutOuter;
        float intensity = clamp((theta - cutOuter) / epsilon, 0.0, 1.0);

        float diff    = max(dot(norm, lightDir), 0.0);
        vec3  diffuse = matDiffuse * diff * texColor * lightColor * strength * intensity * globalDiffuseIntensity * attenuation;

        vec3  halfDir  = normalize(lightDir + viewDir);
        float spec     = pow(max(dot(norm, halfDir), 0.0), matShininess);
        vec3  specular = matSpecular * spec * lightColor * strength * globalSpecularIntensity * intensity * attenuation;

        return diffuse + specular;
    }

    vec3 calcPointLight(vec3 lightPos, vec3 lightColor, float strength,
                        vec3 norm, vec3 fragPos, vec3 viewDir, vec3 texColor) {
        vec3 lightDir = normalize(lightPos - fragPos);
        float dist = length(lightPos - fragPos);
        
        float attenuation = 1.0 / (1.0 + 0.1 * dist + 0.05 * dist * dist);
        
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = matDiffuse * diff * texColor * lightColor * strength * globalDiffuseIntensity * attenuation;
        
        vec3 halfDir = normalize(lightDir + viewDir);
        float spec = pow(max(dot(norm, halfDir), 0.0), matShininess);
        vec3 specular = matSpecular * spec * lightColor * strength * globalSpecularIntensity * attenuation;
        
        return diffuse + specular;
    }

    void main() {
        vec4 texSample = texture(tex, TexCoord);
        vec3 texColor  = texSample.rgb;
        vec3 norm      = normalize(Normal);
        vec3 viewDir   = normalize(cameraPos - FragPos);

        float ambStr   = (isInterior == 1) ? ambientStrength * 0.4 : ambientStrength;
        vec3  ambient  = ambStr * texColor;

        vec3 lighting = ambient;

        // O Sol afeta exclusivamente objetos Externos
        if (isInterior == 0) {
            if (sunIntensity > 0.0 && sunPos.y >= 0.0) {
                vec3 lightDir = normalize(sunPos - FragPos);
                float shadow  = calcShadow(FragPosLightSpace, norm, lightDir);
                vec3 sunLight = calcSunLight(sunPos, vec3(1.0, 0.97, 0.85), sunIntensity, norm, FragPos, viewDir, texColor);
                lighting += (1.0 - shadow) * sunLight;
            }
        }

        // CORREÇÃO MESH DOUBLE-SIDED: Filtramos as luzes internas pela direção da normal (dot product)
        if (isInterior == 1) {
            
            // TV (Spotlight): Como ela aponta para dentro, se colidir com uma parede cuja normal aponta
            // para o exterior (+X), o produto dot(norm, tvDir) nos diz se estamos na face interna.
            // Para meshes double-sided, as normais internas apontam em direção ao centro da sala, reagindo perfeitamente.
            if (tvIntensity > 0.0) {
                vec3 lightDirTV = normalize(tvPos - FragPos);
                // Se a normal aponta no sentido oposto ao raio emitido pela TV, barramos na parede exterior.
                if (dot(norm, lightDirTV) >= -0.1) {
                    lighting += calcSpotLight(tvPos, tvDir, tvCutoffInner, tvCutoffOuter,
                                              vec3(0.85, 0.92, 1.0), tvIntensity, 
                                              norm, FragPos, viewDir, texColor);
                }
            }
            
            // Lâmpada (Point Light): Fica no centro da casa. O vetor de luz viaja de dentro para fora.
            // As paredes internas da casa têm normais que apontam para o centro (para a lâmpada).
            // Portanto, o produto escalar dot(norm, lightDirLamp) será estritamente POSITIVO por dentro,
            // e NEGATIVO nas paredes e teto por fora. Restaura os reflexos internos de forma absoluta!
            if (lampIntensity > 0.0) {
                vec3 lightDirLamp = normalize(lampPos - FragPos);
                if (dot(norm, lightDirLamp) >= -0.05) { 
                    lighting += calcPointLight(lampPos, vec3(1.0, 0.75, 0.35), lampIntensity,
                                               norm, FragPos, viewDir, texColor);
                }
            }
        }

        lighting  = clamp(lighting, 0.0, 1.0);
        FragColor = vec4(lighting, texSample.a);
    }
    """)

    # ---- Shaders Auxiliares ----
    sky_shader = create_shader("""
    #version 330 core
    layout(location=0) in vec3 aPos;
    out vec3 TexCoords;
    uniform mat4 view, projection;
    void main(){
        TexCoords   = aPos;
        vec4 pos    = projection * view * vec4(aPos, 1.0);
        gl_Position = pos.xyww;
    }""",
    """
    #version 330 core
    in vec3 TexCoords;
    out vec4 FragColor;
    uniform samplerCube skybox;
    void main(){
        FragColor = texture(skybox, TexCoords);
    }""")

    sun_shader = create_shader("""
    #version 330 core
    layout(location=0) in vec3 aPos;
    layout(location=1) in vec2 aTex;
    out vec2 TexCoord;
    uniform mat4 model, view, projection;
    void main(){
        TexCoord    = aTex;
        gl_Position = projection * view * model * vec4(aPos, 1.0);
    }""",
    """
    #version 330 core
    in vec2 TexCoord;
    out vec4 FragColor;
    uniform sampler2D tex;
    uniform float sunIntensity;
    void main(){
        vec4 c = texture(tex, TexCoord);
        float brightness = clamp(sunIntensity / 3.0, 0.05, 1.5);
        c.rgb *= brightness;
        FragColor = clamp(c, 0.0, 1.0);
    }""")

    emissive_shader = create_shader("""
    #version 330 core
    layout(location=0) in vec3 aPos;
    layout(location=1) in vec2 aTex;
    out vec2 TexCoord;
    uniform mat4 model, view, projection;
    void main(){
        TexCoord    = aTex;
        gl_Position = projection * view * model * vec4(aPos, 1.0);
    }""",
    """
    #version 330 core
    in vec2 TexCoord;
    out vec4 FragColor;
    uniform sampler2D tex;
    uniform bool lightOn;
    uniform vec3 emissiveColor;
    uniform float emissivePower;
    void main(){
        vec4 c = texture(tex, TexCoord);
        if (lightOn) {
            c.rgb = mix(c.rgb, emissiveColor, 0.4) * emissivePower;
        } else {
            c.rgb *= 0.15;
        }
        FragColor = clamp(c, 0.0, 1.0);
    }""")

    # ============================================================
    # GEOMETRIA DOS PISOS
    # ============================================================
    grass = np.array([
        -200,0,-200, 0,0,     0,1,0,
         200,0,-200, 200,0,   0,1,0,
         200,0, 200, 200,200, 0,1,0,
         200,0, 200, 200,200, 0,1,0,
        -200,0, 200, 0,200,   0,1,0,
        -200,0,-200, 0,0,     0,1,0,
    ], dtype=np.float32)

    inside = np.array([
        -5,0.01,-5, 0,0, 0,1,0,
         5,0.01,-5, 1,0, 0,1,0,
         5,0.01, 5, 1,1, 0,1,0,
         5,0.01, 5, 1,1, 0,1,0,
        -5,0.01, 5, 0,1, 0,1,0,
        -5,0.01,-5, 0,0, 0,1,0,
    ], dtype=np.float32)

    # ============================================================
    # TEXTURAS
    # ============================================================
    tex_sun    = load_texture("texturas/Sun.jpg")
    tex_grass  = load_texture("texturas/grass.jpg")
    tex_inside = load_texture("texturas/floor_inside.jpg")
    tex_casa   = load_texture("texturas/House.png")
    skybox     = load_cubemap([
        "texturas/skybox/right.jpg",
        "texturas/skybox/left.jpg",
        "texturas/skybox/top.jpg",
        "texturas/skybox/bottom.jpg",
        "texturas/skybox/front.jpg",
        "texturas/skybox/back.jpg",
    ])

    # ============================================================
    # VAOs
    # ============================================================
    VAO_grass  = create_vao(grass,  stride=8)
    VAO_inside = create_vao(inside, stride=8)

    sun_data  = load_obj("Objetos/Sun.obj")
    VAO_sun   = create_vao(sun_data, stride=8)

    house_data = load_obj("Objetos/House.obj")
    VAO_house  = create_vao(house_data, stride=8)

    obj1_groups = load_obj_mtl("Objetos/Outdoor Sofa.obj")
    VAOs_obj1   = create_vao_mtl(obj1_groups)

    obj2_groups = load_obj_mtl("Objetos/table.obj")
    VAOs_obj2   = create_vao_mtl(obj2_groups)

    obj3_groups = load_obj_mtl("Objetos/10113_Flat Screen Television_v1_L3.obj")
    VAOs_obj3   = create_vao_mtl(obj3_groups)

    obj4_groups = load_obj_mtl("Objetos/doghouse.obj")
    VAOs_obj4   = create_vao_mtl(obj4_groups)

    obj5_groups = load_obj_mtl("Objetos/kodi.obj")
    VAOs_obj5   = create_vao_mtl(obj5_groups)

    lamp_groups = load_obj_mtl("Objetos/lamp.obj")
    VAOs_lamp   = create_vao_mtl(lamp_groups)

    samsung_groups = load_obj_mtl("Objetos/Samsung.obj")
    VAOs_samsung   = create_vao_mtl(samsung_groups)

    skybox_vertices = np.array([
        -1,-1, 1,  1,-1, 1,  1, 1, 1,
         1, 1, 1, -1, 1, 1, -1,-1, 1,
        -1,-1,-1, -1, 1,-1,  1, 1,-1,
         1, 1,-1,  1,-1,-1, -1,-1,-1,
        -1, 1,-1, -1, 1, 1,  1, 1, 1,
         1, 1, 1,  1, 1,-1, -1, 1,-1,
        -1,-1,-1,  1,-1,-1,  1,-1, 1,
         1,-1, 1, -1,-1, 1, -1,-1,-1,
         1,-1,-1,  1, 1,-1,  1, 1, 1,
         1, 1, 1,  1,-1, 1,  1,-1,-1,
        -1,-1,-1, -1,-1, 1, -1, 1, 1,
        -1, 1, 1, -1, 1,-1, -1,-1,-1,
    ], dtype=np.float32)

    skyVAO = glGenVertexArrays(1)
    skyVBO = glGenBuffers(1)
    glBindVertexArray(skyVAO)
    glBindBuffer(GL_ARRAY_BUFFER, skyVBO)
    glBufferData(GL_ARRAY_BUFFER, skybox_vertices.nbytes, skybox_vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glBindVertexArray(0)

    glUseProgram(shader);     glUniform1i(glGetUniformLocation(shader,     "tex"),    0)
    glUseProgram(sun_shader); glUniform1i(glGetUniformLocation(sun_shader, "tex"),    0)
    glUseProgram(sky_shader); glUniform1i(glGetUniformLocation(sky_shader, "skybox"), 0)
    glUseProgram(0)

    SUN_ORBIT_RADIUS = 354.0
    SUN_ORBIT_Z      = 100.0

    last_time = glfw.get_time()

    TV_POS   = np.array([15.0, 6.5, -10.0], dtype=np.float32)
    LAMP_POS = np.array([0.0, 5.0, 8.0], dtype=np.float32) 

    print("\n=== CONTROLES DE ILUMINAÇÃO ===")
    print("  O   — Liga / Desliga o Sol")
    print("  T   — Liga / Desliga a Emissão da TV")
    print("  L   — Liga / Desliga a Lâmpada Radial Amarela")
    print("  M   — Liga / Desliga a Luz Ambiente Global")
    print("  H   — Liga / Desliga Reflexão Difusa das Luzes")
    print("  K   — Liga / Desliga Reflexão Especular das Luzes")
    print("--------------------------------")
    print("  1/2 — Decrementa / Incrementa Intensidade do Sol")
    print("  3/4 — Decrementa / Incrementa Intensidade da TV")
    print("  U/I — Decrementa / Incrementa Intensidade da Lâmpada")
    print("  7/8 — Decrementa / Incrementa Luz Ambiente Global")
    print("  9/0 — Decrementa / Incrementa Intensidade Difusa Global")
    print("  -/= — Decrementa / Incrementa Reflexão Especular Global")
    print("================================\n")

    # ============================================================
    # LOOP PRINCIPAL
    # ============================================================
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time    = current_time

        process_input(window)

        if sun_auto_rotate:
            sun_angle += dt * (360.0 / 120.0) * sun_speed
        sun_angle %= 360.0

        rad = math.radians(sun_angle)
        sun_world_pos = np.array([
            SUN_ORBIT_RADIUS * math.cos(rad),
            SUN_ORBIT_RADIUS * math.sin(rad),
            SUN_ORBIT_Z
        ], dtype=np.float32)

        view = lookAt(camera_pos, camera_pos + camera_front, camera_up)
        proj = perspective(math.radians(45), WIDTH / HEIGHT, 0.1, 500)

        model1_sm = np.identity(4, dtype=np.float32)
        model1_sm[0][3] = -10.0; model1_sm[2][3] = -10.0
        model1_sm[0][0] = model1_sm[1][1] = model1_sm[2][2] = 8.0

        angle4 = math.radians(obj4_angle)
        c4, s4 = math.cos(angle4), math.sin(angle4)
        rot_y4 = np.array([[ c4,0,s4,0],[0,1,0,0],[-s4,0,c4,0],[0,0,0,1]], dtype=np.float32)
        scale4 = np.diag([6.0, 6.0, 6.0, 1.0]).astype(np.float32)
        trans4 = np.identity(4, dtype=np.float32); trans4[0][3]=30.0; trans4[2][3]=28.0
        model4_sm = trans4 @ rot_y4 @ scale4

        model5_sm = np.identity(4, dtype=np.float32)
        model5_sm[0][3]=obj5_pos[0]; model5_sm[1][3]=obj5_pos[1]; model5_sm[2][3]=obj5_pos[2]

        # ============================================================
        # PASSO 1 — SHADOW MAP
        # ============================================================
        sun_dir = -sun_world_pos / (np.linalg.norm(sun_world_pos) + 1e-6)
        scene_center = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        light_pos_sm = scene_center - sun_dir * 300.0

        def ortho(l, r, b, t, n, f):
            return np.array([
                [2/(r-l), 0, 0, -(r+l)/(r-l)],
                [0, 2/(t-b), 0, -(t+b)/(t-b)],
                [0, 0, -2/(f-n), -(f+n)/(f-n)],
                [0, 0, 0, 1],
            ], dtype=np.float32)

        light_proj = ortho(-400, 400, -400, 400, 1.0, 1200.0)
        up_sm = np.array([0.0, 0.0, 1.0] if abs(sun_dir[1]) > 0.9 else [0.0, 1.0, 0.0], dtype=np.float32)
        light_view = lookAt(light_pos_sm, scene_center, up_sm)
        light_space_matrix = light_proj @ light_view

        glViewport(0, 0, SHADOW_W, SHADOW_H)
        glBindFramebuffer(GL_FRAMEBUFFER, depth_fbo)
        glClear(GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        
        glUseProgram(depth_shader)
        glUniformMatrix4fv(glGetUniformLocation(depth_shader, "lightSpaceMatrix"), 1, GL_TRUE, light_space_matrix)

        def draw_depth(model_mat):
            glUniformMatrix4fv(glGetUniformLocation(depth_shader, "model"), 1, GL_TRUE, model_mat)

        draw_depth(np.identity(4, dtype=np.float32))
        glBindVertexArray(VAO_grass); glDrawArrays(GL_TRIANGLES, 0, 6)

        glDisable(GL_CULL_FACE)
        model_house_sm = np.identity(4, dtype=np.float32)
        model_house_sm[0][0] = model_house_sm[1][1] = model_house_sm[2][2] = 60.0
        draw_depth(model_house_sm)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)

        for model_mat, vaos in [(model1_sm, VAOs_obj1), (model4_sm, VAOs_obj4), (model5_sm, VAOs_obj5)]:
            draw_depth(model_mat)
            for (VAO, n_verts, _) in vaos:
                glBindVertexArray(VAO); glDrawArrays(GL_TRIANGLES, 0, n_verts)

        glCullFace(GL_BACK)
        glDisable(GL_CULL_FACE)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, WIDTH, HEIGHT)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        TV_SPOT_DIR = np.array([-1.0, -0.4, 0.0], dtype=np.float32)
        TV_SPOT_DIR /= np.linalg.norm(TV_SPOT_DIR)

        def set_lighting_uniforms(prog, is_interior, kd=0.8, ks=0.0, shininess=32.0):
            glUseProgram(prog)
            glUniform3fv(glGetUniformLocation(prog, "cameraPos"),     1, camera_pos)
            glUniform3fv(glGetUniformLocation(prog, "sunPos"),        1, sun_world_pos)
            glUniform1f( glGetUniformLocation(prog, "sunIntensity"),  sun_intensity if sun_on else 0.0)
            glUniform3fv(glGetUniformLocation(prog, "tvPos"),         1, TV_POS)
            glUniform3fv(glGetUniformLocation(prog, "tvDir"),         1, TV_SPOT_DIR)
            glUniform1f( glGetUniformLocation(prog, "tvCutoffInner"), math.cos(math.radians(35)))
            glUniform1f( glGetUniformLocation(prog, "tvCutoffOuter"), math.cos(math.radians(50))) 
            glUniform1f( glGetUniformLocation(prog, "tvIntensity"),   tv_intensity if tv_on else 0.0)
            
            glUniform3fv(glGetUniformLocation(prog, "lampPos"),       1, LAMP_POS)
            glUniform1f( glGetUniformLocation(prog, "lampIntensity"),  lamp_intensity if lamp_on else 0.0)
            
            glUniform1f( glGetUniformLocation(prog, "ambientStrength"), ambient_intensity if ambient_on else 0.0)
            glUniform1f( glGetUniformLocation(prog, "globalDiffuseIntensity"),  diffuse_intensity if diffuse_on else 0.0)
            glUniform1f( glGetUniformLocation(prog, "globalSpecularIntensity"), specular_intensity if specular_on else 0.0)
            
            glUniform1f( glGetUniformLocation(prog, "matDiffuse"),     kd)
            glUniform1f( glGetUniformLocation(prog, "matSpecular"),    ks)
            glUniform1f( glGetUniformLocation(prog, "matShininess"),   shininess)
            
            glUniform1i( glGetUniformLocation(prog, "isInterior"),      is_interior)
            glUniform1i( glGetUniformLocation(prog, "shadowMap"),     1)
            glUniformMatrix4fv(glGetUniformLocation(prog, "lightSpaceMatrix"), 1, GL_TRUE, light_space_matrix)

        # ============================================================
        # 1. SKYBOX
        # ============================================================
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisable(GL_DEPTH_TEST)
        glUseProgram(sky_shader)
        view_no_t = view.copy()
        view_no_t[0][3] = view_no_t[1][3] = view_no_t[2][3] = 0
        glUniformMatrix4fv(glGetUniformLocation(sky_shader, "view"),       1, GL_TRUE, view_no_t)
        glUniformMatrix4fv(glGetUniformLocation(sky_shader, "projection"), 1, GL_TRUE, proj)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, skybox)
        glBindVertexArray(skyVAO)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glEnable(GL_DEPTH_TEST)

        if wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # ============================================================
        # 2. SOL
        # ============================================================
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glUseProgram(sun_shader)
        glUniformMatrix4fv(glGetUniformLocation(sun_shader, "view"),       1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(sun_shader, "projection"), 1, GL_TRUE, proj)
        glUniform1f(glGetUniformLocation(sun_shader, "sunIntensity"), sun_intensity if sun_on else 0.0)

        model_sun = np.identity(4, dtype=np.float32)
        model_sun[0][3] = sun_world_pos[0]; model_sun[1][3] = sun_world_pos[1]; model_sun[2][3] = sun_world_pos[2]
        model_sun[0][0] = model_sun[1][1] = model_sun[2][2] = sun_scale

        glUniformMatrix4fv(glGetUniformLocation(sun_shader, "model"), 1, GL_TRUE, model_sun)
        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(VAO_sun); glBindTexture(GL_TEXTURE_2D, tex_sun); glDrawArrays(GL_TRIANGLES, 0, len(sun_data) // 8)
        glDisable(GL_CULL_FACE)

        # ============================================================
        # 3. PISOS
        # ============================================================
        glUseProgram(shader)
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"),       1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_TRUE, proj)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, depth_tex)
        glActiveTexture(GL_TEXTURE0)

        model_id = np.identity(4, dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_TRUE, model_id)

        # Grama (Exterior)
        set_lighting_uniforms(shader, is_interior=0, kd=0.8, ks=0.0, shininess=1.0)
        glBindVertexArray(VAO_grass); glBindTexture(GL_TEXTURE_2D, tex_grass); glDrawArrays(GL_TRIANGLES, 0, 6)

        # Piso Interno (Interior)
        set_lighting_uniforms(shader, is_interior=1, kd=0.75, ks=0.2, shininess=16.0)
        glBindVertexArray(VAO_inside); glBindTexture(GL_TEXTURE_2D, tex_inside); glDrawArrays(GL_TRIANGLES, 0, 6)

        # ============================================================
        # 4. CASA 
        # ============================================================
        set_lighting_uniforms(shader, is_interior=1, kd=0.8, ks=0.0, shininess=1.0)
        glBindVertexArray(VAO_house); glBindTexture(GL_TEXTURE_2D, tex_casa)
        model_house = np.identity(4, dtype=np.float32)
        model_house[0][0] = model_house[1][1] = model_house[2][2] = 60.0
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_TRUE, model_house)
        glDrawArrays(GL_TRIANGLES, 0, len(house_data) // 8)

        # ============================================================
        # 5. OBJETOS EXTERNOS
        # ============================================================
        set_lighting_uniforms(shader, is_interior=0, kd=0.8, ks=0.1, shininess=8.0)
        draw_obj_mtl(VAOs_obj4, shader, model4_sm)
        draw_obj_mtl(VAOs_obj5, shader, model5_sm)

        # ============================================================
        # 6. OBJETOS INTERNOS
        # ============================================================
        
        # Sofá Outdoor (Tecido)
        set_lighting_uniforms(shader, is_interior=1, kd=0.85, ks=0.0, shininess=1.0)
        draw_obj_mtl(VAOs_obj1, shader, model1_sm)

        # Objeto 2 — Mesa
        set_lighting_uniforms(shader, is_interior=1, kd=0.7, ks=0.25, shininess=24.0)
        angle2   = math.radians(90); cos2, sin2 = math.cos(angle2), math.sin(angle2); scale2   = 0.22
        rot_y2   = np.array([[cos2*scale2, 0, sin2*scale2, 13.0], [0, scale2, 0, 0.0], [-sin2*scale2, 0, cos2*scale2, -3.0], [0, 0, 0, 1.0]], dtype=np.float32)
        draw_obj_mtl(VAOs_obj2, shader, rot_y2)

        # Lâmpada (lamp)
        set_lighting_uniforms(shader, is_interior=1, kd=0.6, ks=0.4, shininess=32.0)
        model_lamp = np.identity(4, dtype=np.float32)
        model_lamp[0][3] = 0.0; model_lamp[1][3] = 0.0; model_lamp[2][3] = 8.0
        model_lamp[0][0] = model_lamp[1][1] = model_lamp[2][2] = 1.0          
        draw_obj_mtl(VAOs_lamp, shader, model_lamp)

        # Geladeira (Samsung)
        set_lighting_uniforms(shader, is_interior=1, kd=0.9, ks=0.9, shininess=128.0)
        model_samsung = np.identity(4, dtype=np.float32)
        model_samsung[0][3] = -10.0; model_samsung[1][3] = 0.0; model_samsung[2][3] = 3.0 
        model_samsung[0][0] = model_samsung[1][1] = model_samsung[2][2] = 0.1          
        draw_obj_mtl(VAOs_samsung, shader, model_samsung)

        # Objeto 3 — TV
        set_lighting_uniforms(shader, is_interior=1, kd=0.5, ks=0.5, shininess=64.0)
        angle_y3  = math.radians(270); cy3, sy3  = math.cos(angle_y3), math.sin(angle_y3)
        rot_y3    = np.array([[ cy3, 0, sy3, 0], [  0,  1,   0, 0], [-sy3, 0, cy3, 0], [  0,  0,   0, 1]], dtype=np.float32)
        angle_z3  = math.radians(270); cz3, sz3  = math.cos(angle_z3), math.sin(angle_z3)
        rot_z3    = np.array([[cz3, -sz3, 0, 0], [sz3,  cz3, 0, 0], [  0,    0, 1, 0], [  0,    0, 0, 1]], dtype=np.float32)
        scale3    = np.diag([0.05, 0.05, 0.05, 1.0]).astype(np.float32); trans3    = np.identity(4, dtype=np.float32)
        trans3[0][3] = 15.0; trans3[1][3] = 3.5; trans3[2][3] = -10.0 
        model3    = trans3 @ rot_z3 @ rot_y3 @ scale3

        screen_keywords = ('screen', 'tela', 'display', 'monitor', 'glass', 'Screen', 'Tela', 'Display', 'Monitor', 'Glass', 'SCREEN')

        glUseProgram(shader)
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_TRUE, model3)
        for (VAO, n_verts, tex), (_, mat_name, _) in zip(VAOs_obj3, obj3_groups):
            if any(kw in mat_name for kw in screen_keywords): continue
            glBindVertexArray(VAO); glBindTexture(GL_TEXTURE_2D, tex); glDrawArrays(GL_TRIANGLES, 0, n_verts)

        if tv_on:
            glUseProgram(emissive_shader)
            glUniformMatrix4fv(glGetUniformLocation(emissive_shader, "view"),       1, GL_TRUE, view)
            glUniformMatrix4fv(glGetUniformLocation(emissive_shader, "projection"), 1, GL_TRUE, proj)
            glUniform1i( glGetUniformLocation(emissive_shader, "lightOn"),       1)
            glUniform3f( glGetUniformLocation(emissive_shader, "emissiveColor"),  0.85, 0.92, 1.0)
            glUniform1f( glGetUniformLocation(emissive_shader, "emissivePower"),  1.8)
            glUniformMatrix4fv(glGetUniformLocation(emissive_shader, "model"),   1, GL_TRUE, model3)
            for (VAO, n_verts, tex), (_, mat_name, _) in zip(VAOs_obj3, obj3_groups):
                if not any(kw in mat_name for kw in screen_keywords): continue
                glBindVertexArray(VAO); glBindTexture(GL_TEXTURE_2D, tex); glDrawArrays(GL_TRIANGLES, 0, n_verts)
        else:
            glUseProgram(shader)
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_TRUE, model3)
            for (VAO, n_verts, tex), (_, mat_name, _) in zip(VAOs_obj3, obj3_groups):
                if not any(kw in mat_name for kw in screen_keywords): continue
                glBindVertexArray(VAO); glBindTexture(GL_TEXTURE_2D, tex); glDrawArrays(GL_TRIANGLES, 0, n_verts)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()