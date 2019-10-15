# ================================
# module: grammar
#
# description:
#     Provides tools to parse, interpret and run a CGA shape grammar
#
# ================================


__all__ = [
        'Grammar',
        'Rule',
        'RuleJob',
        ]

from .geometry import *
from sly import Lexer, Parser
from .operations import *
from .model import Model

class Grammar:
    # startRule has type Rule and is the first rule of the grammar
    def __init__(self, fname, startRule):
        lexer = CGALexer()
        parser = CGAParser()
        checker = CGAChecker()

        with open(fname) as f:
            grammar = f.read()

        # TODO get rid of this
        toks = lexer.tokenize(grammar)
        for tok in toks:
            print(tok)

        parser.parse(lexer.tokenize(grammar))
        self.ruleFromLabel = checker.check(parser.ruleFromLabel)
        self.startRule = startRule

    def run(self, startModel, LOD):
        scope = Scope(startModel.pos, startModel.coordSys, startModel.size)
        ruleQueue = [RuleJob(self.startRule, scope)]
        i = 0
        while len(ruleQueue) > i:
            rule = self.ruleFromLabel[ruleQueue[i].ruleLabel]
            if (rule.LOD <= LOD):
                ruleQueue += rule.run(startModel, ruleQueue[i].scope)
            i += 1

class CGALexer(Lexer):
    tokens = {
      IDENT,
      NUMBER,
      PLUS,
      TIMES,
      MINUS,
      DIVIDE,
      ASSIGN,
      COLON,
      ARROW,
      SPLIT,
      LPAR,
      RPAR,
      COMMA,
      COLOUR,
      NEWLINE,
      FLOAT,
    }

    # NEWLINE = r'\n'

    # Tokens
    IDENT = r'[a-zA-Z_][a-zA-Z0-9_]*'
    IDENT['split'] = SPLIT
    IDENT['colour'] = COLOUR
    #FLOAT = r'\d+\.\d+'
    #NUMBER = r'\d+'

    # Special symbols
    ARROW = r'-->'
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    ASSIGN = r'='
    COLON = r':'
    LPAR = r'\('
    RPAR = r'\)'
    COMMA = r','
    NEWLINE = r'\n'


    # Ignored pattern
    ignore = ' \t'
    ignore_comment = r'\#.*'
    #ignore_newlines = r'\n+'

    # Extra action for newlines
    #def ignore_newlines(self, t):
    #    self.lineno += t.value.count('\n')

    @_(r'\d+\.\d+')
    def FLOAT(self, t):
        t.value = float(t.value)   # Convert to a numeric value
        return t

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)   # Convert to a numeric value
        return t

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

class Rule:
    def __init__(self, left, right, LOD):
        self.ruleNum = left.ruleNum
        self.label = left.label
        self.ops = right.ops
        self.priority = right.priority
        self.LOD = LOD

    def run(self, model, scope):
        newRulesToRun = []
        for op in self.ops:
            newRulesToRun += op.run(model, scope)
        return newRulesToRun

class Right:
    def __init__(self, ops, priority = None):
        self.ops = ops
        self.priority = priority

class Left:
    def __init__(self, ruleNum, label):
        self.ruleNum = ruleNum
        self.label = label


class CGAParser(Parser):

    tokens = CGALexer.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        )

    def __init__(self):
        self.ruleFromLabel = { }

    @_('rules rule')
    def rules(self, p):
        p.rules.append(p.rule)
        return p.rules

    @_('rule')
    def rules(self, p):
        return [p.rule]

    @_('left ARROW right NEWLINE')
    def rule(self, p):
        # Just do LOD=1 for now
        newRule = Rule(p.left, p.right, 1)
        if newRule.label in self.ruleFromLabel:
            if type(self.ruleFromLabel[newRule.label]) != list:
                ruleWithSameName = self.ruleFromLabel[newRule.label]
                raise RuntimeError(f'Rule number {ruleWithSameName.ruleNum} has the same name as another rule but no priority')
            elif p.right.priority == None:
                raise RuntimeError(f'Rule number {newRule.ruleNum} has the same name as another rule but no priority')
            else:
                prevRule = self.ruleFromLabel[newRule.label][-1]
                newRule.cumulativePriority = prevRule.cumulativePriority + newRule.priority
                self.ruleFromLabel[newRule.label].append(newRule)
        else:
            if newRule.priority == None:
                self.ruleFromLabel[newRule.label] = newRule
            else:
                newRule.cumulativePriority = newRule.priority
                self.ruleFromLabel[newRule.label] = [newRule]
        return newRule

    # TODO: add cond
    @_('NUMBER COLON ruleLabel')
    def left(self, p):
        return Left(p.NUMBER, p.ruleLabel)

    # TODO: should be able to give params too
    @_('IDENT')
    def ruleLabel(self, p):
        return p.IDENT

    @_('ops COLON FLOAT')
    def right(self, p):
        return Right(p.ops, p.FLOAT)

    @_('ops')
    def right(self, p):
        return Right(p.ops)

    # TODO: should be able to have multiple ops rather than just one
    @_('op')
    def ops(self, p):
        return [p.op]

    # TODO: add more ops and add ability for a rule_name to be an op
    # TODO: make SPLIT actually work like SPLIT should
    # TODO: in fact, we should just have an IDENT which we lookup to check it is a valid op
    @_('SPLIT params')
    def op(self, p):
        return OpSplit(*p.params)

    @_('COLOUR params')
    def op(self, p):
        return OpColour(*p.params)

    @_('LPAR inner RPAR')
    def params(self, p):
        return p.inner

    # TODO: for now it is just a list of rules but probs shouldn't be!
    @_('inner COMMA ruleLabel')
    def inner(self, p):
        p.inner.append(p.ruleLabel)
        return p.inner

    @_('ruleLabel')
    def inner(self, p):
        return [p.ruleLabel]

class CGAChecker:
    def __init__(self):
        pass

    def check(self, ruleFromLabel):
        for label, rules in ruleFromLabel.items():
            if type(rules) == list:
                left = Left(rules[0].ruleNum, label)
                right = Right([OpChooseRuleWithPriority(rules)])
                # TODO: just using the first rule's LOD for now
                ruleFromLabel[label] = Rule(left, right, rules[0].LOD)
        return ruleFromLabel
    # This should check stuff like probabilities adding to 1
    # Should maybe do the replacing complex rules with simple rules here too


if __name__ == '__main__':
    grammar = Grammar('simple_grammar.txt', 'plot')
    model = Model(Position(0,0,0), CoordinateSystem((1,0,0), (0,1,0), (0,0,1)), Size(10,10,10))
    grammar.run(model, 1)