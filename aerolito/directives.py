# -*- coding:utf-8 -*-
# Copyright (c) 2011 Renato de Pontes Pereira, renato.ppontes at gmail dot com
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

# Directive pool is used to stores user defined directives, registered by 
# ``register_directive``
_directive_pool = {}

def register_directive(alias, directive):
    _directive_pool[alias] = directive

class Directive(object):
    u"""
    Directive super class. Inherit this class and override run's method for new
    directives.
    """
    def __init__(self, environ):
        self.environ = environ

    def __call__(self, params):
        return self.run(*params)

    def run(self, *params):
        raise Exception(u'Not Implemented')

class Define(Directive):
    u"""
    Directive ``define`` store a given ``value`` in a ``variable`` in local 
    variables.
    """
    def run(self, variable, value):
        session = self.environ['session'][self.environ['userid']]
        session['locals'][variable] = value

        return True

class Delete(Directive):
    u"""
    Directive ``delete`` removes a ``variable`` of local variables.
    """
    def run(self, variable):
        session = self.environ['session'][self.environ['userid']]
        del session['locals'][variable]

        return True

class IsDefined(Directive):
    u"""
    Directive ``isdefined`` verifies if ``variable`` IS IN local vars.
    """
    def run(self, variable):
        session = self.environ['session'][self.environ['userid']]
        return variable in session['locals']

class IsNotDefined(Directive):
    u"""
    Directive ``isnotdefined`` verifies if ``variable IS NOT IN local vars.
    """
    def run(self, variable):
        session = self.environ['session'][self.environ['userid']]
        return variable not in session['locals']

class Equal(Directive):
    u"""
    Directive ``equal`` compares two values, return True if both are the same.
    """
    def run(self, value1, value2):
        return value1 == value2

class NotEqual(Directive):
    u"""
    Directive ``notequal`` compares two values, return True if both are not
    equals.
    """
    def run(self, value1, value2):
        return value1 != value2

class GreaterThan(Directive):
    u"""
    Directive ``greaterthan`` compares if a value1 is greater than value2.
    """
    def run(self, value1, value2):
        return value1 > value2

class LessThan(Directive):
    u"""
    Directive ``lessthan`` compares if a value1 is less than value2.
    """
    def run(self, value1, value2):
        return value1 < value2

class GreaterEqual(Directive):
    u"""
    Directive ``greaterequal`` compares if a value1 is greater or equals to 
    value2.
    """
    def run(self, value1, value2):
        return value1 >= value2

class LessEqual(Directive):
    u"""
    Directive ``lessequal`` compares if a value1 is less of equals to value2.
    """
    def run(self, value1, value2):
        return value1 <= value2

