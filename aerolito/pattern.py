# -*- coding: utf-8 -*-

import re

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

    def __init__(self, function):
        """
        Constructor receive a python function.
        """
        self._function = function

    def run(self, params):
        """
        Execute the ``function`` applying ``params``.

        The ``params`` is a list/tuple of values, these values are given in 
        discussion files (.yml)
        """
        return self._function(*params)


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
    _after = None # Regex list
    _in = None # Regex list
    _when = None # Action list
    _out = None # Literal list
    _post = None # Action list

"""
class Literal:
    _value

class Regex:
    _expression
    _stars
    __call__() : bool

class Action:
    _function
    __call__()

class Pattern:
    _after = Regex list
    _in = Regex list
    _when = Action list
    _out = Literal list
    _post = Action list


class Kernel:
    __init__()
    load()
    respond()
"""