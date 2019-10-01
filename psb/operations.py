# ================================
# module: operations
#
# description:
#     Provides definitions for opeartions that can be used in a CGA Shape grammar
#
# ================================


__all__ = [
        'OpSplit',
        'OpPushScope',
        'OpPopScope',
        'OpColour',
        ]

from .geometry import *

class Op:
    def __init__(self):
        raise NotImplementedError

    def run(self, model, scope):
        raise NotImplementedError

class OpSplit(Op):

    # For now just split in half and apply left and right to the new scopes
    def __init__(self, left, right):
        self.leftRule = left
        self.rightRule = right

    def run(self, model, scope):
        # Create a new scope for each part of the split
        # For now just split in half
        s = scope
        leftScope = Scope(s.pos, s.coordSys, Size(s.size.x / 2, s.size.y, s.size.z))

        rightScope = Scope(Position(s.pos.x + s.size.x / 2, s.pos.y, s.pos.z), s.coordSys, Size(s.size.x / 2, s.size.y, s.size.z))

        # Return the param/scope pairs as rules that need running

        return [(self.leftRule, leftScope), (self.rightRule, rightScope)]

class OpPushScope(Op):
    def __init__(self):
        ()

    def run(self, model, scope):
        scope.push
        return []

class OpPopScope(Op):
    def __init__(self):
        ()

    def run(self, model, scope):
        scope.pop
        return []

class OpColour(Op):
    def __init__(self, colour):
        self.colour = colour

    def run(self, model, scope):
        print(f"Colouring scope:\n{scope}\nwith colour {self.colour}")
        model.recolour(scope, self.colour)
        return []


