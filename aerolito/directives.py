# -*- coding:utf-8 -*-

class Directive(object):
    def __init__(self, environ):
        self.environ = environ

    def __call__(self, params):
        return self.run(*params)

    def run(self, *params):
        raise Exception(u'Not Implemented')

class Define(Directive):
    def run(self, variable, value):
        session = self.environ['session'][self.environ['userid']]
        session['locals'][variable] = value

        return True

class Delete(Directive):
    def run(self, variable):
        session = self.environ['session'][self.environ['userid']]
        del session['locals'][variable]

        return True

class IsDefined(Directive):
    def run(self, variable):
        session = self.environ['session'][self.environ['userid']]
        return variable in session['locals']

class IsNotDefined(Directive):
    def run(self, variable):
        session = self.environ['session'][self.environ['userid']]
        return variable not in session['locals']

class Equal(Directive):
    def run(self, variable1, variable2):
        return variable1 == variable2

class NotEqual(Directive):
    def run(self, variable1, variable2):
        return variable1 != variable2

class GreaterThan(Directive):
    def run(self, variable1, variable2):
        return variable1 > variable2

class LessThan(Directive):
    def run(self, variable1, variable2):
        return variable1 < variable2

class GreaterEqual(Directive):
    def run(self, variable1, variable2):
        return variable1 >= variable2

class LessEqual(Directive):
    def run(self, variable1, variable2):
        return variable1 <= variable2

