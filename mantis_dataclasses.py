from dataclasses import dataclass, field

@dataclass
class xForm_info():
    object_type          :  str = field(default="")
    root_armature        :  str = field(default="")
    parent_pose_name     :  str = field(default="")
    parent_edit_name     :  str = field(default="")
    self_pose_name       :  str = field(default="")
    self_edit_name      :  str = field(default="")
# should I add node signatures to this?
