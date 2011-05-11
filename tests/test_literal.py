# -*- coding:utf-8 -*-
import unittest

class TestLiteral(unittest.TestCase):
    def getTarget(self, *args, **kw):
        from aerolito.pattern import Literal
        return Literal(*args, **kw)

    def test_init(self):
        literal = self.getTarget(u'Olá <name>!')
        assert literal._value == u'Olá <name>!'
        
if __name__ == '__main__':
    unittest.main()
