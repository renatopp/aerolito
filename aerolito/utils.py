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
"""
Utilities functions
"""

import re
import itertools
from aerolito import exceptions

substitute = [
    (u'ç', u'c'),
    (u'ã', u'a'),
    (u'á', u'a'),
    (u'à', u'a'),
    (u'â', u'a'),
    (u'ä', u'a'),
    (u'é', u'e'),
    (u'è', u'e'),
    (u'ê', u'e'),
    (u'ë', u'e'),
    (u'ó', u'o'),
    (u'ò', u'o'),
    (u'ô', u'o'),
    (u'õ', u'o'),
    (u'ö', u'o'),
    (u'í', u'i'),
    (u'ì', u'i'),
    (u'î', u'i'),
    (u'ï', u'i'),
    (u'ú', u'u'),
    (u'ù', u'u'),
    (u'û', u'u'),
    (u'ü', u'u'),
]

def remove_accents(text):
    u"""
    Removes accents of a ``text`` changing by correspondent letters, e.g.:

    >>> remove_accents(u'ã')
    'a'
    """
    for t, f in substitute:
        text = text.replace(t, f)
        text = text.replace(t.upper(), f.upper())

    return text

def get_meanings(text, meanings, localMeanings=None):
    u"""
    Replaces meaning tags by their values, using a meaning list.

    If a mean tag of ``text`` is searched in ``localMeaning`` first, if mean is
    not found, method try by global ``meanings``.
    """
    keys = re.findall('\(mean\|([^\)]*)\)', text)
    for key in keys:
        text = text.replace('(mean|%s)'%key, '%s')

    l = []
    m = []
    for key in keys:
        if localMeanings and key in localMeanings:
            m.append(localMeanings[key])
        elif key in meanings:
            m.append(meanings[key])
        else:
            raise exceptions.InvalidMeaningKey(u'Invalid meaning key "%s"'%key)
    # m = [meanings.get(key, )  for key in keys]
    for values in itertools.product(*m):
        a = text%values
        l.append(a)

    return l

def substitue_synonym(text, synonyms):
    u"""
    Replaces synonyms tags by their values, using a sysnonym list.
    """
    text = text.lower()
    for k, v in synonyms.items():
        for expression in v:
            text = re.sub(r'(\W|^)%s(\W|$)'%expression, r'\1%s\2'%k, text)

    return text

def normalize_input(text, synonyms=None):
    u"""
    Automatizes the task of remove accents and substitute synonyms.
    """
    text = remove_accents(text)

    if synonyms:
        text = substitue_synonym(text, synonyms)

    return text