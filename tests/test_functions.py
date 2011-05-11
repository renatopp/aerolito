# -*- coding:utf-8 -*-
import unittest

class TestReplace(unittest.TestCase):
    def getStubLiteral(self, value):
        class Literal: pass
        literal = Literal
        literal._value = value
        return literal


    def test_replaceStar(self):
        from aerolito.pattern import replace
        environ = {
            'userid': 1,
            'globals': {},
            'session': {
                1: {
                    'stars': ['a', 'b', 'c']
                }
            }
        }

        text = 'Meu nome eh <star> porque <star 1> e <star 2>'
        literal = self.getStubLiteral(text)
        
        result = replace(literal, environ)
        assert result == 'Meu nome eh a porque b e c'

    def test_replaceGlobals(self):
        from aerolito.pattern import replace
        environ = {
            'userid': 1,
            'globals': {
                'botname': 'chapolin',
                'version': 'v0.1'
            },
            'session': {1:{}}

        }

        text = 'Meu nome eh <botname>, <version>'
        literal = self.getStubLiteral(text)
        
        result = replace(literal, environ)
        assert result == 'Meu nome eh chapolin, v0.1'

    def test_replaceLocals(self):
        from aerolito.pattern import replace
        environ = {
            'userid': 1,
            'globals': {},
            'session': {1:{
                'stars':[],
                'locals': {
                    'name': 'Renato',
                    'lastname': 'Pereira'
                }
            }}
        }

        text = 'Meu nome eh <name> <lastname>'
        literal = self.getStubLiteral(text)
        
        result = replace(literal, environ)
        assert result == 'Meu nome eh Renato Pereira'

    def test_replace_notFind(self):
        from aerolito.pattern import replace
        environ = {
            'userid': 1,
            'globals': {},
            'session': {1:{
                'stars':[],
                'locals': {}
            }}
        }

        text = 'Meu nome eh <name>'
        literal = self.getStubLiteral(text)
        
        result = replace(literal, environ)
        assert result == 'Meu nome eh '

    def test_replaceInteger(self):
        from aerolito.pattern import replace
        environ = {
            'userid': 1,
            'globals': {},
            'session': {1:{
                'stars':[],
                'locals': {}
            }}
        }

        text = 2
        literal = self.getStubLiteral(text)
        
        result = replace(literal, environ)
        assert result == 2


        
if __name__ == '__main__':
    unittest.main()
