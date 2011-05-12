# -*- coding:utf-8 -*-

import yaml
from aerolito.pattern import Pattern

class Kernel(object):
    def __init__(self, configFile):
        self.loadConfig(configFile)
        self.addUser('default')
        self._environ['userid'] = 'default'

    def addUser(self, userid):
        self._environ['session'][userid] = {}
        session = self._environ['session'][userid]
        session['inputs'] = []
        session['responses'] = []
        session['stars'] = []
        session['locals'] = {}

    def removeUser(self, userid):
        if userid in self._environ['session']:
            del self._environ['session'][userid]

    def loadConfig(self, configFile):
        config = yaml.load(open(configFile, 'rb').read())
        self._environ = {
            'userid': None,
            'directives': {},
            'globals': config,
            'session': {},
        }

        self._patterns = []

        for dataFile in config.get('files'):
            self.loadData(dataFile)


    def loadData(self, dataFile):
        data = yaml.load(open(dataFile, 'rb').read())
        for p in data['patterns']:
            pattern = Pattern(p, self._environ)
            self._patterns.append(pattern)


    def respond(self, value, userid='default'):
        output = None
        for pattern in self._patterns:
            if pattern.match(value, self._environ):
                output = pattern.choiceOutput(self._environ)
                pattern.executePost(self._environ)
            
        session = self._environ['session'][userid]
        session['inputs'].append(value)
        session['responses'].append(output)

        return output

