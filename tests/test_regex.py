# -*- coding:utf-8 -*-
import unittest

class TestRegex(unittest.TestCase):
    def getTarget(self, *args, **kw):
        from aerolito.pattern import Regex
        return Regex(*args, **kw)

    def test_init(self):
        regex = self.getTarget(u'Hello')
        
        assert regex._expression == u'^Hello$'

    def test_makeSimpleExpression(self):
        regex = self.getTarget(u'H?e.l|l{o}! World')
        assert regex._expression == u'^H\\?e\\.l\\|l\\{o\\}\\!\\ World$', regex._expression
        
    def test_makeStarExpression(self):
        regex = self.getTarget(u'*')
        assert regex._expression == u'^(.*)$'

        regex = self.getTarget(u'\\*')
        assert regex._expression == u'^\\*$'

        regex = self.getTarget(u'    *    ')
        assert regex._expression == u'^(.*)$', regex._expression
    
    def test_makeAdvancedExpression(self):
        regex = self.getTarget(u'Meu nome e *!')
        assert regex._expression == u'^Meu\\ nome\\ e(.*)\\!$'

        regex = self.getTarget(u'Super \*.\* Exp!ao * heh')
        assert regex._expression == u'^Super\\ \\*\\.\\*\\ Exp\\!ao(.*)heh$'

    def test_matchSimple(self):
        regex = self.getTarget(u'Hello! \*.\*')
        assert regex.match(u'Hello! *.*')

    def test_matchCaseInsensitive(self):
        regex = self.getTarget(u'Hello Friend!')
        assert regex.match(u'heLLO fRIEND!')

    def test_matchStar(self):
        regex = self.getTarget(u'Hello *')
        assert regex.match(u'Hello Renato')

    def test_getStar(self):
        regex = self.getTarget(u'* first * sec \* ond *')
        assert regex.match(u'TESTE first T E S T E sec * ond')
        
        star1 = regex._stars[0]
        assert star1 == 'TESTE'

        star2 = regex._stars[1]
        assert star2 == 'T E S T E'

        star3 = regex._stars[2]
        assert star3 == ''
        

        

if __name__ == '__main__':
    unittest.main()
