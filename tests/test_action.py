# -*- coding:utf-8 -*-
import unittest

class TestAction(unittest.TestCase):
    """Tests ``pattern.Action`` class"""

    def get_target(self, *args, **kw):
        from aerolito.pattern import Action
        return Action(*args, **kw)

    def get_stub_literal(self, value):
        class Literal: pass
        literal = Literal
        literal._value = value
        return literal

    def get_stub(self):
        return lambda v: v[0]+v[1]

    def test_init(self):
        stub = self.get_stub()
        action = self.get_target(stub, [1, 2, 3])
        
        assert action._directive == stub
        assert action._params == [1, 2, 3]
    
    def test_run(self):
        environ = {
            'directives': {
                'add': lambda v: v[0]+v[1],
                'isdefined': lambda v:True,
            },
            'user_id':1,
            'globals': {},
            'session': {
                1: {
                    'stars': [],
                    'locals': {},
                }
            }
        }

        stub = self.get_stub()
        action = self.get_target(stub, [
            self.get_stub_literal(4), 
            self.get_stub_literal(1)
        ])

        assert action.run(environ) == 5

if __name__ == '__main__':
    unittest.main()
