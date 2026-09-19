from .base_definitions import MantisSocketTemplate as ST
from dataclasses import replace


StaticIntSockets = [
    Operation := ST(name="Operation", bl_idname="MathFloatOperation", is_input=True),
    IntA := ST(name="Int A", bl_idname="IntSocket", is_input=True),
    IntB := ST(name="Int B", bl_idname="IntSocket", is_input=True),
    ResultInt := ST(name="Result Int", bl_idname="IntSocket", is_input=False),
]

StaticFloatSockets = [
    Operation,
    FloatA := ST(name="Float A", bl_idname="FloatSocket", is_input=True),
    FloatB := ST(name="Float B", bl_idname="FloatSocket", is_input=True),
    ResultFloat := ST(name="Result Float", bl_idname="FloatSocket", is_input=False),
]

StaticVectorSockets = [
    Operation := ST(name="Operation", bl_idname="MathVectorOperation", is_input=True),
    VectorA := ST(name="Vector A", bl_idname="VectorSocket", is_input=True),
    VectorB := ST(name="Vector B", bl_idname="VectorSocket", is_input=True),
    ScalarA := ST(name="Scalar A", bl_idname="FloatSocket", is_input=True, hide=True),
    ResultVector := ST(name="Result Vector", bl_idname="VectorSocket", is_input=False),
    ResultFloat := ST(name="Result Float", bl_idname="FloatSocket", is_input=False, hide=True),
]