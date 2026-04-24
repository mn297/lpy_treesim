from pxr import Usd, UsdGeom, Vt
import ctypes


from pxr import Usd, UsdGeom, Gf


def create_mesh(stage, path, points, face_vertex_counts, face_vertex_indices):
    """
    Helper function to create a USD mesh.
    """
    mesh = UsdGeom.Mesh.Define(stage, path)
    mesh.CreatePointsAttr(points)
    mesh.CreateFaceVertexCountsAttr(face_vertex_counts)
    mesh.CreateFaceVertexIndicesAttr(face_vertex_indices)
    mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
    return mesh


def create_mesh_usd(file_path, vertices, colors, faces):
    # 1. Create a new USD stage
    # Set the up axis and units
    stage = Usd.Stage.CreateNew(file_path)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    # 2. Define the Mesh primitive
    mesh = UsdGeom.Mesh.Define(stage, '/TreeMesh')

    # 3. Set the vertex positions (points)
    vs = [(pt[0], pt[2], pt[1]) for pt in vertices]
    mesh.CreatePointsAttr(vs)

    # 4. Define face topology
    # face_counts: how many vertices in each face (e.g., [3, 3, 3] for triangles)
    # face_indices: flat list of vertex indices for all faces
    face_counts = [len(face) for face in faces]
    face_indices = [idx for face in faces for idx in face]

    mesh.CreateFaceVertexCountsAttr(face_counts)
    mesh.CreateFaceVertexIndicesAttr(face_indices)

    # --- ADDING COLOR ---
    # 1. Create the displayColor Primvar
    color_primvar = mesh.CreateDisplayColorAttr()
    cs = [(col[0] / 255.0, col[1] / 255.0, col[2] / 255.0) for col in colors]
    color_primvar.Set(cs)

    # Example transform
    # UsdGeom.XformCommonAPI(mesh).SetRotate((0, 0, 25))

    # 2. Set Interpolation
    # 'constant' = 1 color for whole mesh
    # 'vertex'   = 1 color per point (blends across faces)
    # 'uniform'  = 1 color per face
    if len(colors) == 1:
        mesh.GetDisplayColorPrimvar().SetInterpolation(UsdGeom.Tokens.constant)
    else:
        mesh.GetDisplayColorPrimvar().SetInterpolation(UsdGeom.Tokens.vertex)

    # 5. Set optional subdivision scheme (none for a poly mesh)
    mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)

    # 6. Save the stage
    stage.GetRootLayer().Save()

# Example Data
# verts = [(0,0,0), (1,0,0), (1,1,0), (0,1,0)] # 4 vertices
# faces = [(0,1,2), (0,2,3)]                  # 2 triangles forming a square

# create_mesh_usd("mesh_example.usda", verts, faces)
