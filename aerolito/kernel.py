# -*- coding:utf-8 -*-

import re
import yaml
import codecs
from aerolito import exceptions
from aerolito.pattern import Pattern
from aerolito.pattern import removeAccents
from aerolito.pattern import normalizeInput


class Kernel(object):
    _patterns = None
    _environ = None
    _synonyms = None
    _meanings = None

    def __init__(self, configFile, encoding='utf-8'):
        self.loadConfig(configFile, encoding=encoding)
        self.addUser('default')
        self.setUser('default')

    def addUser(self, userid):
        """
        Adiciona um novo usuário na sessão, reservando as variáveis:

        - **inputs**: Lista com todas entradas de um usuário
        - **responses**: Lista com todas respostas retornadas para um usuário, 
          se não houver saída, ou seja, se o retorno for None, o retorno não é 
          registrado
        - **stars**: Variáveis retiradas no reconhecimento de uma entrada, pelas
          tags ``after`` e ``in``. Essa lista de variáveis contém as substrings
          reconhecidas no lugar do asterisco (\*).
        - **locals**: Dicionário de variáveis locais, setadas via padrões de 
          discussão.

        Se o ``userid`` já estiver na sessão uma exceção 
        ``UserAlreadyInSessionException`` é lançada.
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
        """
        Define qual é o usuário ativo na sessão. As funções e objetos usam a 
        variável ``_environ['userid']`` para pegar a sessão correta.
        """
        self._environ['userid'] = userid

    def removeUser(self, userid):
        """
        Remove um usuário da sessão. Se não o usuário não exister nada acontece.
        """
        if userid in self._environ['session']:
            del self._environ['session'][userid]

    def loadConfig(self, configFile, encoding='utf-8'):
        """
        Carrega o arquivo de configuração.
        
        Recebe como parâmetro o nome (ou nome e caminho) do arquivo de 
        configuração e o encoding do arquivo. O encoding padrão é utf-8.

        O Arquivo de configuração possui tags obrigatórias:

        - **files**: Tag que especifica os arquivos de conversação (Um lista de
          string contendo o nome (com ou sem caminho) dos arquivo).

        Cada Kernel pode carregar apenas um arquivo de configuração, então se 
        esse método for chamado mais de uma vez, a última vai sobrescrever a 
        váriavel ``_environ``, iniciando a sessão.
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
        """
        Carrega um arquivo de conversação.

        Recebe como parâmetro o nome (ou nome e caminho) de um arquivo de 
        conversação e o encoding do arquivo. O encoding padrão é utf-8.

        O Arquivo de configuração possui tags obrigatórias:

        - **pattens**: Tag que especifica a lista de padrões de convesação. 

        Os padrões carregados são adicionados à lista ``_patterns``
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
        """
        Método para retornar uma resposta à uma entrada do usuário

        O parâmetro ``value`` é a entrada do usuário que deve ser respondida. 
        
        Se o ``userid`` for informado, o kernel troca seta a sessão para ele, se
        o parâmetro for nulo, é mantido o usuário atual. No caso do parâmetro 
        não ser informado e nenhum usuário esta ativo, o kernel tenta usar o 
        usuário *'default'*, se ele não estiver na sessão uma exceção
        ``NoUserActiveInSession`` é lançada.

        Esse método só pode ser chamado depois da inicialização (arquivos de 
        configuração e conversação carregados) por causa da inicialização das
        variáveis de ambiente e processamento dos padrões. 

        Caso a variáveis ``_environ`` ou ``_patterns`` estiverem vazias, uma
        exceção ``InitializationRequired`` é lançada.
        """

        # Verifica inicialização
        if not self._environ :
            raise exceptions.InitializationRequired(
                    u'Initialization required: Load a configuration file')
        elif not self._patterns:
            raise exceptions.InitializationRequired(
                    u'Initialization required: Load a conversation file')

        # Verifica o usuário da sessão
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
                # print 'to replace:', toreplace, '=>', resp
                output = output.replace(toreplace, resp)

            if registry:
                session['responses'].append(output)
                session['responses-normalized'].append(normalizeInput(output, self._synonyms))

        return output

