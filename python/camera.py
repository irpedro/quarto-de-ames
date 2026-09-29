import numpy as np
import math

def create_perspective_matrix(fov_deg, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_deg) / 2.0)
    mat = np.zeros((4, 4), dtype=np.float32)
    mat[0, 0] = f / aspect
    mat[1, 1] = f
    mat[2, 2] = (far + near) / (near - far)
    # CORREÇÃO: Os índices corretos para a divisão de perspectiva no OpenGL
    mat[2, 3] = (2.0 * far * near) / (near - far) 
    mat[3, 2] = -1.0                              
    return mat


def create_lookat_matrix(eye, target, up):
    f = target - eye
    f = f / np.linalg.norm(f)
    s = np.cross(f, up)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)
    
    mat = np.identity(4, dtype=np.float32)
    mat[0, :3] = s
    mat[1, :3] = u
    mat[2, :3] = -f
    mat[0, 3] = -np.dot(s, eye)
    mat[1, 3] = -np.dot(u, eye)
    mat[2, 3] =  np.dot(f, eye)
    return mat
