# ================================
# test: simple_colour_split
#
# description:
#     Simple test that splits a cube into two halves and colours each half
#
# ================================


from psb import *

model = Model(Position(0,0,0), CoordinateSystem((1,0,0), (0,1,0), (0,0,1)), Size(10,10,10))

colourRed = OpColour("red")
colourRedRule = Rule([colourRed], 1)

colourBlue = OpColour("blue")
colourBlueRule = Rule([colourBlue], 1)

splitRedBlue = OpSplit(colourRedRule, colourBlueRule)
splitRedBlueRule = Rule([splitRedBlue], 1)

grammar = Grammar(splitRedBlueRule)
grammar.run(model, 1)