from dataclasses import dataclass, field
from typing import List, Any


@dataclass
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
    default_value    : Any = field(default=None)

@dataclass
class xForm_info():
    object_type          :  str = field(default="")
    root_armature        :  str = field(default="")
    parent_pose_name     :  str = field(default="")
    parent_edit_name     :  str = field(default="")
    self_pose_name       :  str = field(default="")
    self_edit_name      :  str = field(default="")
# should I add node signatures to this?

@dataclass
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