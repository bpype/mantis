# This file is for defining socket-filler operators by name
# These operators are defined by name in Socket Templates and used by
#    the Socket Filler system in the Property-Socket Map to transform
#    Mantis data to Blender-ready data
# Primarily, this will involve type-casting and enum handling
# Probably I will need to expand this system to take arbitrary arguments
#    but for now we'll take the Mantis Node and the data as arguments

def cast_to_bool(*args, **kwargs):
    return bool(args[1]) # args[1] is the data

def invert_cast_to_bool(*args, **kwargs):
    return bool( not args[1]) # args[1] is the data

def resolve_rotation_mode_auto(*args, **kwargs):
    return 'XYZ' # for now this is hardcoded lmao
