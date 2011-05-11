# -*- coding: utf-8 -*-

import re
import random
from aerolito import exceptions

def replace(literal, environ):
    """
    Replace a literal value with variable in environ. 
    
    The vars replaced are in format <variablename>. If variablename is not 
    defined, the value is replaced by an empty string.
    """
    session = environ['session'][environ['userid']]
    p = '\<([\d|\s|\w]*)\>'
    _vars = re.findall(p, unicode(literal._value), re.I)

    result = literal._value
    for var in _vars:
        # star
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
    Literal objects represents an entry of ``pattern-out``.
    """

    def __init__(self, value):
        self._value = value


class Action(object):
    """
    Action objects represents an entry of ``pattern-when`` and ``pattern-post``

    Actions are the link between aerolito and python function.
    """

    def __init__(self, function, params):
        """
        Constructor receive a python function and a params (list of literals)
        """
        self._function = function
        self._params = params

    def run(self, params, environ):
        """
        Execute the ``function`` applying ``params``.

        The ``params`` is a list/tuple of values, these values are given in 
        discussion files (.yml)
        """
        return self._function(*params, environ=environ)


class Regex(object):
    """
    Regex objects represents an entry of ``pattern-after`` and ``pattern-in``

    Regex convert an entry value of ``pattern-after`` and ``pattern-in`` to a
    regular expression. This class is responsible by match user input and 
    retrieve *star* values.
    """

    def __init__(self, text):
        """
        Receive a text and converts to regular expression.
        """
        self._expression = re.escape(text)
        self._expression = self._expression.replace('\\*', '(.*)')
        self._expression = self._expression.replace('\\\\(.*)', '\*')
        self._expression = re.sub('(\\\ )+\(\.\*\)', '(.*)', self._expression)
        self._expression = re.sub('\(\.\*\)(\\\ )+', '(.*)', self._expression)
        self._expression = '^%s$'%self._expression 
        
        self._stars = None
    
    def match(self, value):
        """
        Try to match ``value`` to ``expression`` and retrieve the *star* 
        variables of value.
        """
        m = re.match(self._expression, value, re.I)
        if m:
            self._stars = [x.strip() for x in m.groups()]
            return True
        else:
            self._stars = None
            return False


class Pattern(object):
    """
    Represents a conversation pattern.
    """

    def __init__(self, p, environ):
        self._after = self.__convertRegex(p, 'after')
        self._in = self.__convertRegex(p, 'in')
        self._out = self.__convertLiteral(p, 'out')
        self._when = self.__convertAction(p, 'when', environ)
        self._post = self.__convertAction(p, 'post', environ)

        self._stars = None

    def __convertRegex(self, p, tag):
        if p.has_key(tag):
            tagValues = p[tag]
            if tagValues is None or tagValues == u'':
                raise exceptions.InvalidTagValueException(
                                    'Invalid value for tag %s.'%tag)

            if isinstance(tagValues, (tuple, list)):
                return [Regex(unicode(x)) for x in tagValues]
            else:
                return [Regex(unicode(tagValues))]
        else:
            return None

    def __convertLiteral(self, p, tag):
        if p.has_key(tag):
            tagValues = p[tag]
            if tagValues is None or tagValues == u'':
                raise exceptions.InvalidTagValueException(
                                    'Invalid value for tag %s.'%tag)

            if isinstance(tagValues, (tuple, list)):
                return [Literal(unicode(x)) for x in tagValues]
            else:
                return [Literal(unicode(tagValues))]
        else:
            return None

    def __convertAction(self, p, tag, environ):
        if p.has_key(tag):
            tagValues = p[tag]
            actions = []

            if isinstance(tagValues, (tuple, list)):
                for d in tagValues:
                    for k, p in d.iteritems():
                        if isinstance(p, (tuple, list)):
                            params = [Literal(x) for x in p]
                        else:
                            params = [Literal(p)]
                        action = Action(environ['directives'][k], params)
                        actions.append(action)
            elif isinstance(tagValues, dict):
                for k, p in tagValues.iteritems():
                    if isinstance(p, (tuple, list)):
                        params = [Literal(x) for x in p]
                    else:
                        params = [Literal(p)]
                    action = Action(environ['directives'][k], params)
                    actions.append(action)
            else:
                raise exceptions.InvalidTagValueException(
                                    'Invalid value for tag %s.'%tag)
            
            return actions
        else:
            return None


    def match(self, value, environ):
        self._stars = None
        session = environ['session'][environ['userid']]

        if self._after:
            for regex in self._after:
                if regex.match(environ['lastresponse']):
                    self._stars = regex._stars
                    session['stars'] = regex._stars
                    break
            else:
                return False

        if self._in:
            for regex in self._in:
                if regex.match(value):
                    self._stars = regex._stars
                    session['stars'] = regex._stars
                    break
            else:
                return False

        if self._when:
            for action in self._when:
                if action._params:
                    params = [replace(x, environ) for x in action._params]
                else:
                    params = []

                if not action.run(params, environ=environ):
                    return False
        
        return True

    def choiceOutput(self, environ):
        return replace(random.choice(self._out), environ)
    
    def executePost(self, environ):
        if self._post:
            for action in self._post:
                if action._params:
                    params = [replace(x, environ) for x in action._params]
                else:
                    params = []

                action.run(params, environ=environ)
