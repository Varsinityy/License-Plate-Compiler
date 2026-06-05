import io
import math
import os
import struct
from collections import defaultdict
import numpy as np


class BinaryStream:
    def __init__(self, buffer):
        if isinstance(buffer, memoryview):
            self._stream = io.BytesIO(buffer)
        elif isinstance(buffer, (bytes, bytearray)):
            self._stream = io.BytesIO(buffer)
        else:
            self._stream = io.BytesIO(bytes(buffer))
        self._buffer = self._stream.getbuffer()

    def __getitem__(self, key):
        return self._buffer[key]

    def tell(self):
        return self._stream.tell()

    def seek(self, offset, whence=0):
        return self._stream.seek(offset, whence)

    def read(self, size=None):
        return self._stream.read(size)

    def readString(self):
        length = self.readU32()
        return self._stream.read(length).decode("utf-8")

    def read7bitString(self):
        length = self.read7bit()
        return self._stream.read(length).decode("utf-8")

    def readS16(self):
        v = self._stream.read(2)
        if not v or len(v) < 2:
            return None
        return struct.unpack('h', v)[0]

    def readU8(self):
        v = self._stream.read(1)
        if not v:
            return None
        return struct.unpack('B', v)[0]

    def readU16(self):
        v = self._stream.read(2)
        if not v or len(v) < 2:
            return None
        return struct.unpack('H', v)[0]

    def readS32(self):
        v = self._stream.read(4)
        if not v or len(v) < 4:
            return None
        return struct.unpack('i', v)[0]

    def readU32(self):
        v = self._stream.read(4)
        if not v or len(v) < 4:
            return None
        return struct.unpack('I', v)[0]

    def readF16(self):
        v = self._stream.read(2)
        if not v or len(v) < 2:
            return None
        return struct.unpack('e', v)[0]

    def readF32(self):
        v = self._stream.read(4)
        if not v or len(v) < 4:
            return None
        return struct.unpack('f', v)[0]

    def readSn16(self):
        return self.readS16() / 32767

    def readUn8(self):
        return self.readU8() / 255

    def readUn16(self):
        return self.readU16() / 65535

    def read7bit(self):
        value = 0
        shift = 0
        while True:
            valueByte = self.readU8()
            value |= (valueByte & 0x7F) << shift
            shift += 7
            if valueByte & 0x80 == 0:
                break
        return value


class Tag:
    Grub = 0x47727562
    Id = 0x49642020
    Name = 0x4E616D65
    TXCH = 0x54584348
    Modl = 0x4D6F646C
    Skel = 0x536B656C
    MatI = 0x4D617449
    Mesh = 0x4D657368
    VLay = 0x564C6179
    IndB = 0x496E6442
    VerB = 0x56657242
    MBuf = 0x4D427566


class Version:
    def __init__(self):
        self.major = 0
        self.minor = 0

    def deserialize(self, stream):
        self.major = stream.readU8()
        self.minor = stream.readU8()

    def isAtLeast(self, major, minor):
        return self.major > major or self.major == major and self.minor >= minor

    def isAtMost(self, major, minor):
        return self.major < major or self.major == major and self.minor <= minor


class Metadata:
    def __init__(self):
        self.tag = 0
        self.version = 0

    def deserialize(self, stream):
        self.tag = stream.readU32()
        versionAndSize = stream.readU16()
        self.version = versionAndSize & 0xF
        size = versionAndSize >> 4
        offset = stream.readU16()
        self.stream = BinaryStream(stream[offset: offset + size])

    def readString(self):
        return self.stream.read().decode('utf-8')

    def readS32(self):
        return self.stream.readS32()


class Blob:
    def __init__(self):
        self.tag = 0
        self.version = Version()
        self.metadataLength = 0
        self.metadataOffset = 0
        self.dataOffset = 0
        self.dataSize = 0

    def deserialize(self, stream):
        self.tag = stream.readU32()
        self.version.deserialize(stream)
        self.metadataLength = stream.readU16()
        self.metadataOffset = stream.readU32()
        self.dataOffset = stream.readU32()
        self.dataSize = stream.readU32()
        stream.seek(4, os.SEEK_CUR)
        self.metadata = {}
        for i in range(self.metadataLength):
            metadata = Metadata()
            metadata.deserialize(BinaryStream(stream[self.metadataOffset + i * 8:]))
            self.metadata[metadata.tag] = metadata
        self.stream = BinaryStream(stream[self.dataOffset: self.dataOffset + self.dataSize])


class Bundle:
    def __init__(self):
        self.tag = 0
        self.version = Version()
        self.blobsLength = 0
        self.blobs = defaultdict(list)

    def deserialize(self, stream):
        self.tag = stream.readU32()
        if self.tag != Tag.Grub:
            raise ValueError("Not a valid Grub bundle")
        self.version.deserialize(stream)
        self.blobsLength = stream.readU16()
        stream.seek(4 * 2, os.SEEK_CUR)
        if self.version.isAtLeast(1, 1):
            self.blobsLength = stream.readU32()
        for _ in range(self.blobsLength):
            blob = Blob()
            blob.deserialize(stream)
            self.blobs[blob.tag].append(blob)


class Model:
    def __init__(self):
        self.meshesLength = 0
        self.buffersLength = 0
        self.vertexLayoutsLength = 0
        self.materialsLength = 0
        self.levelsOfDetail = 0
        self.decompressFlags = 0

    def deserialize(self, blob):
        stream = blob.stream
        self.meshesLength = stream.readS16()
        self.buffersLength = stream.readS16()
        self.vertexLayoutsLength = stream.readS16()
        self.materialsLength = stream.readS16()
        stream.seek(4, os.SEEK_CUR)
        self.levelsOfDetail = stream.readU16()
        if blob.version.isAtLeast(1, 2):
            self.decompressFlags = stream.readU8()


class D3D12InputElementDesc:
    def __init__(self):
        self.semanticName = ""
        self.semanticIndex = 0
        self.inputSlot = 0
        self.format = 0


class VertexLayout:
    def __init__(self):
        self.elementNamesLength = 0
        self.elementNames = None
        self.elementsLength = 0
        self.elements = defaultdict(D3D12InputElementDesc)

    def deserialize(self, stream):
        self.elementNamesLength = stream.readU16()
        self.elementNames = [None] * self.elementNamesLength
        for i in range(self.elementNamesLength):
            self.elementNames[i] = stream.readString()
        self.elementsLength = stream.readU16()
        for i in range(self.elementsLength):
            semanticName = self.elementNames[stream.readU16()]
            semanticIndex = stream.readU16()
            element = self.elements[semanticName + str(semanticIndex)]
            element.inputSlot = stream.readU16()
            stream.seek(2, os.SEEK_CUR)
            element.format = stream.readU32()
            stream.seek(4 * 2, os.SEEK_CUR)


class ModelBuffer:
    def __init__(self):
        self.length = 0
        self.size = 0
        self.stride = 0
        self.format = 0

    def deserialize(self, blob):
        self.length = blob.stream.readU32()
        self.size = blob.stream.readU32()
        self.stride = blob.stream.readU16()
        blob.stream.seek(1 + 1, os.SEEK_CUR)
        if blob.version.isAtLeast(1, 0):
            self.format = blob.stream.readU32()
            self.stream = blob.stream[0x10: 0x10 + self.size]
        else:
            self.stream = blob.stream[0xC: 0xC + self.size]


class MeshVertexBufferIndex:
    def __init__(self):
        self.id = 0
        self.stride = 0
        self.offset = 0


class MeshData:
    def __init__(self):
        self.materialId = 0
        self.boneIndex = 0
        self.levelsOfDetail = 0
        self.renderPass = 0
        self.skinningElementsCount = 0
        self.morphWeightsCount = 0
        self.indexBufferId = 0
        self.startIndexLocation = 0
        self.baseVertexLocation = 0
        self.indexCount = 0
        self.uvTransforms = [None] * 5
        self.scale = [1, 1, 1, 1]
        self.translate = [0, 0, 0, 0]
        self.name = ""

    def deserialize(self, blob):
        self.name = blob.metadata[Tag.Name].readString()
        self.materialId = blob.stream.readS16()
        if blob.version.isAtLeast(1, 9):
            self.materialId = blob.stream.readS16()
            blob.stream.seek(2 * 2, os.SEEK_CUR)
        self.boneIndex = blob.stream.readS16()
        self.levelsOfDetail = blob.stream.readU16()
        blob.stream.seek(2, os.SEEK_CUR)
        self.renderPass = blob.stream.readU16()
        blob.stream.seek(1, os.SEEK_CUR)
        if blob.version.isAtLeast(1, 2):
            self.skinningElementsCount = blob.stream.readU8()
            self.morphWeightsCount = blob.stream.readU8()
        if blob.version.isAtLeast(1, 3):
            blob.stream.seek(1, os.SEEK_CUR)
        blob.stream.seek(1 + 2, os.SEEK_CUR)
        self.indexBufferId = blob.stream.readS32()
        blob.stream.seek(4, os.SEEK_CUR)
        self.startIndexLocation = blob.stream.readS32()
        self.baseVertexLocation = blob.stream.readS32()
        self.indexCount = blob.stream.readU32()
        blob.stream.seek(4, os.SEEK_CUR)
        if blob.version.isAtLeast(1, 6):
            blob.stream.seek(4 + 4, os.SEEK_CUR)
        self.vertexLayoutId = blob.stream.readU32()
        self.vertexBufferIndicesLength = blob.stream.readU32()
        self.vertexBufferIndices = [None] * self.vertexBufferIndicesLength
        for i in range(self.vertexBufferIndicesLength):
            vbi = MeshVertexBufferIndex()
            vbi.id = blob.stream.readS32()
            inputSlot = blob.stream.readS32()
            vbi.stride = blob.stream.readS32()
            vbi.offset = blob.stream.readS32()
            self.vertexBufferIndices[inputSlot] = vbi
        if blob.version.isAtLeast(1, 4):
            self.morphDataBufferId = blob.stream.readS32()
            self.skinningDataBufferId = blob.stream.readS32()
        self.constantBufferIndicesLength = blob.stream.readU32()
        if blob.version.isAtLeast(1, 1):
            blob.stream.seek(4, os.SEEK_CUR)
        if blob.version.isAtLeast(1, 5):
            for i in range(5):
                self.uvTransforms[i] = (
                    (blob.stream.readF32(), blob.stream.readF32()),
                    (blob.stream.readF32(), blob.stream.readF32())
                )
        if blob.version.isAtLeast(1, 8):
            self.scale = [blob.stream.readF32(), blob.stream.readF32(), blob.stream.readF32(), blob.stream.readF32()]
            self.translate = [blob.stream.readF32(), blob.stream.readF32(), blob.stream.readF32(), blob.stream.readF32()]


class Bone:
    def __init__(self):
        self.name = ""
        self.transform = [[1 if i == j else 0 for i in range(4)] for j in range(4)]

    def deserialize(self, blob):
        nameLength = blob.stream.readU32()
        self.name = blob.stream.read(nameLength).decode("utf-8")
        self.parentIndex = blob.stream.readS16()
        self.childIndex = blob.stream.readS16()
        self.nextIndex = blob.stream.readS16()
        for j in range(4):
            for i in range(4):
                self.transform[j][i] = blob.stream.readF32()


class Skeleton:
    def __init__(self):
        self.bonesLength = 0
        self.bones = []

    def deserialize(self, blob):
        self.bonesLength = blob.stream.readU16()
        self.bones = [Bone() for _ in range(self.bonesLength)]
        transform = [[0 for _ in range(4)] for _ in range(4)]
        for bone in self.bones:
            bone.deserialize(blob)
            if bone.parentIndex != -1:
                tr = self.bones[bone.parentIndex].transform
                for j in range(4):
                    for i in range(4):
                        transform[j][i] = 0
                for i in range(4):
                    for j in range(4):
                        for k in range(4):
                            transform[i][j] += bone.transform[i][k] * tr[k][j]
                bone.transform = [row[:] for row in transform]


class VertexLayoutElement:
    def __init__(self):
        self.stream = None
        self.advance = 0
        self.format = -1


class MeshGroup:
    def __init__(self, indexStart, indexCount, materialId, meshName=""):
        self.indexStart = indexStart
        self.indexCount = indexCount
        self.materialId = materialId
        self.meshName = meshName


class ParsedModel:
    def __init__(self):
        self.vertices = None
        self.normals = None
        self.uvs = None
        self.indices = None
        self.meshName = ""
        self.meshGroups = []
        self.materialNames = []  # list of lowercased material name strings, indexed by materialId

def parseModelbin(filepath, requestedLod=1, requestedRenderPass=0xFFFF, skipMeshes=1, onlyMaterialIds=None):
    with open(filepath, "rb") as f:
        data = f.read()
    s = BinaryStream(memoryview(data))

    bundle = Bundle()
    bundle.deserialize(s)

    modelBlobs = bundle.blobs[Tag.Modl]
    if not modelBlobs:
        raise ValueError("No Modl blob found")
    modelBlob = modelBlobs[0]
    model = Model()
    model.deserialize(modelBlob)

    skelBlobs = bundle.blobs[Tag.Skel]
    skeleton = Skeleton()
    if skelBlobs:
        skeleton.deserialize(skelBlobs[0])

    vlayBlobs = bundle.blobs[Tag.VLay]
    vertexLayouts = [VertexLayout() for _ in range(len(vlayBlobs))]
    for vl, vlBlob in zip(vertexLayouts, vlayBlobs):
        vl.deserialize(vlBlob.stream)

    indBBlobs = bundle.blobs[Tag.IndB]
    if not indBBlobs:
        raise ValueError("No IndB blob found")
    indexBuffer = ModelBuffer()
    indexBuffer.deserialize(indBBlobs[0])

    verBBlobs = bundle.blobs[Tag.VerB]
    maxVbId = max((vb.metadata[Tag.Id].readS32() for vb in verBBlobs), default=-1)
    for vb in verBBlobs:
        vb.metadata[Tag.Id].stream.seek(0)
    vertexBuffers = [ModelBuffer() for _ in range(maxVbId + 2)]
    for vbBlob in verBBlobs:
        vertexBuffers[vbBlob.metadata[Tag.Id].readS32() + 1].deserialize(vbBlob)

    matIBlobs = bundle.blobs[Tag.MatI]
    materialNamesById = {}
    for matBlob in matIBlobs:
        materialId = matBlob.metadata[Tag.Id].readS32() if Tag.Id in matBlob.metadata else len(materialNamesById)
        if Tag.Name in matBlob.metadata:
            materialNamesById[materialId] = matBlob.metadata[Tag.Name].readString().lower()
        else:
            materialNamesById[materialId] = ""
    maxMaterialId = max(materialNamesById.keys(), default=-1)
    materialNames = [""] * (maxMaterialId + 1)
    for materialId, materialName in materialNamesById.items():
        if materialId >= 0:
            materialNames[materialId] = materialName

    meshBlobs = bundle.blobs[Tag.Mesh]
    meshes = [MeshData() for _ in range(len(meshBlobs))]
    for mesh, meshBlob in zip(meshes, meshBlobs):
        mesh.deserialize(meshBlob)

    allVerts = []
    allNorms = []
    allUvs = []
    allIndices = []
    meshGroupList = []
    vertexOffset = 0

    for meshIdx, mesh in enumerate(meshes):
        if mesh.levelsOfDetail & requestedLod == 0:
            continue
        meshNameLower = mesh.name.lower()
        if "atlas" in meshNameLower:
            continue
        if meshIdx < skipMeshes and len(meshes) > skipMeshes:
            continue
        if onlyMaterialIds is not None and mesh.materialId not in onlyMaterialIds:
            continue

        drawIndices = [0] * mesh.indexCount
        vertexIdMin = 0xFFFFFFFF
        vertexIdMax = 0
        idxStream = BinaryStream(
            indexBuffer.stream[mesh.startIndexLocation * indexBuffer.stride:
                               (mesh.startIndexLocation + mesh.indexCount) * indexBuffer.stride]
        )
        for i in range(mesh.indexCount):
            if indexBuffer.stride == 4:
                vertexId = idxStream.readU32()
            else:
                vertexId = idxStream.readU16()
            if vertexIdMax < vertexId:
                vertexIdMax = vertexId
            if vertexIdMin > vertexId:
                vertexIdMin = vertexId
            drawIndices[i] = vertexId

        faces = []
        for i in range(mesh.indexCount // 3):
            j = i * 3
            faces.append((
                drawIndices[j] - vertexIdMin,
                drawIndices[j + 2] - vertexIdMin,
                drawIndices[j + 1] - vertexIdMin
            ))

        vertexCount = vertexIdMax - vertexIdMin + 1
        verts = [(0, 0, 0)] * vertexCount
        norms = [(0, 0, 0)] * vertexCount
        uvs = [(0, 0)] * vertexCount

        vertexBufferOffsets = [0 for _ in range(mesh.vertexBufferIndicesLength)]

        elements = defaultdict(VertexLayoutElement)
        for semanticName, vlElemDesc in vertexLayouts[mesh.vertexLayoutId].elements.items():
            vbi = mesh.vertexBufferIndices[vlElemDesc.inputSlot]
            vb = vertexBuffers[vbi.id + 1]

            element = elements[semanticName]
            startByte = vbi.offset + (vertexIdMin + mesh.baseVertexLocation) * vb.stride + vertexBufferOffsets[vlElemDesc.inputSlot]
            endByte = vbi.offset + (vertexIdMax + mesh.baseVertexLocation + 1) * vb.stride + vertexBufferOffsets[vlElemDesc.inputSlot]
            element.stream = BinaryStream(vb.stream[startByte:endByte])
            element.format = vlElemDesc.format
            element.advance = vb.stride

            if vlElemDesc.format == 6:
                vertexBufferOffsets[vlElemDesc.inputSlot] += 12
            elif vlElemDesc.format in (10, 13):
                vertexBufferOffsets[vlElemDesc.inputSlot] += 8
            elif vlElemDesc.format in (24, 28, 35, 37):
                vertexBufferOffsets[vlElemDesc.inputSlot] += 4

        position0 = elements["POSITION0"]
        if position0.format == 13:
            position0.advance -= 8
        elif position0.format == 6:
            position0.advance -= 12

        normal0 = elements["NORMAL0"]
        if normal0.format == 37:
            normal0.advance -= 4
        elif normal0.format == 10:
            normal0.advance -= 6

        texcoord0 = elements["TEXCOORD0"]
        if texcoord0.format == 35:
            texcoord0.advance -= 4

        boneTransform = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        if skeleton.bones and mesh.boneIndex < len(skeleton.bones):
            boneTransform = skeleton.bones[mesh.boneIndex].transform

        uvTransform = mesh.uvTransforms[0] if mesh.uvTransforms[0] else ((0, 1), (0, 1))

        n = [1, 0, 0]
        for idx in range(vertexCount):
            if texcoord0.format == 35:
                t = [texcoord0.stream.readUn16(), texcoord0.stream.readUn16()]
                t[0] = t[0] * uvTransform[0][1] + uvTransform[0][0]
                t[1] = t[1] * uvTransform[1][1] + uvTransform[1][0]
                uvs[idx] = (t[0], 1 - t[1])
                texcoord0.stream.seek(texcoord0.advance, os.SEEK_CUR)

            if position0.format == 13:
                v = [
                    position0.stream.readSn16() * mesh.scale[0] + mesh.translate[0],
                    position0.stream.readSn16() * mesh.scale[1] + mesh.translate[1],
                    position0.stream.readSn16() * mesh.scale[2] + mesh.translate[2]
                ]
                vW = position0.stream.readSn16()
            elif position0.format == 6:
                v = [position0.stream.readF32(), position0.stream.readF32(), position0.stream.readF32()]
                vW = 0
            else:
                v = [0, 0, 0]
                vW = 0
            position0.stream.seek(position0.advance, os.SEEK_CUR)

            if normal0.format == 37:
                n = [vW, normal0.stream.readSn16(), normal0.stream.readSn16()]
                normal0.stream.seek(normal0.advance, os.SEEK_CUR)
            elif normal0.format == 10:
                n = [normal0.stream.readF16(), normal0.stream.readF16(), normal0.stream.readF16()]
                normal0.stream.seek(normal0.advance, os.SEEK_CUR)

            v2 = [0, 0, 0]
            n2 = [0, 0, 0]
            for j in range(3):
                for k in range(4):
                    if k == 3:
                        v2[j] += boneTransform[k][j]
                    else:
                        v2[j] += v[k] * boneTransform[k][j]
                        n2[j] += n[k] * boneTransform[k][j]

            nLength = math.sqrt(n2[0] ** 2 + n2[1] ** 2 + n2[2] ** 2)
            if nLength > 0:
                n2[0] /= nLength
                n2[1] /= nLength
                n2[2] /= nLength

            verts[idx] = (-v2[0], -v2[2], v2[1])
            norms[idx] = (-n2[0], -n2[2], n2[1])

        indexStart = len(allIndices)
        for f in faces:
            allIndices.append(f[0] + vertexOffset)
            allIndices.append(f[1] + vertexOffset)
            allIndices.append(f[2] + vertexOffset)
        meshGroupList.append(MeshGroup(indexStart, len(allIndices) - indexStart, mesh.materialId, mesh.name))

        allVerts.extend(verts)
        allNorms.extend(norms)
        allUvs.extend(uvs)
        vertexOffset += vertexCount

    if not allVerts:
        raise ValueError("No renderable mesh data found in modelbin")

    result = ParsedModel()
    result.vertices = np.array(allVerts, dtype=np.float32)
    result.normals = np.array(allNorms, dtype=np.float32)
    result.uvs = np.array(allUvs, dtype=np.float32)
    result.indices = np.array(allIndices, dtype=np.uint32)
    result.meshName = meshes[0].name if meshes else "unknown"
    result.meshGroups = meshGroupList
    result.materialNames = materialNames
    return result
