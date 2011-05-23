# -*- coding: utf-8 -*-

import re
import yaml
import codecs
from aerolito import exceptions
from aerolito import directives
from aerolito.pattern import Pattern
from aerolito.pattern import removeAccents
from aerolito.pattern import normalizeInput

class Kernel(object):
    u"""
    Aerolito's main object. 

    Kernel use an environment variable for session and variables controlling. 
    Session are used for user-dependent information storage, such inputs and 
    outputs logs, and local variables. Variables are devided into 3 levels: 
    *stars* for pattern-related, *locals* for user-related, and *globals*.
    """
    # List of patterns, synonyms and meanings file, loaded from configuration 
    # file
    _patterns = None
    _synonyms = None
    _meanings = None

    # Environ variable
    _environ = None

    def __init__(self, configFile, encoding='utf-8'):
        self.loadConfig(configFile, encoding=encoding)

        # Create a default user
        self.addUser('default')
        self.setUser('default')

    def addUser(self, userid):
        u"""
        Add a new use in session in environ variable, initializing the following
        user-dependet variables:

        - **inputs**: List with all inputs of an user.
        - **responses**: List with all outputs for an user, without normalizing.
        - **responses-normalized**: List with all outputs normalizeds.
        - **stars**: Pattern-related variables, is a list of stars that matches 
          with recognized pattern (i.e., words in the place of "\*"). Is filled 
          by ``after`` and ``in`` tags.
        - **locals**: Dictionary of local variables, setted via patterns in 
          ``when`` or ``post`` tags.

        If is ``userid`` already in session, an exception
        ``UserAlreadyInSession`` is rised.
        """
        if userid in self._environ:
            raise exceptions.UserAlreadyInSession(
                        u'User "%s" already in session'%str(userid))

        self._environ['session'][userid] = {}
        session = self._environ['session'][userid]
        session['inputs'] = []
        session['responses'] = []
        session['responses-normalized'] = []
        session['stars'] = []
        session['locals'] = {}
    
    def setUser(self, userid):
        u"""
        Defines who is the active user in session. Functions and objects use
        ``_environ['userid']`` variable to catch the correct session.
        """
        self._environ['userid'] = userid

    def removeUser(self, userid):
        u"""
        Remove an user of session.
        """
        if userid in self._environ['session']:
            del self._environ['session'][userid]

    def addDirective(self, name, directive):
        u"""
        Add a new directive in environment var.
        """
        if self._environ['directives'].has_key(name):
            raise DuplicatedDirective(u'Duplicated directive name "%s"'%name)
        
        self._environ['directives'][name] = directive(self._environ)

    def __loadDirectives(self):
        u"""
        Load default directives and directives of ``directives._directivePool``,
        setted via ``directives.registerDirective`` by user.
        """
        envdirectives = self._environ['directives']
        envdirectives['define'] = directives.Define(self._environ)
        envdirectives['delete'] = directives.Delete(self._environ)
        envdirectives['isdefined'] = directives.IsDefined(self._environ)
        envdirectives['isnotdefined'] = directives.IsNotDefined(self._environ)
        envdirectives['equal'] = directives.Equal(self._environ)
        envdirectives['notequal'] = directives.NotEqual(self._environ)
        envdirectives['greaterthan'] = directives.GreaterThan(self._environ)
        envdirectives['lessthan'] = directives.LessThan(self._environ)
        envdirectives['greaterequal'] = directives.GreaterEqual(self._environ)
        envdirectives['lessequal'] = directives.LessEqual(self._environ)

        for k, item in directives._directivePool.iteritems():
            self.addDirective(k, item)

    def loadConfig(self, configFile, encoding='utf-8'):
        u"""
        Load the configuration file.

        Receive as parameters a name (with relative or full path) of 
        configuration file, and their encoding. Default encoding is utf-8.

        The configuration file have a obrigatory tag **conversations**, that 
        specify the conversation files. Is a list with the name (with relative 
        or full path) of the files.

        Each kernel can load only one of configuration files, if this method is
        called two times, the second call will override the previous 
        informations (by environ variable).
        """
        try:
            plaintext = codecs.open(configFile, 'rb', encoding).read()
            config = yaml.load(plaintext)

            # Initialize environment dict
            self._environ = {
                'userid': None,
                'meanings': None,
                'synonyms': None,
                'directives': {},
                'globals': config,
                'session': {},
            }

            self.__loadDirectives()

            if 'conversations' not in config:
                raise exceptions.MissingTag(
                        u'Tag "conversations" not found in configuration file.')

            self._synonyms = {}
            self._meanings = {}
            self._patterns = []
            
            self._environ['synonyms'] = self._synonyms
            self._environ['meanings'] = self._meanings

            for synonymFile in config.get('synonyms', []):
                self.loadSynonym(synonymFile, encoding)

            for meaningFile in config.get('meanings', []):
                self.loadMeaning(meaningFile, encoding)

            for conversationFile in config['conversations']:
                self.loadConversation(conversationFile, encoding)

        except IOError:
            raise exceptions.FileNotFound(
                        u'Configuration file (%s) not found.'%str(configFile))

    def loadSynonym(self, synonymFile, encoding='utf-8'):
        u"""
        Load a synonym file.

        Receive as parameters a name (with relative or full path) of a
        synonym file, and their encoding. Default encoding is utf-8.

        Synonym file must have at least one element. Contains a list of lists.
        
        The patterns are loaded in ``_synonyms``
        """
        try:
            plaintext = codecs.open(synonymFile, 'rb', encoding).read()
            data = yaml.load(plaintext)
            
            for synonyms in data:
                if len(synonyms) < 2:
                    raise exceptions.InvalidTagValue(
                            u'Synonym list must have more than one element.')

                key = removeAccents(synonyms[0]).lower()
                vals = [removeAccents(value).lower() for value in synonyms[1:]]

                if key in self._synonyms:
                    raise exceptions.DuplicatedSynonym(
                            u'Duplicated synonym "%s" in "%s.'%
                            (str(key), str(synonymFile)))
                
                self._synonyms[key] = vals
        except IOError:
            raise exceptions.FileNotFound(
                    u'Synonym file (%s) not found.'%str(synonymFile))

    def loadMeaning(self, meaningFile, encoding='utf-8'):
        u"""
        Load a meaning file.

        Receive as parameters a name (with relative or full path) of a
        meaning file, and their encoding. Default encoding is utf-8.

        Meaning file must have at least one element. Contains a list of lists.

        The patterns are loaded in ``_meanings``
        """
        try:
            plaintext = codecs.open(meaningFile, 'rb', encoding).read()
            data = yaml.load(plaintext)
            
            for meanings, values in data.items():
                if len(values) == 0:
                    raise exceptions.InvalidTagValue(
                            u'Meaning list must have one or more element.')

                key = removeAccents(meanings).lower()
                vals = [normalizeInput(v, self._environ['synonyms']).lower() for v in values]

                if key in self._meanings:
                    raise exceptions.DuplicatedMeaning(
                            u'Duplicated meaning "%s" in "%s.'%
                            (str(key), str(meaningFile)))
                
                self._meanings[key] = vals
        except IOError:
            raise exceptions.FileNotFound(
                    u'Meaning file (%s) not found.'%str(meaningFile))

    def loadConversation(self, conversationFile, encoding='utf-8'):
        u"""
        Load a conversation file.

        Receive as parameters a name (with relative or full path) of a
        conversation file, and their encoding. Default encoding is utf-8.

        The conversations file have a obrigatory tag **patterns**, that specify 
        the conversation patterns. Is a list of dictonaries.

        The patterns are loaded in ``_patterns``
        """
        try:
            plaintext = codecs.open(conversationFile, 'rb', encoding).read()
            data = yaml.load(plaintext)
            if 'patterns' not in data:
                raise exceptions.MissingTag(
                    u'Tag "patterns" not found in conversation file (%s).'%
                        str(conversationFile))

            for p in data['patterns']:
                pattern = Pattern(p, self._environ)
                self._patterns.append(pattern)
        except IOError:
            raise exceptions.FileNotFound(
                    u'Conversation file (%s) not found.'%str(conversationFile))


    def respond(self, value, userid=None, registry=True):
        u"""
        Returns a response for a given user input.

        Parameters ``value`` is the user input.

        If ``userid`` is informed, the kernel changes the session for this user,
        if parameter is null, kernel keeps the active user. If user is not 
        informed and no user is active, kernel try to use the *'default'* user,
        if default is not avaliable (out of session pool) an exception is 
        raised.
        
        This method just can be used after environment initialization.
        """

        # Verify initialization
        if not self._environ :
            raise exceptions.InitializationRequired(
                    u'Initialization required: Load a configuration file')
        elif not self._patterns:
            raise exceptions.InitializationRequired(
                    u'Initialization required: Load a conversation file')

        # Verify user's session
        if userid is not None:
            self.setUser(userid)
        elif self._environ['userid'] is None:
            if 'default' in self._environ['session']:
                self.setUser('default')
            else:
                raise exceptions.NoUserActiveInSession(u'No user to session')

        output = None
        value = normalizeInput(value, self._synonyms)
        for pattern in self._patterns:
            if pattern.match(value, self._environ):
                output = pattern.choiceOutput(self._environ)
                pattern.executePost(self._environ)
                break
            
        session = self._environ['session'][self._environ['userid']]
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
                session['responses-normalized'].append(normalizeInput(output, self._synonyms))

        return output
