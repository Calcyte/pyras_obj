import pygame
import platform as pla
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo
import os
oppath = os.path.dirname(os.path.realpath(__file__))
runos = pla.system()
if runos == "Windows":
    split = "\""
else:
    split="/"
def load_texture(filename):
    texpath=oppath+split+"assets"+split+"bucket"+split+filename
    if not os.path.exists(texpath):
        print("Texture file " + filename + " not found in the bucket.")
        return None
    surface = pygame.image.load(texpath) 
    width, height = surface.get_size()
    image_data = pygame.image.tostring(surface, "RGBA", True)
    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)  
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR) 
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    return texid
def collect_objvert(reqass="Complex"):
    filepath = oppath + split + "assets" + split + "models" + split + reqass + ".obj"
    faces = []
    objverts = []
    mtllis = []
    mat = None
    texturecoords = []
    normals = []
    def new_material(name):
        return [name, [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], 1.0, 1.0, 1.0, 1, None, None, [None, None, None]]
    with open(filepath, "r") as assfil:
        for line in assfil:
            if line.startswith("mtllib "):
                line = line.strip()
                mtllib = open(oppath + split + "assets" + split + "models" + split + line[7:], "r")
                for mline in mtllib:
                    if mline.startswith("newmtl "):
                        mtllis.append(new_material(mline[7:].strip()))
                    elif mline.startswith("Ka "):
                        tmp = mline[3:].split()
                        for i in range(len(tmp)):
                            tmp[i] = float(tmp[i])
                        mtllis[len(mtllis)-1][1] = tmp
                        tmp = mline[3:].split()
                        for i in range(len(tmp)):
                            tmp[i] = float(tmp[i])
                        mtllis[len(mtllis)-1][2] = tmp
                    elif mline.startswith("Ks "):
                        tmp = mline[3:].split()
                        for i in range(len(tmp)):
                            tmp[i] = float(tmp[i]) 
                        mtllis[len(mtllis)-1][3] = tmp
                    elif mline.startswith("d "):
                        mtllis[len(mtllis)-1][4] = float(mline[2:].strip())
                    elif mline.startswith("Tr "):
                        mtllis[len(mtllis)-1][5] = float(mline[3:].strip())
                    elif mline.startswith("Ns "):
                        if float(mline[3:].strip()) > 128:
                            mtllis[len(mtllis)-1][6] = float(128)
                        else:
                            mtllis[len(mtllis)-1][6] = float(mline[3:].strip())
                    elif mline.startswith("illum "):
                        mtllis[len(mtllis)-1][7] = int(mline[6:].strip())
                    elif mline.startswith("map_Kd "):
                        mtllis[len(mtllis)-1][8] = load_texture(mline[7:].strip()) if mline[7:].strip() != "" else 0
                mtllib.close()
            if line.startswith("usemtl "):
                if mat is not None and faces:
                    mtllis[mat][9] = faces
                    mat = None
                mat_name = line[7:].strip()
                for i in range(len(mtllis)):
                    if mtllis[i][0] == mat_name:
                        mat = i
                faces = []
            if line.startswith("vt "):
                parts = line[3:].split()
                if float(parts[0]) > 1:
                    parts[0] = 1
                if float(parts[0]) < 0:
                    parts[0] = 0
                if float(parts[1]) > 1:
                    parts[1] = 1
                if float(parts[1]) < 0:
                    parts[1] = 0
                texturecoords.append([float(parts[0]), float(parts[1])])
            if line.startswith("vn "):
                parts = line[3:].split()
                normals.append([float(parts[0]), float(parts[1]), float(parts[2])]) 
            if line.startswith("v "):
                parts = line[2:].split()
                objverts.append([float(parts[0]), float(parts[1]), float(parts[2])])
            if line.startswith("f "):
                parts = line[2:].strip().split()
                if parts:
                    face = []
                    for p in parts:
                        indices = p.split("/")
                        vert_idx = int(indices[0]) - 1 if len(indices) > 0 and indices[0] != '' else None
                        tex_idx = int(indices[1]) - 1 if len(indices) > 1 and indices[1] != '' else None
                        norm_idx = int(indices[2]) - 1 if len(indices) > 2 and indices[2] != '' else None
                        face.append([vert_idx, tex_idx, norm_idx])
                    if len(face) > 3:
                        for i in range(1, len(face) - 1):
                            faces.append([face[0], face[i], face[i + 1]])
                    else:
                        faces.append(face)
    if mat is not None and faces:
        mtllis[mat][9] = faces
    return mtllis, objverts, texturecoords, normals
def setup_vbo(mtllis, verts, texcoo, norms):
    for materials in mtllis:
        if materials[9] is None or len(materials[9]) == 0:
            continue
        texcor = []
        triangle = []
        norm = []
        if len(materials[1]) != 4:
            materials[1].append(float(materials[4]))
            materials[2].append(float(materials[4]))
            materials[3].append(float(materials[4]))
        for face in materials[9]:
            if len(face) == 3:
                sad = []
                texsad = []
                norsad = []
                for v in face:
                    v_idx = v[0] if v[0] is not None else 0
                    if texcoo and v[1] is not None and v[1] < len(texcoo):
                        texsad.append(texcoo[v[1]])
                    else:
                        texsad.append([0.0, 0.0])
                    if norms and v[2] is not None and v[2] < len(norms):
                        norsad.append(norms[v[2]])
                    else:
                        norsad.append([0.0, 0.0, 1.0])
                    sad.append(verts[v_idx])
                triangle.extend(sad)
                texcor.extend(texsad)
                norm.extend(norsad)
        texture_array = np.array(texcor, dtype=np.float32)
        triangle_array = np.array(triangle, dtype=np.float32)
        normal_array = np.array(norm, dtype=np.float32)
        materials[10][0] = vbo.VBO(triangle_array)
        materials[10][1] = vbo.VBO(texture_array)
        materials[10][2] = vbo.VBO(normal_array)
    return mtllis
def render_vbo(mtllis):
    for materials in mtllis:
        if materials[10][0] is not None:
            glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, materials[1])
            glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, materials[2])
            glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, materials[3])
            glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, materials[6])
            materials[10][0].bind()
            glEnableClientState(GL_VERTEX_ARRAY)
            glVertexPointer(3, GL_FLOAT, 0, materials[10][0])
            if materials[10][1] is not None and materials[8]:
                materials[10][1].bind()
                glEnableClientState(GL_TEXTURE_COORD_ARRAY)
                glBindTexture(GL_TEXTURE_2D, materials[8])
                glTexCoordPointer(2, GL_FLOAT, 0, materials[10][1])
            if materials[10][2] is not None:
                materials[10][2].bind()
                glEnableClientState(GL_NORMAL_ARRAY)
                glNormalPointer(GL_FLOAT, 0, materials[10][2])
            glDrawArrays(GL_TRIANGLES, 0, len(materials[10][0]))
            if len(materials[10]) > 2 and materials[10][2] is not None:
                glDisableClientState(GL_NORMAL_ARRAY)
                materials[10][2].unbind()
            if materials[10][1] is not None and materials[8]:
                glDisableClientState(GL_TEXTURE_COORD_ARRAY)
                materials[10][1].unbind()
            glDisableClientState(GL_VERTEX_ARRAY)
            materials[10][0].unbind()
def main():
    pygame.init()
    displayinfo = pygame.display.Info()
    pygame.display.set_mode((0, 0), DOUBLEBUF | OPENGL | FULLSCREEN)
    pygame.display.set_caption("RAS1")
    mtllis, vertices, texcoo, normals = collect_objvert()
    vbo_obj = setup_vbo(mtllis, vertices, texcoo, normals)
    cam_pos = [1000.0, 1.0, 0.0]
    cam_yaw = 0.0
    cam_pitch = 0.0
    dc = [displayinfo.current_w // 2, displayinfo.current_h // 2]
    pygame.mouse.set_pos(dc) 
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    glClearColor(0.2, 0.2, 0.3, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 10000, 40000, 0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.7, 0.7, 0.7, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glShadeModel(GL_SMOOTH)
    glEnable(GL_TEXTURE_2D)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (displayinfo.current_w / displayinfo.current_h), 0.1, 100000)
    glMatrixMode(GL_MODELVIEW)
    loc = [10, 1, 0]
    gluLookAt(loc[0], loc[1], loc[2], 0, 0, 0, 0, 1, 0)
    matrix=glGetFloatv(GL_MODELVIEW_MATRIX)
    glLoadIdentity()
    uda=0.0
    while True:
        dt = clock.tick(9999999) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.mouse.set_pos(dc)
        keys = pygame.key.get_pressed()
        mos = pygame.mouse.get_rel()
        cam_yaw += mos[0] * 0.1
        cam_pitch -= mos[1] * 0.1
        cam_pitch = max(-89, min(89, cam_pitch))
        yaw_rad = np.radians(cam_yaw)
        pitch_rad = np.radians(cam_pitch)
        forward = [np.cos(pitch_rad) * np.sin(yaw_rad), np.sin(pitch_rad), -np.cos(pitch_rad) * np.cos(yaw_rad)]
        right = [np.sin(yaw_rad - np.pi/2), 0, -np.cos(yaw_rad - np.pi/2)]
        speed = 100.0 * dt
        if keys[pygame.K_w]:
            cam_pos[0] += forward[0] * speed
            cam_pos[1] += forward[1] * speed
            cam_pos[2] += forward[2] * speed
        if keys[pygame.K_s]:
            cam_pos[0] -= forward[0] * speed
            cam_pos[1] -= forward[1] * speed
            cam_pos[2] -= forward[2] * speed
        if keys[pygame.K_a]:
            cam_pos[0] += right[0] * speed
            cam_pos[2] += right[2] * speed
        if keys[pygame.K_d ]:
            cam_pos[0] -= right[0] * speed
            cam_pos[2] -= right[2] * speed
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        look_x = cam_pos[0] + forward[0]
        look_y = cam_pos[1] + forward[1]
        look_z = cam_pos[2] + forward[2]
        gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2], look_x, look_y, look_z, 0, 1, 0)
        glLightfv(GL_LIGHT0, GL_POSITION, (0, 10000, 40000, 0))
        render_vbo(vbo_obj) 
        pygame.display.flip()
main()
