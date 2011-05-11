# -*- coding:utf-8 -*-
import unittest

class TestPatternConvertions(unittest.TestCase):
    def getTarget(self, *args, **kw):
        if len(args) < 2 and 'environ' not in kw:
            kw['environ'] = self.getStubEnviron()
        from aerolito.pattern import Pattern
        return Pattern(*args, **kw)

    def getPattern(self):
        p = {'after': ['teste', 'abc * jabis'],
                'in': ['lala', 2, 'asdf?!'],
               'out': ['blah <variavel>'],
              'post': [{'add': [2, 3]}],
              'when': [{'isdefined': 'blah'}]}
        
        return p

    def getStubEnviron(self):
        environ = {
            'directives': {
                'add': lambda x, y, environ: x+y,
                'isdefined': lambda x, environ:True,
            }
        }

        return environ


    def test_convertAfter_WList(self):
        p = self.getPattern()
        pattern = self.getTarget(p)

        assert len(pattern._after) == 2
        assert pattern._after[0]._expression == u'^teste$'
        assert pattern._after[1]._expression == u'^abc(.*)jabis$'

    def test_convertAfter_WString(self):
        p = self.getPattern()
        p['after'] = 'renato *'
        pattern = self.getTarget(p)

        assert len(pattern._after) == 1
        assert pattern._after[0]._expression == u'^renato(.*)$'

    def test_convertAfter_WoPattern(self):
        p = self.getPattern()
        del p['after']
        pattern = self.getTarget(p)

        assert pattern._after is None

    def test_convertAfter_BadValue(self):
        from aerolito.exceptions import InvalidTagValueException
        p = self.getPattern()
        p['after'] = None
        self.assertRaises(InvalidTagValueException, self.getTarget, p)

        p['after'] = ''
        self.assertRaises(InvalidTagValueException, self.getTarget, p)


    def test_convertIn_WList(self):
        p = self.getPattern()
        pattern = self.getTarget(p)

        assert len(pattern._in) == 3
        assert pattern._in[0]._expression == u'^lala$'
        assert pattern._in[1]._expression == u'^2$'
        assert pattern._in[2]._expression == u'^asdf\\?\\!$'

    def test_convertIn_WString(self):
        p = self.getPattern()
        p['in'] = 'renato *'
        pattern = self.getTarget(p)

        assert len(pattern._in) == 1
        assert pattern._in[0]._expression == u'^renato(.*)$'

    def test_convertIn_WoPattern(self):
        p = self.getPattern()
        del p['in']
        pattern = self.getTarget(p)

        assert pattern._in is None

    def test_convertIn_BadValue(self):
        from aerolito.exceptions import InvalidTagValueException
        p = self.getPattern()
        p['in'] = None
        self.assertRaises(InvalidTagValueException, self.getTarget, p)

        p['in'] = ''
        self.assertRaises(InvalidTagValueException, self.getTarget, p)

    
    def test_convertOut_WList(self):
        p = self.getPattern()
        pattern = self.getTarget(p)

        assert len(pattern._out) == 1
        assert pattern._out[0]._value == u'blah <variavel>'

    def test_convertIn_WString(self):
        p = self.getPattern()
        p['out'] = 'renato *'
        pattern = self.getTarget(p)

        assert len(pattern._out) == 1
        assert pattern._out[0]._value == u'renato *'

    def test_convertIn_WoPattern(self):
        p = self.getPattern()
        del p['out']
        pattern = self.getTarget(p)

        assert pattern._out is None

    def test_convertIn_BadValue(self):
        from aerolito.exceptions import InvalidTagValueException
        p = self.getPattern()
        p['out'] = None
        self.assertRaises(InvalidTagValueException, self.getTarget, p)

        p['out'] = ''
        self.assertRaises(InvalidTagValueException, self.getTarget, p)


    def test_convertWhen_WList(self):
        p = self.getPattern()
        environ = self.getStubEnviron()
        pattern = self.getTarget(p, environ)

        assert len(pattern._when) == 1
        assert pattern._when[0]._function == environ['directives']['isdefined']
        assert pattern._when[0].run(['lalal'], None)

    def test_convertWhen_WDict(self):
        p = self.getPattern()
        p['when'] = {'isdefined':'value'}
        environ = self.getStubEnviron()
        pattern = self.getTarget(p, environ)

        assert len(pattern._when) == 1
        assert pattern._when[0]._function == environ['directives']['isdefined']
        assert pattern._when[0].run(['lalal'], None)

    def test_convertWhen_WoPattern(self):
        p = self.getPattern()
        del p['when']
        environ = self.getStubEnviron()
        pattern = self.getTarget(p, environ)

        assert pattern._when is None

    def test_convertWhen_BadValue(self):
        from aerolito.exceptions import InvalidTagValueException
        p = self.getPattern()
        p['when'] = None
        self.assertRaises(InvalidTagValueException, self.getTarget, p)

        p['when'] = 'aasdfokasdf'
        self.assertRaises(InvalidTagValueException, self.getTarget, p)


    def test_convertPost_WList(self):
        p = self.getPattern()
        environ = self.getStubEnviron()
        pattern = self.getTarget(p, environ)

        assert len(pattern._post) == 1
        assert pattern._post[0]._function == environ['directives']['add']
        assert pattern._post[0].run([5, 3], None) == 8

    def test_convertPost_WDict(self):
        p = self.getPattern()
        p['post'] = {'add':[2, 3]}
        environ = self.getStubEnviron()
        pattern = self.getTarget(p, environ)

        assert len(pattern._post) == 1
        assert pattern._post[0]._function == environ['directives']['add']
        assert pattern._post[0].run([2, 3], None) == 5

    def test_convertPost_WoPattern(self):
        p = self.getPattern()
        del p['post']
        environ = self.getStubEnviron()
        pattern = self.getTarget(p, environ)

        assert pattern._post is None

    def test_convertPost_BadValue(self):
        from aerolito.exceptions import InvalidTagValueException
        p = self.getPattern()
        p['post'] = None
        self.assertRaises(InvalidTagValueException, self.getTarget, p)

        p['post'] = 'aasdfokasdf'
        self.assertRaises(InvalidTagValueException, self.getTarget, p)


class TestPattern(unittest.TestCase):
    def getTarget(self, *args, **kw):
        from aerolito.pattern import Pattern
        return Pattern(*args, **kw)

    def getPattern(self):
        p = {'after': ['Who is there?'],
                'in': ['lala', 2, 'asdf?!'],
               'out': ['blah <variavel>'],
              'post': [{'add': [2, 3]}],
              'when': [{'isdefined': 'blah'}]}
        
        return p

    def getStubEnviron(self):
        def define(x, v, environ):
            environ[x] = v
            return True

        environ = {
            'userid':1,
            'directives': {
                'add': lambda x, y, environ: x+y,
                'define': define,
                'isdefined': lambda x, environ:x=='Renato',
            },
            'globals': {},
            'session': {
                1: {
                    'stars': [],
                    'locals': {

                    },
                }
            }
        }

        return environ

    def test_matchIn(self):
        p = {'in': 'Knock knock *'}
        environ = self.getStubEnviron()
        pattern = self.getTarget(p, environ)

        assert pattern.match('Knock KNOCK', environ)
        assert not pattern.match('knock nhok', environ)

        assert pattern.match('Knock KNOCK block', environ)
        assert len(pattern._stars) == 1
        assert pattern._stars[0] == 'block'

    def test_matchAfter(self):
        p = {'after': 'abc * ghi'}
        environ = self.getStubEnviron()
        pattern = self.getTarget(p, environ)

        environ['lastresponse'] = 'renato ghi'
        assert not pattern.match('', environ)

        environ['lastresponse'] = 'abc renato ghi'
        assert pattern.match('', environ)
        assert len(pattern._stars) == 1
        assert pattern._stars[0] == 'renato'

    def test_matchWhen(self):
        p = {'when': [{'isdefined': '<name>'}]}
        environ = self.getStubEnviron()
        pattern = self.getTarget(p, environ)

        assert not pattern.match('', environ)

        environ['session'][1]['locals']['name'] = 'Bozo'
        assert not pattern.match('', environ)

        environ['session'][1]['locals']['name'] = 'Renato'
        assert pattern.match('', environ)
    
    def test_choiceOutput(self):
        environ = self.getStubEnviron()
        
        pattern = self.getTarget({'out':'renato'}, environ)
        assert pattern.choiceOutput(environ) == 'renato'

        pattern = self.getTarget({'out':['bozo']}, environ)
        assert pattern.choiceOutput(environ) == 'bozo'

        pattern = self.getTarget({'out':u'olá <name>'}, environ)
        environ['globals']['name'] = 'renato'
        assert pattern.choiceOutput(environ) == u'olá renato'

    def test_executePost(self):
        environ = self.getStubEnviron()
        pattern = self.getTarget({'post':[{'define':['abc', 'hehe']}]}, environ)
        pattern.executePost(environ)

        assert environ['abc'] == 'hehe'

        

if __name__ == '__main__':
    unittest.main()
