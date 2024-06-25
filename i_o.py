# this is the I/O part of mantis. I eventually intend to make this a markup language. not right now tho lol

# https://stackoverflow.com/questions/42033142/is-there-an-easy-way-to-check-if-an-object-is-json-serializable-in-python
# thanks!
def is_jsonable(x):
    import json
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False



def export_to_json(tree, path):
    # takes a parsed mantis tree and returns a JSON
    tree_data = tree.parsed_tree

    # we have to prepare the tree data.
    #   SO: we can't use tuples as keys in JSON
    #   but the tree uses a lot of tuple keys in Python dicts
    #   so we can map the tuples to UUIDs instead
    #  then we can store the list of nodes mapped to the same UUIDs
    # the goal is to store the tree in a way that makes reproduction possible


    import json
    with open(path, "w") as file:
        print("Writing mantis tree data to: ", file.name)
        file.write( json.dumps(json_data, indent = 4) )
    

def import_from_json(json_data):
    #reads a JSON file and makes a tree from it.
    pass

def tree_to_b_nodes(tree):
    # creates a node tree in Blender from a mantis tree
    pass