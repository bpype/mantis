# This file is a minimal parser for simple expressions
# It's used for e.g. Overlay variables
# Also used to figure out the initial value of a driver for e.g. Curve Pin Node

# For now I will only support basic operations.
# Once I get this working it will be easy to expand
tokens = {
    "+" : "ADD",
    "-" : 'SUBTRACT',
    "/" : 'DIVIDE',
    "*" : 'MULTIPLY',
}

#I'm too tired to work on this but I need to do it later so... I'll save the file.
def parse_expression(expression):
    numbers = []
    current_number = ""
    # for i range len(expression):
    #     if 
    pass
        