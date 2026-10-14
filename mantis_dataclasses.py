from dataclasses import dataclass, field
from typing import List, Any, Tuple, Optional

@dataclass(slots=True)
class MantisSocketTemplate():
    name             : str = field(default="")
    bl_idname        : str = field(default="")
    traverse_target  : str = field(default="")
    identifier       : str = field(default="")
    display_shape    : str = field(default="") # for arrays
    category         : str = field(default="") # for use in display update
    blender_property : str | tuple[str] = field(default="") # for props_sockets -> evaluate sockets
    is_input         : bool = field(default=False)
    hide             : bool = field(default=False)
    use_multi_input  : bool = field(default=False)
    ui_only          : bool = field(default=False)
    default_value    : Any = field(default=None)
    # this is a hint for the props_sockets system for complex situations
    #  where multiple blender objects own the properties, like e.g. bone/posebone
    prop_owner_group : str = field(default="")
    is_animatable    : bool = field(default=True) # controls whether a driver is legal or not
    # These attributes are for deprecated or new features in Blender
    min_bpy_version  : Optional[tuple[int]] = field(default=None)
    max_bpy_version  : Optional[tuple[int]] = field(default=None)

@dataclass(slots=True)
class xForm_info():
    object_type          :  str = field(default="")
    root_armature        :  str = field(default="")
    parent_pose_name     :  str = field(default="")
    parent_edit_name     :  str = field(default="")
    self_pose_name       :  str = field(default="")
    self_edit_name      :  str = field(default="")
# should I add node signatures to this?

@dataclass(slots=True)
class custom_prop_template():
    name      : str = field(default="")
    prop_type : str = field(default="")
    default_value_string : str = field(default="")
    default_value_bool   : bool = field(default=False)
    default_value_int    : int = field(default=0)
    default_value_float  : float = field(default=0.0)
    default_value_vector : List[float] = field(default_factory=list)
    min : float|int = field(default=0)
    max : float|int = field(default=1)
    soft_min : float|int = field(default=1)
    soft_max : float|int = field(default=1)
    description : str = field(default="")

@dataclass(slots=True)
class MantisBoneTransform():
    matrix    : Any = field(default=[1,0,0,0,
                                     0,1,0,0,
                                     0,0,1,0,
                                     0,0,0,1,]),
    # I would like to have an intelligent way of handling
    #  object- vs. world- space matrices
    matrix_space  : str = field(default="OBJECT")
    length    : float = field(default=1.0),

@dataclass(slots=True)
class MantisBBoneTransform():
    num_bbone_segmetns: int = field(default=1)
    # Offsets & Curve Handles
    bbone_curveinx: float = field(default=0.0)
    bbone_curveiny: float = field(default=0.0)
    bbone_curveoutx: float = field(default=0.0)
    bbone_curveouty: float = field(default=0.0)
    # Easing
    bbone_easein: float = field(default=1.0)
    bbone_easeout: float = field(default=1.0)
    # Roll
    bbone_rollin: float = field(default=0.0)
    bbone_rollout: float = field(default=0.0)
    # Scale Vectors
    bbone_scalein: Tuple[float, float, float] = field(
        default_factory=lambda: (1.0, 1.0, 1.0) )
    bbone_scaleout: Tuple[float, float, float] = field(
        default_factory=lambda: (1.0, 1.0, 1.0) )
    # Custom Handles
    use_bbone_custom_handles: bool = field(default=False)
    bbone_custom_handle_start: str = field(default=None)
    bbone_custom_handle_end: str = field(default=None)

# used to apply values or drivers to blender properties in a generic way
@dataclass(slots=True)
class MantisSocketFiller():
    socket_name: str = field(default="")
    property_name : str = field(default="")
    default_value: Any = field(default=None)
    array_index: int = field(default=0) # for multi-input array sockets
    value_index: Optional[int] = field(default=None) # for vector properties
    # A Combo Property is a property that jams a bunch of blender properties into one socket
    combo_property: bool = field(default=False)

    def __repr__(self):
        return f"socket_name: {self.socket_name}, " \
               f"property_name: {self.property_name}, " \
               f"default_value: {self.default_value}, " \
               f"array_index: {self.array_index or 0}, " \
               f"value_index: {self.value_index or None}" 