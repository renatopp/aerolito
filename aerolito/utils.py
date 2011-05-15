# -*- coding: utf-8 -*-
"""
Arquivo de funções utilitárias
"""

import re
import itertools
from aerolito import exceptions

substitute = [
    (u'ç', 'c'),
    (u'ã', 'a'),
    (u'á', 'a'),
    (u'à', 'a'),
    (u'â', 'a'),
    (u'ä', 'a'),
    (u'é', 'e'),
    (u'è', 'e'),
    (u'ê', 'e'),
    (u'ë', 'e'),
    (u'ó', 'o'),
    (u'ò', 'o'),
    (u'ô', 'o'),
    (u'õ', 'o'),
    (u'ö', 'o'),
    (u'í', 'i'),
    (u'ì', 'i'),
    (u'î', 'i'),
    (u'ï', 'i'),
    (u'ú', 'u'),
    (u'ù', 'u'),
    (u'û', 'u'),
    (u'ü', 'u'),
]

def removeAccents(text):
    """
    Remove acentos de um texto trocando pela letra correspondente, por exemplo:

    >>> removeAccents(u'ã')
    'a'
    """
    for t, f in substitute:
        text = text.replace(t, f)
        text = text.replace(t.upper(), f.upper())

    return text

def getMeanings(text, meanings, localMeanings=None):
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

def substitueSynonym(text, synonyms):
    text = text.lower()
    for k, v in synonyms.items():
        for expression in v:
            text = re.sub(r'(\W|^)%s(\W|$)'%expression, r'\1%s\2'%k, text)

    return text

def normalizeInput(text, synonyms=None):
    text = removeAccents(text)

    if synonyms:
        text = substitueSynonym(text, synonyms)

    return text