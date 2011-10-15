# -*- coding:utf-8 -*-
import unittest

class TestLiteral(unittest.TestCase):
    """Tests ``pattern.Literal`` class"""

    def get_target(self, *args, **kw):
        from aerolito.pattern import Literal
        return Literal(*args, **kw)

    def test_init(self):
        literal = self.get_target(u'Hello <name>!')
        assert literal._value == u'Hello <name>!'


if __name__ == '__main__':
    unittest.main()
