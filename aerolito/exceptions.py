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

class AerolitoException(Exception):
    message = '%s'

    def __init__(self, *values):
        self.values = [str(i) for i in values]
        if len(self.values) == 1:
            self.values = self.values[0]
    
    def __str__(self):
        return self.message%self.values

class InvalidTagValue(AerolitoException): pass
class MissingTag(AerolitoException):
    message = u'Tag "%s" not found in %s file.'

class UserAlreadyInSession(AerolitoException):
    message = u'User "%s" already in session.'

class NoUserActiveInSession(AerolitoException):
    message = u'No user to session.'

class FileNotFound(AerolitoException):
    message = u'File ("%s") not found.'

class InitializationRequired(AerolitoException):
    message = u'Initialization required: Load a %s file'

class DuplicatedDirective(AerolitoException):
    message = u'Duplicated directive name "%s".'

class DuplicatedSynonym(AerolitoException):
    message = u'Duplicated synonym "%s" in "%s.'

class DuplicatedMeaning(AerolitoException):
    message = u'Duplicated meaning "%s" in "%s.'

class InvalidMeaningKey(AerolitoException): pass