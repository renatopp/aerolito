# -*- coding:utf-8 -*-
import unittest

class TestPatternConvertions(unittest.TestCase):
    def get_target(self, *args, **kw):
        if len(args) < 2 and 'environ' not in kw:
            kw['environ'] = self.get_stub_environ()
        from aerolito.pattern import Pattern
        return Pattern(*args, **kw)

    def get_pattern(self):
        p = {'after': ['teste', 'abc * jabis'],
                'in': ['lala', 2, 'asdf?!'],
               'out': ['blah <variavel>'],
              'post': [{'add': [2, 3]}],
              'when': [{'isdefined': 'blah'}]}
        
        return p

    def get_stub_environ(self):
        environ = {
            'directives': {
                'add': lambda v: v[0]+v[1],
                'isdefined': lambda v:True,
            },
            'user_id':1,
            'globals': {},
            'synonyms': {},
            'meanings': {},
            'session': {1: {'stars': [], 'locals': {},}}
        }

        return environ

    def test_convert_after_with_list(self):
        p = self.get_pattern()
        pattern = self.get_target(p)

        assert len(pattern._after) == 2
        assert pattern._after[0]._expression == u'^teste$'
        assert pattern._after[1]._expression == u'^abc(.*)jabis$'

    def test_convert_after_with_string(self):
        p = self.get_pattern()
        p['after'] = 'renato *'
        pattern = self.get_target(p)

        assert len(pattern._after) == 1
        assert pattern._after[0]._expression == u'^renato(.*)$'

    def test_convert_after_without_pattern(self):
        p = self.get_pattern()
        del p['after']
        pattern = self.get_target(p)

        assert pattern._after is None

    def test_convert_after_badvalue(self):
        from aerolito.exceptions import InvalidTagValue
        p = self.get_pattern()
        p['after'] = None
        self.assertRaises(InvalidTagValue, self.get_target, p)

        p['after'] = ''
        self.assertRaises(InvalidTagValue, self.get_target, p)

    def test_convert_in_with_list(self):
        p = self.get_pattern()
        pattern = self.get_target(p)

        assert len(pattern._in) == 3
        assert pattern._in[0]._expression == u'^lala$'
        assert pattern._in[1]._expression == u'^2$'
        assert pattern._in[2]._expression == u'^asdf\\?\\!$'

    def test_convert_in_with_string(self):
        p = self.get_pattern()
        p['in'] = 'renato *'
        pattern = self.get_target(p)

        assert len(pattern._in) == 1
        assert pattern._in[0]._expression == u'^renato(.*)$'

    def test_convert_in_without_pattern(self):
        p = self.get_pattern()
        del p['in']
        pattern = self.get_target(p)

        assert pattern._in is None

    def test_convert_in_badvalue(self):
        from aerolito.exceptions import InvalidTagValue
        p = self.get_pattern()
        p['in'] = None
        self.assertRaises(InvalidTagValue, self.get_target, p)

        p['in'] = ''
        self.assertRaises(InvalidTagValue, self.get_target, p)

    def test_convert_out_with_list(self):
        p = self.get_pattern()
        pattern = self.get_target(p)

        assert len(pattern._out) == 1
        assert pattern._out[0]._value == u'blah <variavel>'

    def test_convert_out_with_string(self):
        p = self.get_pattern()
        p['out'] = 'renato *'
        pattern = self.get_target(p)

        assert len(pattern._out) == 1
        assert pattern._out[0]._value == u'renato *'

    def test_convert_out_without_pattern(self):
        p = self.get_pattern()
        del p['out']
        pattern = self.get_target(p)

        assert pattern._out is None

    def test_convert_out_badvalue(self):
        from aerolito.exceptions import InvalidTagValue
        p = self.get_pattern()
        p['out'] = None
        self.assertRaises(InvalidTagValue, self.get_target, p)

        p['out'] = ''
        self.assertRaises(InvalidTagValue, self.get_target, p)

    def test_convert_when_with_list(self):
        p = self.get_pattern()
        environ = self.get_stub_environ()
        pattern = self.get_target(p, environ)

        assert len(pattern._when) == 1
        assert pattern._when[0]._directive == environ['directives']['isdefined']
        assert pattern._when[0].run(environ)

    def test_convert_when_with_dict(self):
        p = self.get_pattern()
        p['when'] = {'isdefined':'value'}
        environ = self.get_stub_environ()
        pattern = self.get_target(p, environ)

        assert len(pattern._when) == 1
        assert pattern._when[0]._directive == environ['directives']['isdefined']
        assert pattern._when[0].run(environ)

    def test_convert_when_without_pattern(self):
        p = self.get_pattern()
        del p['when']
        environ = self.get_stub_environ()
        pattern = self.get_target(p, environ)

        assert pattern._when is None

    def test_convert_when_badvalue(self):
        from aerolito.exceptions import InvalidTagValue
        p = self.get_pattern()
        p['when'] = None
        self.assertRaises(InvalidTagValue, self.get_target, p)

        p['when'] = 'aasdfokasdf'
        self.assertRaises(InvalidTagValue, self.get_target, p)

    def test_convert_post_with_list(self):
        p = self.get_pattern()
        environ = self.get_stub_environ()
        p['post'][0]['add'] = [5, 3]
        pattern = self.get_target(p, environ)

        assert len(pattern._post) == 1
        assert pattern._post[0]._directive == environ['directives']['add']
        assert pattern._post[0].run(environ) == 8

    def test_convert_post_with_dict(self):
        p = self.get_pattern()
        p['post'] = {'add':[2, 3]}
        environ = self.get_stub_environ()
        pattern = self.get_target(p, environ)

        assert len(pattern._post) == 1
        assert pattern._post[0]._directive == environ['directives']['add']
        assert pattern._post[0].run(environ) == 5

    def test_convert_post_without_pattern(self):
        p = self.get_pattern()
        del p['post']
        environ = self.get_stub_environ()
        pattern = self.get_target(p, environ)

        assert pattern._post is None

    def test_convert_post_badvalue(self):
        from aerolito.exceptions import InvalidTagValue
        p = self.get_pattern()
        p['post'] = None
        self.assertRaises(InvalidTagValue, self.get_target, p)

        p['post'] = 'aasdfokasdf'
        self.assertRaises(InvalidTagValue, self.get_target, p)

class TestPattern(unittest.TestCase):
    def get_target(self, *args, **kw):
        from aerolito.pattern import Pattern
        return Pattern(*args, **kw)

    def get_pattern(self):
        p = {'after': ['Who is there?'],
                'in': ['lala', 2, 'asdf?!'],
               'out': ['blah <variavel>'],
              'post': [{'add': [2, 3]}],
              'when': [{'isdefined': 'blah'}]}
        
        return p

    def get_stub_environ(self):
        def define(v):
            define.environ[v[0]] = v[1]
            return True
        
        environ = {
            'user_id':1,
            'directives': {
                'add': lambda v: v[0]+v[1],
                'define': define,
                'isdefined': lambda x:x[0]=='Renato',
            },
            'globals': {},
            'synonyms': {},
            'meanings': {},
            'session': {
                1: {
                    'stars': [],
                    'locals': {
                    },
                }
            }
        }

        environ['directives']['define'].environ = environ

        return environ

    def test_match_in(self):
        p = {'in': 'Knock knock *'}
        environ = self.get_stub_environ()
        pattern = self.get_target(p, environ)

        assert pattern.match('Knock KNOCK', environ)
        assert not pattern.match('knock nhok', environ)

        assert pattern.match('Knock KNOCK block', environ)
        assert len(environ['session'][1]['stars']) == 1
        assert environ['session'][1]['stars'][0] == 'block'

    def test_match_after(self):
        p = {'after': 'abc * ghi'}
        environ = self.get_stub_environ()
        pattern = self.get_target(p, environ)

        environ['session'][1]['responses-normalized'] = ['renato ghi']
        assert not pattern.match('', environ)

        environ['session'][1]['responses-normalized'] = ['abc renato ghi']
        assert pattern.match('', environ)
        assert len(environ['session'][1]['stars']) == 1
        assert environ['session'][1]['stars'][0] == 'renato'
    
    def test_match_when(self):
        p = {'when': [{'isdefined': '<name>'}], 'in':'hello'}
        environ = self.get_stub_environ()
        pattern = self.get_target(p, environ)

        assert not pattern.match('hello', environ)

        environ['session'][1]['locals']['name'] = 'Bozo'
        assert not pattern.match('hello', environ)

        environ['session'][1]['locals']['name'] = 'Renato'
        print pattern._when
        assert pattern.match('hello', environ)
    
    def test_choice_output(self):
        environ = self.get_stub_environ()
        
        pattern = self.get_target({'out':'renato'}, environ)
        assert pattern.choice_output(environ) == 'renato'

        pattern = self.get_target({'out':['bozo']}, environ)
        assert pattern.choice_output(environ) == 'bozo'

        pattern = self.get_target({'out':u'olá <name>'}, environ)
        environ['globals']['name'] = 'renato'
        assert pattern.choice_output(environ) == u'olá renato'

    def test_execute_post(self):
        environ = self.get_stub_environ()
        pattern = self.get_target({'post':[{'define':['abc', 'hehe']}]}, environ)
        pattern.execute_post(environ)

        assert environ['abc'] == 'hehe'

        

if __name__ == '__main__':
    unittest.main()
