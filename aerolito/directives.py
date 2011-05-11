# -*- coding:utf-8 -*-

class Directive(object):
    # kernel/variables to __init__

    def __call__(self):
        # pass variables, params, doknow
        pass

class Define(Directive):
    def run(self, variable, value):
        pass

class IsDefined(Directive):
    def run(self, variable, value):
        pass

class Equal(Directive):
    def run(self, *variables):
        pass

class NotEqual(Directive):
    def run(self, *variables):
        pass

class GreaterThan(Directive):
    def run(self, *variables):
        pass

class LessThan(Directive):
    def run(self, *variables):
        pass

class GreaterEqual(Directive):
    def run(self, *variables):
        pass

class LessEqual(Directive):
    def run(self, *variables):
        pass

class Delete(Directive):
    def run(self, *variables):
        pass
