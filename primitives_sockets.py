from .base_definitions import MantisSocketTemplate as SockTemplate
from dataclasses import replace


LatticeSockets = [
    Name := SockTemplate(name="Name", blender_property="name", default_value='Lattice',
            is_input=True, bl_idname="StringSocket"),
    ResolutionU := SockTemplate(name = "Resolution U", bl_idname="UnsignedIntSocket",
            blender_property="points_u", is_input=True, default_value=2),
    ResolutionV := SockTemplate(name = "Resolution V", bl_idname="UnsignedIntSocket",
            blender_property="points_v", is_input=True, default_value=2),
    ResolutionW := SockTemplate(name = "Resolution W", bl_idname="UnsignedIntSocket",
            blender_property="points_w", is_input=True, default_value=2),
    InterpolationTypeU := SockTemplate(name = "Interpolation Type U",
            bl_idname="EnumLatticeInterpolationTypeSocket",
            blender_property="interpolation_type_u",
            is_input=True, default_value='KEY_BSPLINE'),
    InterpolationTypeV := SockTemplate(name = "Interpolation Type V",
            bl_idname="EnumLatticeInterpolationTypeSocket",
            blender_property="interpolation_type_v",
            is_input=True, default_value='KEY_BSPLINE'),
    InterpolationTypeW := SockTemplate(name = "Interpolation Type W",
            bl_idname="EnumLatticeInterpolationTypeSocket",
            blender_property="interpolation_type_w",
            is_input=True, default_value='KEY_BSPLINE'),
    GeometryOutput := SockTemplate(name="Lattice Geometry", bl_idname="GeometrySocket")
]