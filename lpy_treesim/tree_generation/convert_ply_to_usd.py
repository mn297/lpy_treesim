from pxr import Usd, UsdGeom, Vt, Gf, UsdSemantics, Sdf, UsdShade
import ctypes


def create_labeled_asset(file_path):
    # 1. Create a new Stage
    stage = Usd.Stage.CreateNew(file_path)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

    # 2. Create your Mesh or Xform
    root_path = "/MyLabeledObject"
    mesh_prim = UsdGeom.Mesh.Define(stage, root_path)

    # 3. Apply the SemanticsAPI
    # The 'instanceName' (second arg) is usually "class" for Isaac Sim
    semantics_api = UsdSemantics.SemanticsAPI.Apply(mesh_prim.GetPrim(), "class")

    # 4. Set the attributes that Isaac Sim's annotators read
    # semanticType: Defines the category (usually 'class')
    # semanticData: Defines the specific label (e.g., 'engine_part')
    semantics_api.CreateSemanticTypeAttr().Set("class")
    semantics_api.CreateSemanticDataAttr().Set("engine_part")

    # Do twice to get two different labelings
    semantics_api.CreateSemanticTypeAttr().Set("class II")
    semantics_api.CreateSemanticDataAttr().Set("engine_part")

    # Save the stage
    stage.GetRootLayer().Save()
    print(f"Asset created at: {file_path}")


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

def check_texture():
    # 1. Create a new USD stage
    # Set the up axis and units
    stage = Usd.Stage.CreateNew("test_texture.usda")
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    # 2. Define the Mesh primitive
    mesh = UsdGeom.Mesh.Define(stage, '/TreeMesh')

    # 2. Define Texture Coordinates (UVs)
    # We use 'st' as the name.
    # 'interpolation' determines how UVs map to the geometry.
    tex_coords = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
        "st",
        Sdf.ValueTypeNames.TexCoord2fArray,
        UsdGeom.Tokens.varying
    )

    # 2. Create the Material
    material_path = Sdf.Path("/textures/pine_bark_vmbibe2g_2k")
    material = UsdShade.Material.Define(stage, material_path)

    # 3. Create the Shader (UsdPreviewSurface)
    shader = UsdShade.Shader.Define(stage, material_path.AppendChild("PBRShader"))
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)

    # 4. Create the Texture Sampler (UsdUVTexture)
    reader = UsdShade.Shader.Define(stage, material_path.AppendChild("TexSampler"))
    reader.CreateIdAttr("UsdUVTexture")
    reader.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("textures/Pine_Bark_vmbibe2g_2K_BaseColor.jpg")
    # Connect texture output to shader's diffuseColor input
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
        reader.CreateOutput("rgb", Sdf.ValueTypeNames.Color3f))

    # 5. Create the Primvar Reader (To tell the texture to use 'st')
    st_reader = UsdShade.Shader.Define(stage, material_path.AppendChild("STReader"))
    st_reader.CreateIdAttr("UsdPrimvarReader_float2")
    st_reader.CreateInput("varname", Sdf.ValueTypeNames.String).Set("st")
    # Connect reader output to texture sampler's st input
    reader.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(
        st_reader.CreateOutput("result", Sdf.ValueTypeNames.Float2))

    # 6. Bind the Material to the Mesh
    UsdShade.MaterialBindingAPI(mesh).Bind(material)
    # 6. Save the stage
    stage.GetRootLayer().Save()


def create_mesh_usd(file_path, vertices, colors, textures, faces, meta_data):
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

    # 2. Define Texture Coordinates (UVs)
    # We use 'st' as the name.
    # 'interpolation' determines how UVs map to the geometry.
    tex_coords = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar(
        "st",
        Sdf.ValueTypeNames.TexCoord2fArray,
        UsdGeom.Tokens.varying
    )
    # 3. Set the UV values
    # These correspond to the points defined above: (u, v)
    ts = [(t[0], t[1]) for t in textures]
    tex_coords.Set(ts)

    # 2. Create the Material
    material_path = Sdf.Path("/textures/pine_bark_vmbibe2g_2k")
    material = UsdShade.Material.Define(stage, material_path)

    # 3. Create the Shader (UsdPreviewSurface)
    shader = UsdShade.Shader.Define(stage, material_path.AppendChild("PBRShader"))
    shader.CreateIdAttr("UsdPreviewSurface")
    shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)

    # 4. Create the Texture Sampler (UsdUVTexture)
    reader = UsdShade.Shader.Define(stage, material_path.AppendChild("TexSampler"))
    reader.CreateIdAttr("UsdUVTexture")
    reader.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("textures/Pine_Bark_vmbibe2g_2K_BaseColor.jpg")
    # Connect texture output to shader's diffuseColor input
    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
        reader.CreateOutput("rgb", Sdf.ValueTypeNames.Color3f))

    # 5. Create the Primvar Reader (To tell the texture to use 'st')
    st_reader = UsdShade.Shader.Define(stage, material_path.AppendChild("STReader"))
    st_reader.CreateIdAttr("UsdPrimvarReader_float2")
    st_reader.CreateInput("varname", Sdf.ValueTypeNames.String).Set("st")
    # Connect reader output to texture sampler's st input
    reader.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(
        st_reader.CreateOutput("result", Sdf.ValueTypeNames.Float2))

    # 6. Bind the Material to the Mesh
    UsdShade.MaterialBindingAPI(mesh).Bind(material)

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
