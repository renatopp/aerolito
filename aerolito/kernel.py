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
import yaml
import codecs
from aerolito import exceptions
from aerolito import directives
from aerolito.pattern import Pattern
from aerolito.pattern import remove_accents
from aerolito.pattern import normalize_input

class Kernel(object):
    u"""
    Aerolito's main object. 

    Kernel uses an environment variable for session and variables controlling. 
    Sessions are used for user-dependent information storage, such inputs and 
    outputs logs, and local variables. Variables are devided into 3 levels: 
    *stars* for pattern stars ``*``, *locals* for user-related informations, 
    and *globals*.

    By default kernel sets the first users as "default" key. It session can be 
    acessed via ``_environ['session']['default']``. A kernel object have 4 
    instance variables:

    _patterns
        A list of all patterns that kernel is handling.
    
    _synonyms
        A list of all *synonyms*.

    _meanings
        A list of all *meanings*.

    _environ
        The environment variable.
    """

    def __init__(self, config_file, encoding='utf-8'):
        u"""Initializes a kernel object, creating the user "default". """
        self._patterns = None
        self._synonyms = None
        self._meanings = None
        self._environ = None

        self.load_config(config_file, encoding=encoding)

        self.add_user('default')
        self.set_user('default')

    def add_user(self, user_id):
        u"""
        Add a new user in session of environ variable, initializing the 
        following user-dependet variables:

        - **inputs**: List with all inputs of an user.
        - **responses**: List with all outputs for an user, without 
          normalizing.
        - **responses-normalized**: List with all outputs normalized.
        - **stars**: Pattern-related variables, is a list of stars that matches 
          with recognized pattern (i.e., words in the place of "\*"). Is filled 
          by ``after`` and ``in`` tags.
        - **locals**: Dictionary of local variables, setted via patterns in 
          ``when`` or ``post`` tags.

        If ``user_id`` is already in session, an exception 
        ``UserAlreadyInSession`` is rised.
        """
        if user_id in self._environ['session']:
            raise exceptions.UserAlreadyInSession(user_id)

        self._environ['session'][user_id] = {}
        session = self._environ['session'][user_id]
        session['inputs'] = []
        session['responses'] = []
        session['responses-normalized'] = []
        session['stars'] = []
        session['locals'] = {}
    
    def set_user(self, user_id):
        u"""
        Defines who is the active user in session. Functions and objects uses
        ``_environ['user_id']`` variable to select the correct session.
        """
        self._environ['user_id'] = user_id

    def remove_user(self, user_id):
        u"""
        Removes an user from session.
        """
        if user_id in self._environ['session']:
            del self._environ['session'][user_id]

    def add_directive(self, name, directive):
        u"""
        Add a new directive in environment var.
        """
        if self._environ['directives'].has_key(name):
            raise DuplicatedDirective(name)
        
        self._environ['directives'][name] = directive(self._environ)

    def __load_directives(self):
        u"""
        Loads default directives and directives of 
        ``directives._directive_pool``, setted via 
        ``directives.register_directive`` by users.
        """
        env_directives = self._environ['directives']
        env_directives['define'] = directives.Define(self._environ)
        env_directives['delete'] = directives.Delete(self._environ)
        env_directives['isdefined'] = directives.IsDefined(self._environ)
        env_directives['isnotdefined'] = directives.IsNotDefined(self._environ)
        env_directives['equal'] = directives.Equal(self._environ)
        env_directives['notequal'] = directives.NotEqual(self._environ)
        env_directives['greaterthan'] = directives.GreaterThan(self._environ)
        env_directives['lessthan'] = directives.LessThan(self._environ)
        env_directives['greaterequal'] = directives.GreaterEqual(self._environ)
        env_directives['lessequal'] = directives.LessEqual(self._environ)

        for k, item in directives._directive_pool.iteritems():
            self.add_directive(k, item)

    def load_config(self, config_file, encoding='utf-8'):
        u"""
        Loads the configuration file.

        Receive as parameters a name (with relative or full path) of 
        configuration file, and its encoding. Default encoding is utf-8.

        The configuration file have a mandatory tag **conversations**, that 
        specify the conversation files. Is a list with the names (with relative 
        or full path) of the files.

        Each kernel can load only one of configuration files, if this method is
        called two times, the second call will override the previous 
        informations (by environ variable).
        """
        try:
            plain_text = codecs.open(config_file, 'rb', encoding).read()
            config = yaml.load(plain_text)
        except IOError:
            raise exceptions.FileNotFound(config_file)

        # Initialize environment dict
        self._environ = {
            'user_id': None,
            'meanings': None,
            'synonyms': None,
            'directives': {},
            'globals': config,
            'session': {},
        }

        self.__load_directives()

        if 'conversations' not in config:
            raise exceptions.MissingTag('conversations', 'config')

        self._synonyms = {}
        self._meanings = {}
        self._patterns = []
        
        self._environ['synonyms'] = self._synonyms
        self._environ['meanings'] = self._meanings

        for synonym_file in config.get('synonyms', []):
            self.load_sysnonym(synonym_file, encoding)

        for meaning_file in config.get('meanings', []):
            self.load_meaning(meaning_file, encoding)

        for conversation_file in config['conversations']:
            self.load_conversation(conversation_file, encoding)


    def load_sysnonym(self, synonym_file, encoding='utf-8'):
        u"""
        Load a synonym file.

        Receive as parameters a name (with relative or full path) of a
        synonym file, and their encoding. Default encoding is utf-8.

        Synonym file must have at least one element. Contains a list of lists.
        
        The patterns are loaded in ``_synonyms``
        """
        try:
            plain_text = codecs.open(synonym_file, 'rb', encoding).read()
            data = yaml.load(plain_text)
        except IOError:
            raise exceptions.FileNotFound(synonym_file)
            
        for synonyms in data:
            if len(synonyms) < 2:
                raise exceptions.InvalidTagValue(
                        u'Synonym list must have more than one element.')

            key = remove_accents(synonyms[0]).lower()
            vals = [remove_accents(value).lower() for value in synonyms[1:]]

            if key in self._synonyms:
                raise exceptions.DuplicatedSynonym(key, synonym_file)
            
            self._synonyms[key] = vals

    def load_meaning(self, meaning_file, encoding='utf-8'):
        u"""
        Load a meaning file.

        Receive as parameters a name (with relative or full path) of a
        meaning file, and their encoding. Default encoding is utf-8.

        Meaning file must have at least one element. Contains a list of lists.

        The patterns are loaded in ``_meanings``
        """
        try:
            plain_text = codecs.open(meaning_file, 'rb', encoding).read()
            data = yaml.load(plain_text)
        except IOError:
            raise exceptions.FileNotFound(meaning_file)
            
        for meanings, values in data.items():
            if len(values) == 0:
                raise exceptions.InvalidTagValue(
                        u'Meaning list must have one or more element.')

            key = remove_accents(meanings).lower()
            vals = [normalize_input(v, self._environ['synonyms']).lower() for v in values]

            if key in self._meanings:
                raise exceptions.DuplicatedMeaning(key, meaning_file)
            
            self._meanings[key] = vals

    def load_conversation(self, conversation_file, encoding='utf-8'):
        u"""
        Load a conversation file.

        Receive as parameters a name (with relative or full path) of a
        conversation file, and their encoding. Default encoding is utf-8.

        The conversations file have a obrigatory tag **patterns**, that specify 
        the conversation patterns. Is a list of dictonaries.

        The patterns are loaded in ``_patterns``
        """
        try:
            plain_text = codecs.open(conversation_file, 'rb', encoding).read()
            data = yaml.load(plain_text)
        except IOError:
            raise exceptions.FileNotFound(conversation_file)

        if 'patterns' not in data:
            raise exceptions.MissingTag('patterns', conversation_file)

        for p in data['patterns']:
            pattern = Pattern(p, self._environ)
            self._patterns.append(pattern)


    def respond(self, value, user_id=None, registry=True):
        u"""
        Returns a response for a given user input.

        Parameters ``value`` is the user input.

        If ``user_id`` is informed, the kernel changes the session for this user,
        if parameter is null, kernel keeps the active user. If user is not 
        informed and no user is active, kernel try to use the *'default'* user,
        if default is not avaliable (out of session pool) an exception is 
        raised.
        
        This method just can be used after environment initialization.
        """

        # Verify initialization
        if not self._environ :
            raise exceptions.InitializationRequired('configuration')
        elif not self._patterns:
            raise exceptions.InitializationRequired('conversation')

        # Verify user's session
        if user_id is not None:
            self.set_user(user_id)
        elif self._environ['user_id'] is None:
            if 'default' in self._environ['session']:
                self.set_user('default')
            else:
                raise exceptions.NoUserActiveInSession()

        output = None
        value = normalize_input(value, self._synonyms)
        for pattern in self._patterns:
            if pattern.match(value, self._environ):
                output = pattern.choice_output(self._environ)
                pattern.execute_post(self._environ)
                break
            
        session = self._environ['session'][self._environ['user_id']]
        if registry:
            session['inputs'].append(value)
        
        if output:
            recursive = re.findall('\(rec\|([^\)]*)\)', output)
            for r in recursive:
                toreplace = u'(rec|%s)'%r
                resp = self.respond(r, registry=False) or ''
                output = output.replace(toreplace, resp)

            if registry:
                session['responses'].append(output)
                session['responses-normalized'].append(normalize_input(output, self._synonyms))

        return output
