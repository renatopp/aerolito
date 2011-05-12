# -*- coding:utf-8 -*-
import unittest

class TestAction(unittest.TestCase):
    def getTarget(self, *args, **kw):
        from aerolito.pattern import Action
        return Action(*args, **kw)

    def getStubLiteral(self, value):
        class Literal: pass
        literal = Literal
        literal._value = value
        return literal

    def getStub(self):
        return lambda x, y, environ: x+y

    def test_init(self):
        stub = self.getStub()
        action = self.getTarget(stub, [1, 2, 3])
        
        assert action._function == stub
        assert len(action._params) == 3

    def test_run(self):
        environ = {
            'directives': {
                'add': lambda x, y, environ: x+y,
                'isdefined': lambda x, environ:True,
            },
            'userid':1,
            'globals': {},
            'session': {
                1: {
                    'stars': [],
                    'locals': {

                    },
                }
            }
        }

        stub = self.getStub()
        action = self.getTarget(stub, 
            [self.getStubLiteral(4), self.getStubLiteral(1)])

        assert action.run(environ) == 5
        
if __name__ == '__main__':
    unittest.main()
