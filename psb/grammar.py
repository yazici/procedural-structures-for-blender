# ================================
# module: grammar
#
# description:
#     Provides tools to construct and run a CGA shape grammar
#
# ================================


__all__ = [
        'Grammar',
        'Rule',
        'RuleJob',
        ]

from .geometry import Scope

class Grammar:
    # startRule has type Rule and is the first rule of the grammar
    def __init__(self, startRule):
        self.startRule = startRule

    def run(self, startModel, LOD):
        scope = Scope(startModel.pos, startModel.coordSys, startModel.size)
        ruleQueue = [RuleJob((self.startRule, scope))]
        i = 0
        while len(ruleQueue) > i:
            if (ruleQueue[i].rule.LOD <= LOD):
                ruleQueue += ruleQueue[i].rule.run(startModel, ruleQueue[i].scope)
            i += 1

class Rule:
    def __init__(self, ops, LOD):
        self.ops = ops
        self.LOD = LOD

    def run(self, model, scope):
        newRulesToRun = []
        for op in self.ops:
            newRulesToRun += [RuleJob(job) for job in op.run(model, scope)]

        return newRulesToRun

class RuleJob:
    def __init__(self, ruleAndScope):
        self.rule, self.scope = ruleAndScope