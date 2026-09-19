from .base_definitions import MantisSocketTemplate as ST
from dataclasses import replace

# NOTE most Schema nodes are fully dynamic, and the rest are
#      mostly dynamic, so they don't use Socket Templates much.
SchemaIndexSockets = [
    Index := ST(name="Index", bl_idname="IntSocket", is_input=False),
    SchemaLength := ST(name="Schema Length", bl_idname="IntSocket", is_input=False),
]

SchemaArrayInputGetSockets = [
    OoBBehaviour := ST(name="OoB Behaviour", bl_idname="EnumArrayGetOptions", is_input=True),
    Index := ST(name="Index", bl_idname="IntSocket", is_input=True),
]