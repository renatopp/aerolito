# -*- coding: utf-8 -*-
"""
Arquivo de funções utilitárias
"""

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