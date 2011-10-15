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

import re
import random
from aerolito import exceptions
from aerolito.utils import remove_accents
from aerolito.utils import normalize_input
from aerolito.utils import get_meanings

def replace(literal, environ):
    """
    Replace the value of an ``Literal`` by variables in ``_environ`` 
    dictionary.

    This function looks for variables in the sequence:

    1. ``session['stars']``
    2. ``_environ['globals']``
    3. ``session['locals']``
    """

    session = environ['session'][environ['user_id']]
    p = r'\<([\d|\s|\w]*)\>'
    _vars = re.findall(p, unicode(literal._value), re.I)

    result = literal._value
    for var in _vars:
        # Decompõe a expressão em <variavel parametro1 parametroN>
        temp = var.split()
        varname = temp[0]
        params = temp[1:]
        
        if varname == 'star':
            index = int(params[0]) if params else 0
            result = result.replace('<%s>'%var, session['stars'][index])
        elif varname in environ['globals']:
            result = result.replace('<%s>'%var, environ['globals'][varname])
        elif varname in session['locals']:
            result = result.replace('<%s>'%var, session['locals'][varname])
        else:
            result = result.replace('<%s>'%var, '')

    return result


class Literal(object):
    """
    A Literal object represents an element of ``pattern:out`` tag.
    """

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return '<Literal %s>' % self._value


class Action(object):
    """
    The Actions are representations of the elements of ``pattern:when`` tag and
    ``pattern:post``. They are the link of Aerolito and python functions.
    """

    def __init__(self, directive, params):
        """
        Receives a directive and a parameters list.
        """
        self._directive = directive
        self._params = params

    def run(self, environ):
        """
        Executes  the ``_directive`` with ``_params`` and the ``_environ``
        variable.
        """
        params = []
        if self._params:
            params = [replace(x, environ) for x in self._params]
            
        return self._directive(params)


class Regex(object):
    """
    The Regex objects represents the elements of ``pattern:after`` tag and 
    ``pattern:in``. It converts the text received in initialization into 
    regular expressions. This class is responsible to accept (or not) an user 
    input.

    After matchs some tag. A Regex object stores the values grouped by special
    expression "\*".
    """

    def __init__(self, text, ignore=None):
        """
        Receive a text and converts it into a regular expression.
        """
        # self._expression = remove_accents(text)
        if ignore:
            ignore = '|'.join([re.escape(i) for i in ignore])
            self._ignore = re.compile('[%s]'%ignore)
            self._expression = re.sub(self._ignore, '', text)
        else:
            self._ignore = None
            self._expression = text

        self._expression = re.escape(self._expression)
        self._expression = self._expression.replace('\\*', '(.*)')
        self._expression = self._expression.replace('\\\\(.*)', '\*')
        self._expression = re.sub('(\\\ )+\(\.\*\)', '(.*)', self._expression)
        self._expression = re.sub('\(\.\*\)(\\\ )+', '(.*)', self._expression)
        self._expression = '^%s$'%self._expression 
        
        self._stars = None
    
    def match(self, value):
        """
        Try to match the ``value`` with the ``_expression``. If matched, it 
        extract the ``<star>`` values.
        """
        if self._ignore:
            value = re.sub(self._ignore, '', value)

        m = re.match(self._expression, value, re.I)
        if m:
            self._stars = [x.strip() for x in m.groups()]
            return True
        else:
            self._stars = None
            return False

    def __repr__(self):
        return '<Regex %s>' % self._expression


class Pattern(object):
    u"""
    Represents a conversation pattern.

    A patterns is divided into 7 tags, used in the following order:

    1. **mean**: considered as local meaning, is used like a meaning file.
    2. **ignore**: a string or a list of string with characters that will be 
       ignored in pattern match.
    3. **after**: condition to select the pattern. The value of the tag is 
       compared with the last response, if the values matchs the pattern is 
       valid.
    4. **in**: condition to select the pattern. The value of the tag is 
       compared with the user input.
    5. **when**: condition to select the pattern. Is a set of actions that must
       return True to validated the pattern.
    6. **out**: return values, they are the user response.
    7. **post**: set of actions that are executed after a pattern is accepted 
       and a response selected.
    """

    def __init__(self, p, environ):
        u"""
        Receive a dict ``p`` with the tags (that comes from conversation file)
        and the ``_environ`` variable.
        """
        self._mean = self.__convert_mean(p, environ)
        self._ignore = self.__convert_ignore(p, environ)
        self._after = self.__convert_regex(p, 'after', environ)
        self._in = self.__convert_regex(p, 'in', environ)
        self._out = self.__convert_literal(p, 'out', environ)
        self._when = self.__convert_action(p, 'when', environ)
        self._post = self.__convert_action(p, 'post', environ)

    def __convert_mean(self, p, environ=None):
        meanings = {}
        synonyms = environ['synonyms']
        if p.has_key('mean'):
            tagValues = p['mean']
            if tagValues is None:
                raise exceptions.InvalidTagValue(u'Invalid value for tag mean')

            for k in tagValues:
                key = remove_accents(k)
                meanings[key] = [normalize_input(v, synonyms) for v in tagValues[k]]
                
            return meanings
        else:
            return None

    def __convert_ignore(self, p, environ=None):
        if p.has_key('ignore'):
            if  isinstance(p['ignore'], (tuple, list)):
                tag_values = p['ignore']
            else:
                tag_values = list(str(p['ignore']))
        else:
            tag_values = None
        
        return tag_values
                

    def __convert_regex(self, p, tag, environ=None):
        u"""
        Converts the values of ``tag`` to ``Regex``s. Accepts a list of string 
        or just a string.
        """
        synonyms = environ['synonyms']
        meanings = environ['meanings']
        if p.has_key(tag):
            tagValues = p[tag]
            if tagValues is None or tagValues == u'':
                raise exceptions.InvalidTagValue(
                                    u'Invalid value for tag %s.'%tag)

            if isinstance(tagValues, (tuple, list)):
                values = tagValues
            else:
                values = [tagValues]

            normalized = [normalize_input(unicode(x), synonyms) for x in values]
            patterns = []
            for x in normalized:
                patterns.extend(get_meanings(x, meanings, self._mean))

            return [Regex(x, self._ignore) for x in patterns]
        else:
            return None

    def __convert_literal(self, p, tag, environ=None):
        u"""
        Converts the values of ``tag`` to ``Literal``s. Accepts a list of 
        string or just a string.
        """
        meanings = environ['meanings']
        if p.has_key(tag):
            tagValues = p[tag]
            if tagValues is None or tagValues == u'':
                raise exceptions.InvalidTagValue(
                                    'Invalid value for tag %s.'%tag)

            if isinstance(tagValues, (tuple, list)):
                values = tagValues
            else:
                values = [tagValues]

            patterns = []
            for x in values:
                patterns.extend(get_meanings(x, meanings, self._mean))

            return [Literal(unicode(x)) for x in patterns]
        else:
            return None

    def __convert_action(self, p, tag, environ):
        u"""
        Converts the values of ``tag`` to ``Action``s, an action just can be 
        created when there is a correspondent directive. An ``InvalidTagValue``
        is raised if there is no correspondent directive.

        This method accepts a list of dicts or just a dict. The dictionaries 
        can have more than one key, each key means a name of a directive and 
        the values are the parameters.
        """
        if p.has_key(tag):
            tagValues = p[tag]
            actions = []

            if isinstance(tagValues, dict):
                tagValues = [tagValues]

            if isinstance(tagValues, (tuple, list)):
                for d in tagValues:
                    for k, p in d.iteritems():
                        if isinstance(p, (tuple, list)):
                            params = [Literal(x) for x in p]
                        else:
                            params = [Literal(p)]
                        
                        if k not in environ['directives']:
                            raise exceptions.InvalidTagValue(
                                    u'Directive "%s" not found'%str(k))

                        action = Action(environ['directives'][k], params)
                        actions.append(action)
            else:
                raise exceptions.InvalidTagValue(
                                    u'Invalid value for tag %s.'%tag)
            
            return actions
        else:
            return None

    def match(self, value, environ):
        u"""
        Verify if ``value`` is associated with the pattern. The verification
        sequence is as follow:

        1. Tag After: at least one element of tag must be associated with the
           last response.
        2. Tag In: at least one element of tag must be associated with the 
           ``value``.
        3. Tag When: all actions of this tag must return True.

        A pattern just can match if all three conditions are accepted.
        """
        self._stars = None
        session = environ['session'][environ['user_id']]

        if self._after:
            for regex in self._after:
                if session['responses-normalized'] and \
                   regex.match(session['responses-normalized'][-1]):
                    session['stars'] = regex._stars
                    break
            else:
                return False

        if self._in:
            for regex in self._in:
                if regex.match(value):
                    session['stars'] = regex._stars
                    break
            else:
                return False

        if self._when:
            for action in self._when:
                if not action.run(environ):
                    return False
        
        return True

    def choice_output(self, environ):
        u"""
        Choices one random response, replacing the veriables
        """
        return replace(random.choice(self._out), environ)
    
    def execute_post(self, environ):
        u"""
        Executes the actions of post tag
        """
        if self._post:
            for action in self._post:
                action.run(environ)
