# ================================
# test: simple_colour_split
#
# description:
#     Simple test that splits a cube into two halves and colours each half
#
# ================================


from psb import *

grammar = Grammar("grammars\/simple_grammar.txt", "plot")
model = Model(Position(0,0,0), CoordinateSystem((1,0,0), (0,1,0), (0,0,1)), Size(10,10,10))
grammar.run(model, 1)