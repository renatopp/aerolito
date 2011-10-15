# -*- coding:utf-8 -*-
import unittest

class TestReplace(unittest.TestCase):
    """Test ``pattern.replace`` function"""

    def get_stub_literal(self, value):
        class Literal: pass
        literal = Literal
        literal._value = value
        return literal

    def test_replace_star(self):
        """Test replace literal with star vars"""
        from aerolito.pattern import replace
        environ = {
            'user_id': 1,
            'globals': {},
            'session': {1: {'stars': ['a', 'b', 'c']}}
        }

        text = 'My name is <star> because <star 1> and <star 2>'
        literal = self.get_stub_literal(text)
        
        result = replace(literal, environ)
        assert result == 'My name is a because b and c'

    def test_replace_globals(self):
        """Test replace literal with globals vars"""
        from aerolito.pattern import replace
        environ = {
            'user_id': 1,
            'globals': {
                'botname': 'chapolin',
                'version': 'v0.1'
            },
            'session': {1:{}}

        }

        text = 'My name is <botname>, <version>'
        literal = self.get_stub_literal(text)
        
        result = replace(literal, environ)
        assert result == 'My name is chapolin, v0.1'

    def test_replace_locals(self):
        """Test replace literal with locals vars"""
        from aerolito.pattern import replace
        environ = {
            'user_id': 1,
            'globals': {},
            'session': {1:{
                'stars':[],
                'locals': {
                    'name': 'Renato',
                    'lastname': 'Pereira'
                }
            }}
        }

        text = 'My name is <name> <lastname>'
        literal = self.get_stub_literal(text)
        
        result = replace(literal, environ)
        assert result == 'My name is Renato Pereira'

    def test_replace_notfound(self):
        """Test replace when key is not found in stars, globals or locals"""
        from aerolito.pattern import replace
        environ = {
            'user_id': 1,
            'globals': {},
            'session': {1:{
                'stars': [],
                'locals': {}
            }}
        }

        text = 'My name is <name>'
        literal = self.get_stub_literal(text)
        
        result = replace(literal, environ)
        assert result == 'My name is '

    def test_replace_notfound_integer(self):
        """Test replace when key is not found and pattern is an integer"""
        from aerolito.pattern import replace
        environ = {
            'user_id': 1,
            'globals': {},
            'session': {1:{
                'stars': [],
                'locals': {}
            }}
        }

        text = 2
        literal = self.get_stub_literal(text)
        
        result = replace(literal, environ)
        assert result == 2
        
if __name__ == '__main__':
    unittest.main()
