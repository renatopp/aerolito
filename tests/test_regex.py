# -*- coding:utf-8 -*-
import unittest

class TestRegex(unittest.TestCase):
    def get_target(self, *args, **kw):
        from aerolito.pattern import Regex
        return Regex(*args, **kw)

    def test_init(self):
        regex = self.get_target(u'Hello')
        assert regex._expression == u'^Hello$'

    def test_init_with_ignore(self):
        regex = self.get_target(u',H!e,l,,,lo!', [u',', u'!'])
        assert regex._expression == u'^Hello$'

    def test_make_simple_expression(self):
        regex = self.get_target(u'H?e.l|l{o}! World')
        assert regex._expression == u'^H\\?e\\.l\\|l\\{o\\}\\!\\ World$', regex._expression
        
    def test_make_star_expression(self):
        regex = self.get_target(u'*')
        assert regex._expression == u'^(.*)$'

        regex = self.get_target(u'\\*')
        assert regex._expression == u'^\\*$'

        regex = self.get_target(u'    *    ')
        assert regex._expression == u'^(.*)$', regex._expression
    
    def test_make_advanced_expression(self):
        regex = self.get_target(u'Meu nome e *!')
        assert regex._expression == u'^Meu\\ nome\\ e(.*)\\!$'

        regex = self.get_target(u'Super \*.\* Exp!ao * heh')
        assert regex._expression == u'^Super\\ \\*\\.\\*\\ Exp\\!ao(.*)heh$'

    def test_match_simple(self):
        regex = self.get_target(u'Hello! \*.\*')
        assert regex.match(u'Hello! *.*')

    def test_match_case_insensitive(self):
        regex = self.get_target(u'Hello Friend!')
        assert regex.match(u'heLLO fRIEND!')

    def test_match_star(self):
        regex = self.get_target(u'Hello *')
        assert regex.match(u'Hello Renato')

    def test_match_with_ignore(self):
        regex = self.get_target(u'Hello, there!', [u',', '!'])
        assert regex.match(u'Hello there')
        assert regex.match(u'Hello there!!!')

    def test_get_star(self):
        regex = self.get_target(u'* first * sec \* ond *')
        assert regex.match(u'TESTE first T E S T E sec * ond')
        
        star1 = regex._stars[0]
        assert star1 == 'TESTE'

        star2 = regex._stars[1]
        assert star2 == 'T E S T E'

        star3 = regex._stars[2]
        assert star3 == ''

if __name__ == '__main__':
    unittest.main()
