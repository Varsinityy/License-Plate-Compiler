import numpy as np
from PIL import Image, ImageDraw, ImageFont
import ctypes

try:
    from pyopengltk import OpenGLFrame
    from OpenGL.GL import *
    from OpenGL.GL import shaders as glshaders
    from OpenGL.GLU import *
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False

import math

VERT_SHADER = """
#version 120
attribute vec3 aTangent;

varying vec3 vPosition;
varying vec3 vNormal;
varying vec2 vTexCoord;
varying mat3 vTBN;

void main() {
    vPosition = vec3(gl_ModelViewMatrix * gl_Vertex);
    vNormal = normalize(gl_NormalMatrix * gl_Normal);
    vTexCoord = gl_MultiTexCoord0.xy;

    vec3 T = normalize(gl_NormalMatrix * aTangent);
    vec3 N = vNormal;
    T = normalize(T - dot(T, N) * N);
    vec3 B = cross(N, T);
    vTBN = mat3(T, B, N);

    gl_Position = ftransform();
}
"""

FRAG_SHADER = """
#version 120
uniform sampler2D uDiffuse;
uniform sampler2D uNormal;
uniform int uHasDiffuse;
uniform int uHasNormal;

varying vec3 vPosition;
varying vec3 vNormal;
varying vec2 vTexCoord;
varying mat3 vTBN;

void main() {
    vec3 normal = normalize(vNormal);

    if (uHasNormal == 1) {
        vec3 mapNormal = texture2D(uNormal, vTexCoord).rgb;
        mapNormal = mapNormal * 2.0 - 1.0;
        normal = normalize(vTBN * mapNormal);
    }

    vec4 baseColor = vec4(0.8, 0.8, 0.8, 1.0);
    if (uHasDiffuse == 1) {
        baseColor = texture2D(uDiffuse, vTexCoord);
    }

    vec3 ambient = vec3(0.35);
    vec3 result = ambient * baseColor.rgb;

    vec3 lightDirs[3];
    vec3 lightColors[3];
    lightDirs[0] = normalize(vec3(0.3, 0.8, 1.0));
    lightColors[0] = vec3(0.8);
    lightDirs[1] = normalize(vec3(-0.6, 0.4, -0.3));
    lightColors[1] = vec3(0.35, 0.35, 0.4);
    lightDirs[2] = normalize(vec3(0.0, -0.5, -1.0));
    lightColors[2] = vec3(0.2, 0.2, 0.25);

    vec3 viewDir = normalize(-vPosition);

    for (int i = 0; i < 3; i++) {
        float diff = max(dot(normal, lightDirs[i]), 0.0);
        result += diff * lightColors[i] * baseColor.rgb;

        vec3 halfDir = normalize(lightDirs[i] + viewDir);
        float spec = pow(max(dot(normal, halfDir), 0.0), 64.0);
        result += spec * vec3(0.8) * lightColors[i];
    }

    gl_FragColor = vec4(result, baseColor.a);
}
"""


class Viewport3D(OpenGLFrame if HAS_OPENGL else object):
    def __init__(self, master, **kwargs):
        if not HAS_OPENGL:
            raise ImportError("PyOpenGL and pyopengltk are required for the 3D viewport")
        super().__init__(master, **kwargs)
        self.animate = 1
        self.rotX = 20.0
        self.rotY = 0.0
        self.panX = 0.0
        self.panY = 0.0
        self.zoom = 2.0
        self.targetX = 0.0
        self.targetY = 0.0
        self.targetZ = 0.0
        self.lastMouseX = 0
        self.lastMouseY = 0
        self.vertexCount = 0
        self.indexCount = 0
        self.diffuseTexId = 0
        self.normalTexId = 0
        self.hasDiffuse = False
        self.hasNormal = False
        self.hasModel = False
        self.vboVertices = 0
        self.vboNormals = 0
        self.vboUvs = 0
        self.vboTangents = 0
        self.eboIndices = 0
        self.bgColor = (0.25, 0.25, 0.27, 1.0)
        self._pendingModel = None
        self._pendingDiffuse = None
        self._pendingNormal = None
        self._cpuVertices = None
        self._cpuIndices = None
        self._meshGroups = []
        self._materialNames = []
        self._hiddenMaterialIds = set()
        self._hiddenMaterialNames = set()
        self._hiddenMeshNames = set()
        self._texturedMaterialIds = None
        self._texturedMaterialNames = None
        self._statusTextureText = ""
        self._statusNormalText = ""
        self._statusTextureId = 0
        self._statusNormalId = 0
        self._statusTextureSize = (0, 0)
        self._statusNormalSize = (0, 0)
        self._statusDirty = True
        self.shaderProgram = 0
        self.tangentAttrib = -1
        self._glInitDone = False
        self.bind("<ButtonPress-1>", self.onLeftPress)
        self.bind("<B1-Motion>", self.onLeftDrag)
        self.bind("<Double-Button-1>", self.onDoubleClick)
        self.bind("<ButtonPress-3>", self.onRightPress)
        self.bind("<B3-Motion>", self.onRightDrag)
        self.bind("<MouseWheel>", self.onScroll)
        self.bind("<ButtonPress-2>", self.onMiddlePress)
        self.bind("<B2-Motion>", self.onMiddleDrag)

    def initgl(self):
        glClearColor(*self.bgColor)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)

        try:
            vs = glshaders.compileShader(VERT_SHADER, GL_VERTEX_SHADER)
            fs = glshaders.compileShader(FRAG_SHADER, GL_FRAGMENT_SHADER)
            self.shaderProgram = glshaders.compileProgram(vs, fs)
            self.tangentAttrib = glGetAttribLocation(self.shaderProgram, "aTangent")
        except Exception as e:
            print(f"Shader compile error: {e}")
            self.shaderProgram = 0

        self._glInitDone = True

    def redraw(self):
        if self._pendingModel is not None:
            self._doUploadModel(self._pendingModel)
            self._pendingModel = None

        if self._pendingDiffuse is not None:
            self.diffuseTexId = self._uploadTexture(self._pendingDiffuse, self.diffuseTexId)
            self.hasDiffuse = True
            self._pendingDiffuse = None

        if self._pendingNormal is not None:
            self.normalTexId = self._uploadTexture(self._pendingNormal, self.normalTexId)
            self.hasNormal = True
            self._pendingNormal = None

        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 0 or h <= 0:
            return

        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = w / h
        gluPerspective(45.0, aspect, 0.01, 100.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClearColor(*self.bgColor)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glTranslatef(self.panX, self.panY, -self.zoom)
        glRotatef(self.rotX, 1.0, 0.0, 0.0)
        glRotatef(self.rotY, 0.0, 1.0, 0.0)
        glTranslatef(-self.targetX, -self.targetY, -self.targetZ)

        self.drawGrid()
        if self.hasModel:
            self.drawModel()
        self.drawStatusText(w, h)

    def updateGrid(self):
        step = 0.1
        gridSize = 100.0
            
        steps = int(gridSize / step)
        yPos = -0.1
        verts = []
        for i in range(-steps, steps + 1):
            pos = i * step
            verts.extend([pos, yPos, -gridSize, pos, yPos, gridSize])
            verts.extend([-gridSize, yPos, pos, gridSize, yPos, pos])
        
        verts_arr = np.array(verts, dtype=np.float32)
        
        if not hasattr(self, 'vboGrid'):
            self.vboGrid = glGenBuffers(1)
            
        glBindBuffer(GL_ARRAY_BUFFER, self.vboGrid)
        glBufferData(GL_ARRAY_BUFFER, verts_arr.nbytes, verts_arr, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self._gridVertexCount = len(verts_arr) // 3

    def drawGrid(self):
        glUseProgram(0)
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        
        if not hasattr(self, 'vboGrid'):
            self.updateGrid()
            
        glColor4f(0.18, 0.18, 0.22, 1.0)
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboGrid)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawArrays(GL_LINES, 0, self._gridVertexCount)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDisableClientState(GL_VERTEX_ARRAY)

    def drawModel(self):
        if self.shaderProgram:
            glUseProgram(self.shaderProgram)

            if self.hasDiffuse:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, self.diffuseTexId)
                glUniform1i(glGetUniformLocation(self.shaderProgram, "uDiffuse"), 0)
                glUniform1i(glGetUniformLocation(self.shaderProgram, "uHasDiffuse"), 1)
            else:
                glUniform1i(glGetUniformLocation(self.shaderProgram, "uHasDiffuse"), 0)

            if self.hasNormal:
                glActiveTexture(GL_TEXTURE1)
                glBindTexture(GL_TEXTURE_2D, self.normalTexId)
                glUniform1i(glGetUniformLocation(self.shaderProgram, "uNormal"), 1)
                glUniform1i(glGetUniformLocation(self.shaderProgram, "uHasNormal"), 1)
            else:
                glUniform1i(glGetUniformLocation(self.shaderProgram, "uHasNormal"), 0)
        else:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            if self.hasDiffuse:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.diffuseTexId)
            glColor4f(0.8, 0.8, 0.8, 1.0)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vboVertices)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vboNormals)
        glNormalPointer(GL_FLOAT, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, self.vboUvs)
        glTexCoordPointer(2, GL_FLOAT, 0, None)

        if self.shaderProgram and self.tangentAttrib >= 0 and self.vboTangents:
            glEnableVertexAttribArray(self.tangentAttrib)
            glBindBuffer(GL_ARRAY_BUFFER, self.vboTangents)
            glVertexAttribPointer(self.tangentAttrib, 3, GL_FLOAT, GL_FALSE, 0, None)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.eboIndices)

        if (
            self._texturedMaterialIds is None
            and self._texturedMaterialNames is None
            and not self._hiddenMaterialIds
            and not self._hiddenMaterialNames
            and not getattr(self, "_hiddenMeshNames", set())
        ):
            glDrawElements(GL_TRIANGLES, self.indexCount, GL_UNSIGNED_INT, None)
        else:
            texturedNames = self._texturedMaterialNames or set()
            for group in self._meshGroups:
                matName = self._materialName(group.materialId)
                if group.materialId in self._hiddenMaterialIds or matName in self._hiddenMaterialNames:
                    continue

                mesh_hidden = False
                if hasattr(self, "_hiddenMeshNames") and self._hiddenMeshNames:
                    mname = getattr(group, "meshName", "").lower()
                    for hname in self._hiddenMeshNames:
                        if hname in mname:
                            mesh_hidden = True
                            break
                if mesh_hidden:
                    continue

                useTexture = self.hasDiffuse and (
                    group.materialId in (self._texturedMaterialIds or set()) or matName in texturedNames
                )
                useNormal = self.hasNormal and (
                    group.materialId in (self._texturedMaterialIds or set()) or matName in texturedNames
                )

                if self.shaderProgram:
                    glUniform1i(glGetUniformLocation(self.shaderProgram, "uHasDiffuse"), 1 if useTexture else 0)
                    glUniform1i(glGetUniformLocation(self.shaderProgram, "uHasNormal"), 1 if useNormal else 0)
                else:
                    glActiveTexture(GL_TEXTURE0)
                    if useTexture:
                        glEnable(GL_TEXTURE_2D)
                        glBindTexture(GL_TEXTURE_2D, self.diffuseTexId)
                    else:
                        glDisable(GL_TEXTURE_2D)

                glDrawElements(
                    GL_TRIANGLES,
                    group.indexCount,
                    GL_UNSIGNED_INT,
                    ctypes.c_void_p(group.indexStart * np.dtype(np.uint32).itemsize)
                )

        if self.shaderProgram and self.tangentAttrib >= 0:
            glDisableVertexAttribArray(self.tangentAttrib)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glUseProgram(0)
        glDisable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)

    def uploadModel(self, parsedModel):
        self._pendingModel = parsedModel

    def setMaterialTextureRules(
        self,
        hiddenMaterialIds=None,
        hiddenMaterialNames=None,
        texturedMaterialIds=None,
        texturedMaterialNames=None,
        hiddenMeshNames=None
    ):
        self._hiddenMaterialIds = set(hiddenMaterialIds or [])
        self._hiddenMaterialNames = {name.lower() for name in (hiddenMaterialNames or [])}
        self._hiddenMeshNames = {name.lower() for name in (hiddenMeshNames or [])}
        if texturedMaterialIds is None:
            self._texturedMaterialIds = None
        else:
            self._texturedMaterialIds = set(texturedMaterialIds)
        if texturedMaterialNames is None:
            self._texturedMaterialNames = None
        else:
            self._texturedMaterialNames = {name.lower() for name in texturedMaterialNames}

    def setStatusText(self, textureText=None, normalText=None):
        if textureText is not None:
            self._statusTextureText = textureText
        if normalText is not None:
            self._statusNormalText = normalText
        self._statusDirty = True

    def _makeStatusTexture(self, text, existingId):
        if existingId:
            glDeleteTextures([existingId])
        if not text:
            return 0, (0, 0)

        font = ImageFont.load_default()
        bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=font)
        w = max(1, bbox[2] - bbox[0] + 2)
        h = max(1, bbox[3] - bbox[1] + 2)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((1 - bbox[0], 1 - bbox[1]), text, font=font, fill=(16, 185, 129, 255))
        data = np.array(img, dtype=np.uint8)

        texId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texId)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glBindTexture(GL_TEXTURE_2D, 0)
        return texId, (w, h)

    def _drawStatusTexture(self, texId, x, y, size):
        w, h = size
        if not texId or w <= 0 or h <= 0:
            return
        glBindTexture(GL_TEXTURE_2D, texId)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0); glVertex2f(x, y)
        glTexCoord2f(1.0, 1.0); glVertex2f(x + w, y)
        glTexCoord2f(1.0, 0.0); glVertex2f(x + w, y + h)
        glTexCoord2f(0.0, 0.0); glVertex2f(x, y + h)
        glEnd()

    def drawStatusText(self, viewportW, viewportH):
        if self._statusDirty:
            self._statusTextureId, self._statusTextureSize = self._makeStatusTexture(self._statusTextureText, self._statusTextureId)
            self._statusNormalId, self._statusNormalSize = self._makeStatusTexture(self._statusNormalText, self._statusNormalId)
            self._statusDirty = False

        if not self._statusTextureId and not self._statusNormalId:
            return

        glUseProgram(0)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, viewportW, 0, viewportH, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)

        pad = 10
        y = 8
        self._drawStatusTexture(self._statusTextureId, pad, y, self._statusTextureSize)
        normalW = self._statusNormalSize[0]
        self._drawStatusTexture(self._statusNormalId, viewportW - normalW - pad, y, self._statusNormalSize)

        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def _computeTangents(self, vertices, normals, uvs, indices):
        tangents = np.zeros_like(vertices)
        for i in range(0, len(indices), 3):
            i0, i1, i2 = indices[i], indices[i + 1], indices[i + 2]
            if i0 >= len(vertices) or i1 >= len(vertices) or i2 >= len(vertices):
                continue
            v0, v1, v2 = vertices[i0], vertices[i1], vertices[i2]
            uv0, uv1, uv2 = uvs[i0], uvs[i1], uvs[i2]

            edge1 = v1 - v0
            edge2 = v2 - v0
            dUV1 = uv1 - uv0
            dUV2 = uv2 - uv0

            denom = dUV1[0] * dUV2[1] - dUV2[0] * dUV1[1]
            if abs(denom) < 1e-8:
                continue
            f = 1.0 / denom

            t = np.array([
                f * (dUV2[1] * edge1[0] - dUV1[1] * edge2[0]),
                f * (dUV2[1] * edge1[1] - dUV1[1] * edge2[1]),
                f * (dUV2[1] * edge1[2] - dUV1[1] * edge2[2])
            ], dtype=np.float32)

            tangents[i0] += t
            tangents[i1] += t
            tangents[i2] += t

        for i in range(len(tangents)):
            n = normals[i]
            t = tangents[i]
            t = t - n * np.dot(n, t)
            length = np.linalg.norm(t)
            if length > 1e-6:
                tangents[i] = t / length
            else:
                tangents[i] = np.array([1, 0, 0], dtype=np.float32)

        return tangents

    def _doUploadModel(self, parsedModel):
        vertices = parsedModel.vertices.flatten()
        normals = parsedModel.normals.flatten()
        uvs = parsedModel.uvs.flatten()
        indices = parsedModel.indices

        tangents = self._computeTangents(
            parsedModel.vertices, parsedModel.normals, parsedModel.uvs, parsedModel.indices
        ).flatten()

        self._cpuVertices = parsedModel.vertices.copy()
        self._cpuIndices = parsedModel.indices.copy()

        self.vertexCount = len(parsedModel.vertices)
        self.indexCount = len(indices)
        self._meshGroups = getattr(parsedModel, "meshGroups", []) or []
        self._materialNames = getattr(parsedModel, "materialNames", []) or []

        if self.vboVertices:
            bufs = [self.vboVertices, self.vboNormals, self.vboUvs, self.eboIndices]
            if self.vboTangents:
                bufs.append(self.vboTangents)
            glDeleteBuffers(len(bufs), bufs)

        self.vboVertices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboVertices)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        self.vboNormals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboNormals)
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)

        self.vboUvs = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboUvs)
        glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_STATIC_DRAW)

        self.vboTangents = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboTangents)
        glBufferData(GL_ARRAY_BUFFER, tangents.nbytes, tangents, GL_STATIC_DRAW)

        self.eboIndices = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.eboIndices)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        self.hasModel = True

        minCoords = parsedModel.vertices.min(axis=0)
        maxCoords = parsedModel.vertices.max(axis=0)
        center = (minCoords + maxCoords) / 2.0
        self.modelExtent = float(np.linalg.norm(maxCoords - minCoords))
        extent = self.modelExtent

        self.targetX = float(center[0])
        self.targetY = float(center[1])
        self.targetZ = float(center[2])
        self.defaultTargetX = self.targetX
        self.defaultTargetY = self.targetY
        self.defaultTargetZ = self.targetZ
        self.zoom = float(extent * 1.2) if extent > 0.01 else 2.0
        self.panX = 0.0
        self.panY = 0.0
        self.rotX = 90.0
        self.rotY = 180.0
        self.updateGrid()

    def _materialName(self, materialId):
        if 0 <= materialId < len(self._materialNames):
            return self._materialNames[materialId].lower()
        return ""

    def setDiffuseTexture(self, pilImage):
        if pilImage is None:
            self.hasDiffuse = False
            return
        self._pendingDiffuse = pilImage

    def setNormalTexture(self, pilImage):
        if pilImage is None:
            self.hasNormal = False
            return
        self._pendingNormal = pilImage

    def _uploadTexture(self, pilImage, existingId):
        img = pilImage.convert("RGBA").transpose(Image.FLIP_TOP_BOTTOM)
        imgData = np.array(img, dtype=np.uint8)

        if existingId:
            glDeleteTextures([existingId])

        texId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texId)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, imgData)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        return texId

    def resetCamera(self):
        self.rotX = 90.0
        self.rotY = 180.0
        self.panX = 0.0
        self.panY = 0.0
        if hasattr(self, 'defaultTargetX'):
            self.targetX = self.defaultTargetX
            self.targetY = self.defaultTargetY
            self.targetZ = self.defaultTargetZ
        if hasattr(self, 'modelExtent') and self.modelExtent > 0.01:
            self.zoom = float(self.modelExtent * 1.2)
        else:
            self.zoom = 2.0

    def onLeftPress(self, event):
        self.lastMouseX = event.x
        self.lastMouseY = event.y

    def onLeftDrag(self, event):
        dx = event.x - self.lastMouseX
        dy = event.y - self.lastMouseY
        self.rotY += dx * 0.5
        self.rotX += dy * 0.5
        self.lastMouseX = event.x
        self.lastMouseY = event.y

    def onDoubleClick(self, event):
        if not self.hasModel or self._cpuVertices is None:
            return
        hitPoint = self._raycast(event.x, event.y)
        if hitPoint is not None:
            self.targetX = float(hitPoint[0])
            self.targetY = float(hitPoint[1])
            self.targetZ = float(hitPoint[2])

    def _raycast(self, screenX, screenY):
        try:
            w = self.winfo_width()
            h = self.winfo_height()
            viewport = glGetIntegerv(GL_VIEWPORT)
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)

            winY = h - screenY

            nearPoint = gluUnProject(screenX, winY, 0.0, modelview, projection, viewport)
            farPoint = gluUnProject(screenX, winY, 1.0, modelview, projection, viewport)

            rayOrigin = np.array(nearPoint, dtype=np.float64)
            rayDir = np.array(farPoint, dtype=np.float64) - rayOrigin
            rayLen = np.linalg.norm(rayDir)
            if rayLen < 1e-10:
                return None
            rayDir /= rayLen

            closestT = float('inf')
            closestPoint = None
            verts = self._cpuVertices
            indices = self._cpuIndices

            for i in range(0, len(indices), 3):
                i0, i1, i2 = indices[i], indices[i + 1], indices[i + 2]
                if i0 >= len(verts) or i1 >= len(verts) or i2 >= len(verts):
                    continue
                v0 = verts[i0].astype(np.float64)
                v1 = verts[i1].astype(np.float64)
                v2 = verts[i2].astype(np.float64)

                edge1 = v1 - v0
                edge2 = v2 - v0
                pvec = np.cross(rayDir, edge2)
                det = np.dot(edge1, pvec)

                if abs(det) < 1e-10:
                    continue

                invDet = 1.0 / det
                tvec = rayOrigin - v0
                u = np.dot(tvec, pvec) * invDet
                if u < 0.0 or u > 1.0:
                    continue

                qvec = np.cross(tvec, edge1)
                v = np.dot(rayDir, qvec) * invDet
                if v < 0.0 or u + v > 1.0:
                    continue

                t = np.dot(edge2, qvec) * invDet
                if t > 0 and t < closestT:
                    closestT = t
                    closestPoint = rayOrigin + rayDir * t

            return closestPoint
        except Exception:
            return None

    def onRightPress(self, event):
        self.lastMouseX = event.x
        self.lastMouseY = event.y

    def onRightDrag(self, event):
        dx = event.x - self.lastMouseX
        dy = event.y - self.lastMouseY
        self.panX += dx * 0.003 * self.zoom
        self.panY -= dy * 0.003 * self.zoom
        self.lastMouseX = event.x
        self.lastMouseY = event.y

    def onMiddlePress(self, event):
        self.lastMouseX = event.x
        self.lastMouseY = event.y

    def onMiddleDrag(self, event):
        dx = event.x - self.lastMouseX
        dy = event.y - self.lastMouseY
        self.panX += dx * 0.003 * self.zoom
        self.panY -= dy * 0.003 * self.zoom
        self.lastMouseX = event.x
        self.lastMouseY = event.y

    def onScroll(self, event):
        if event.delta > 0:
            self.zoom *= 0.9
        else:
            self.zoom *= 1.1
        self.zoom = max(0.0001, min(100.0, self.zoom))
