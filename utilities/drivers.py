from .utilities import (prRed, prGreen, prPurple, prWhite,
                              prOrange,
                              wrapRed, wrapGreen, wrapPurple, wrapWhite,
                              wrapOrange,)



##########################################################################
#  Drivers!
##########################################################################


# SO: the idea is that the driver's input is a Python dictionary
#     with all of the requisite information to build the driver
# I need a generic function to create the driver

# EXAMPLE INPUT:
# example   =     {"owner":None,
                    # "prop":None,
                    # "ind":-1,
                    # "type":"AVERAGE",
                    # "vars":[{"id":None,
                            # "name":"a",
                            # "type":"TRANSFORMS",
                            # "space":'LOCAL_SPACE',
                            # "channel":'LOC_Z',},],
                    # "keys":[{"co":(0,0.5),
                            # "interpolation": "BEZIER",
                            # "handle_left_type":  "AUTO_CLAMPED", #if AUTO then handle_left will be ignored
                            # "handle_right_type": "AUTO_CLAMPED",
                            # "type":"KEYFRAME",}, #display type
                            # {"co":(-1,0),
                            # "interpolation": "BEZIER",
                            # "handle_left_type":  "AUTO_CLAMPED",
                            # "handle_right_type": "AUTO_CLAMPED",
                            # "type":"KEYFRAME",},
                            # {"co":(1,1),
                            # "interpolation": "BEZIER",
                            # "handle_left_type":  "ALIGNED",
                            # "handle_right_type": "ALIGNED",
                            # "handle_left":  (-0.4,0), #these are treated as offsets
                            # "handle_right": ( 0.04,0), #only valid if interp. == BEZIER
                            # "type":"KEYFRAME",},],
                    # }


class MantisDriver(dict):
    pass

def CreateDrivers(drivers):
    from bpy.app import version
    def brackets(s):
        return "[\""+s+"\"]"
    from bpy.types import Object, Key
    fcurves = []
    for driver in drivers:
        if (isinstance(driver["owner"], Object)):
            ob = driver["owner"]
        else: # Pose Bone:
            ob = driver["owner"].id_data
        path_from_id = driver.get('path_from_id')
        # TODO: I want to refactor path_from_id check&set out. it should always be provided
        # I think this is still here because of the 2 or three places where nodes make their
        # own drivers e.g. Hook deformer for curves
        if path_from_id is None:
            path_from_id = driver["owner"].path_from_id(driver["prop"])
        if isinstance(driver["owner"], Key):
            fcurves = ob.driver_add(driver["prop"])
        else:
            fcurves = ob.driver_add(path_from_id, driver["ind"])
        if not isinstance(fcurves, list):
            fcurves = [fcurves] # ususally it is a single fCurve, sometimes it is a list
            # for e.g. array properties if driver_add is given -1 as index
        for fc in fcurves:
            drv = fc.driver
            try: # annoyingly, this initializes with a modifier
                fc.modifiers.remove(fc.modifiers[0])
            except IndexError: #haven't seen this happen, but should handle
                pass # perhaps this has been fixed for 3.0?
            if version >= (5,0,0): # and now it initializes with keys. p
                fc.keyframe_points.clear()
            drv.type = driver["type"]
            if (expr := driver.get("expression")) and isinstance(expr, str):
                drv.expression = expr

            fc.extrapolation = "CONSTANT"
            if (extrapolation_mode := driver.get("extrapolation")) in ("CONSTANT", "LINEAR"):
                fc.extrapolation = extrapolation_mode
            else:
                prRed(f"Extrapolation Mode in driver has incorrect data: {extrapolation_mode}")

            # logic for handling type can go here

            # start by clearing
            while (len(drv.variables) > 0):
                v = drv.variables[0]
                dVar = drv.variables.remove(v)

            for v in driver["vars"]:
                pose_bone = False
                bone = ''; target2bone = ''
                vob, target2ob = None, None
                if (isinstance(v["owner"], Object)):
                    vob = v["owner"]
                else:
                    pose_bone = True
                    vob = v["owner"].id_data
                    bone = v["owner"].name
                #

                if "xForm 2" in v.keys() and v["xForm 2"]:
                    if (isinstance(v["xForm 2"], Object)):
                        target2ob = v["xForm 2"]
                    else:
                        target2ob = v["xForm 2"].id_data
                        target2bone = v["xForm 2"].name

                dVar = drv.variables.new()


                dVar.name = v["name"]
                dVar.type = v["type"]
                #for now, assume this is always true:
                #dVar.targets[0].id_type = "OBJECT"
                #it's possible to use other datablocks, but this is not commonly done
                #actually, it looks like Blender figures this out for me.

                dVar.targets[0].id = vob
                dVar.targets[0].bone_target = bone
                if len(dVar.targets) > 1:
                    dVar.targets[1].id = target2ob
                    dVar.targets[1].bone_target = target2bone

                if (dVar.type == "TRANSFORMS"):
                    dVar.targets[0].transform_space = v["space"]
                    dVar.targets[0].transform_type = v["channel"]
                if (dVar.type == 'SINGLE_PROP'):
                    if pose_bone:
                        stub = "pose.bones[\""+v["owner"].name+"\"]"
                        dVar.targets[0].data_path = stub + brackets(v["prop"])
                        if (hasattr( v["owner"], v["prop"] )):
                            dVar.targets[0].data_path = stub + "."+ (v["prop"])
                        # else: # the property may be added later.
                        # TODO BUG I want a guarantee that this property is already there.

                    else:
                        if (hasattr( v["owner"], v["prop"] )):
                            dVar.targets[0].data_path = (v["prop"])
                        else:
                            dVar.targets[0].data_path = brackets(v["prop"])
            # setup keyframe points
            kp = fc.keyframe_points
            for key in driver["keys"]:
                k = kp.insert(frame=key["co"][0], value = key["co"][1],)

                k.interpolation     = key["interpolation"]
                if (key["interpolation"] == 'BEZIER'):
                    k.handle_left_type  = key["handle_left_type" ]
                    k.handle_right_type = key["handle_right_type"]
                    if (k.handle_left_type in ("ALIGNED", "VECTOR", "FREE")):
                        k.handle_left       = (k.co[0] + key["handle_left"][0], k.co[1] + key["handle_left"][1])
                    if (k.handle_right_type in ("ALIGNED", "VECTOR", "FREE")):
                        k.handle_right      = (k.co[0] + key["handle_right"][0], k.co[1] + key["handle_right"][1])
                k.type = key["type"]
