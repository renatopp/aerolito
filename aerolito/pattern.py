# -*- coding: utf-8 -*-

import re
import random
from aerolito import exceptions
from aerolito.utils import removeAccents
from aerolito.utils import normalizeInput
from aerolito.utils import getMeanings

def replace(literal, environ):
    """
    Substitui o valor de um ``Literal`` por uma variável no dicionario 
    ``_environ``.

    A função procura as variáveis na sequência:

    1. ``session['stars']``: Nas variáveis temporárias retiradas da associação
       da entrada, só é acessada através da forma *<star>* ou *<star N>*. Quando
       for chamado *<star N>* é retornado o valor na posição *N*, começando com
       0 (zero). O *<star>* é apenas um atalho para *<star 0>*.
    2. ``_environ['globals']``: Variáveis globais, carregadas do arquivo de 
       configuração.
    3. ``session['locals']``: Vaiáveis locais, são definidas e acessadas 
       geralmente através padrão de conversação (via Directives).

    No caso do dicionário global e local, as variáveis são acessadas através da
    expressão *<variablename>*. 

    Se uma *<variablename>* não é encontrada na lista de *stars*, variaveis 
    globais ou locais, a expressão é substituída por uma string vazia  ('').
    """

    session = environ['session'][environ['userid']]
    p = '\<([\d|\s|\w]*)\>'
    _vars = re.findall(p, unicode(literal._value), re.I)

    result = literal._value
    for var in _vars:
        # Decompõe a expressão em <variavel parametro1 parametroN>
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
    Um objeto Literal representa um elemento na tag ``pattern:out``.
    """

    def __init__(self, value):
        self._value = value


class Action(object):
    """
    As Actions são representaçãos dos elementos das tags ``pattern:when`` e
    ``pattern:post``. Elas são o link entre a Aerolito e funções do python.

    A funções disponíveis são registradas através das Directives.
    """

    def __init__(self, function, params):
        """
        Recebe uma função e uma lista de parâmetros. Os parâmetros são tratados
        posteriormente no caso de haver algumas expressão para substituição, por
        exemplo com *<variable>*. Os valores dos parâmetros são definidos nos 
        arquivos de conversação.
        """
        self._function = function
        self._params = params

    def run(self, environ):
        """
        Executa a ``_function`` passando os parâmetros ``_params`` e a variável
        ``_environ``. 
        """
        params = []
        if self._params:
            params = [replace(x, environ) for x in self._params]
            
        return self._function(*params, environ=environ)


class Regex(object):
    """
    Os objetos Regex representam os elementos das tags ``pattern:after`` e
    ``pattern:in``.

    Regex convert o texto passado na inicilização (valores das tags) em uma
    expressão regular. Essa classe é responsável por aceitar ou não a entrada
    do usuário com o valor das tags. 
    
    Após a assimilação de alguma tag. O Regex guarda os valores adquiridos pela
    expressão especial "\*".
    """

    def __init__(self, text):
        """
        Recebe um texto e converte em expressão regular
        """
        # self._expression = removeAccents(text)
        self._expression = re.escape(text)
        self._expression = self._expression.replace('\\*', '(.*)')
        self._expression = self._expression.replace('\\\\(.*)', '\*')
        self._expression = re.sub('(\\\ )+\(\.\*\)', '(.*)', self._expression)
        self._expression = re.sub('\(\.\*\)(\\\ )+', '(.*)', self._expression)
        self._expression = '^%s$'%self._expression 
        
        self._stars = None
    
    def match(self, value):
        """
        Tenta reconhecer o ``value`` com a ``_expression``. Se reconhecer guarda
        os valores do *<star>*.
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
    Representa um padrão de conversação.

    Um padrão é dividido em 5 tags, usadas na seguinte ordem:

    1. **after**: Condição para selecionar o padrão. O valor da tag é comparado
       com a última resposta, se for associado então o padrão é válido.
    2. **in**: Condição para selecionar o padrão. O valor da tag é comparado com
       a entrada do usuário.
    3. **when**: Condição para selecionar o padrão. É um conjunto de ações que
       devem retornar uma valor verdadeiro para que o padrão seja aceito.
    4. **out**: Valores de retorno, são as respostas para o usuário.
    5. **post**: Conjunto de ações que são executadas depois de um padrão ser 
       aceito e uma resposta ser selecionada.
    """

    def __init__(self, p, environ):
        """
        Receve um dicionário ``p`` com as tags (vem do arquivo de conversação) e
        a variável ``_environ``.
        """
        self._after = self.__convertRegex(p, 'after', environ)
        self._in = self.__convertRegex(p, 'in', environ)
        self._out = self.__convertLiteral(p, 'out')
        self._when = self.__convertAction(p, 'when', environ)
        self._post = self.__convertAction(p, 'post', environ)

    def __convertRegex(self, p, tag, environ=None):
        """
        Converte para Regex os valores de uma tag ``tag`` dentro do dicionário
        ``p``. 

        Aceita uma lista de strings ou uma string.
        """
        synonyms = environ['synonyms']
        meanings = environ['meanings']
        if p.has_key(tag):
            tagValues = p[tag]
            if tagValues is None or tagValues == u'':
                raise exceptions.InvalidTagValue(
                                    'Invalid value for tag %s.'%tag)

            if isinstance(tagValues, (tuple, list)):
                values = tagValues
            else:
                values = [tagValues]

            normalized = [normalizeInput(unicode(x), synonyms) for x in values]
            patterns = []
            for x in normalized:
                patterns.extend(getMeanings(x, meanings))

            return [Regex(x) for x in patterns]
        else:
            return None

    def __convertLiteral(self, p, tag):
        """
        Converte para Literal os valores de uma tag ``tag`` dentro do dicionário
        ``p``. 

        Aceita uma lista de strings ou uma string.
        """
        if p.has_key(tag):
            tagValues = p[tag]
            if tagValues is None or tagValues == u'':
                raise exceptions.InvalidTagValue(
                                    'Invalid value for tag %s.'%tag)

            if isinstance(tagValues, (tuple, list)):
                return [Literal(unicode(x)) for x in tagValues]
            else:
                return [Literal(unicode(tagValues))]
        else:
            return None

    def __convertAction(self, p, tag, environ):
        """
        Converte para Action os valores de uma tag ``tag`` dentro do dicionário
        ``p``. A action só é criada quando existir uma directive correspondente,
        se a directive não existir uma exceção ``InvalidTagValue`` é
        lançada.

        Aceita uma lista de dicionarios ou um dicionario. O(s) dicionário(s) 
        pode(m) ter mais de uma chave (chave é o nome da directive) onde os 
        valores das chaves são os parâmetros.
        """
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
                        
                        if k not in environ['directives']:
                            raise exceptions.InvalidTagValue(
                                    u'Directive "%s" not found'%str(k))

                        action = Action(environ['directives'][k], params)
                        actions.append(action)
            elif isinstance(tagValues, dict):
                for k, p in tagValues.iteritems():
                    if isinstance(p, (tuple, list)):
                        params = [Literal(x) for x in p]
                    else:
                        params = [Literal(p)]

                    if k not in environ['directives']:
                            raise exceptions.InvalidTagValue(
                                    u'Directive "%s" not found'%str(k))
                    
                    action = Action(environ['directives'][k], params)
                    actions.append(action)
            else:
                raise exceptions.InvalidTagValue(
                                    u'Invalid value for tag %s.'%tag)
            
            return actions
        else:
            return None


    def match(self, value, environ):
        """
        Verifica se o ``value`` é associado com o padrão. A sequência de 
        verificação é a seguinte:

        1. Tag After: Pelo menos um elemento da tag deve ser associada com a 
           última resposta.
        2. Tag In: Pelo menos um elemento da tag deve ser associada com o 
           ``value``.
        3. Tag When: Todas ações da tag devem retornar um valor verdadeiro.
        """
        self._stars = None
        session = environ['session'][environ['userid']]

        if self._after:
            for regex in self._after:
                if session['responses-normalized'] and \
                   regex.match(session['responses-normalized'][-1]):
                    session['stars'] = regex._stars
                    break
            else:
                return False

        if self._in:
            for regex in self._in:
                if regex.match(value):
                    session['stars'] = regex._stars
                    break
            else:
                return False

        if self._when:
            for action in self._when:
                if not action.run(environ=environ):
                    return False
        
        return True

    def choiceOutput(self, environ):
        """
        Escolhe uma resposta aleatória, substituindo as variaveis necessárias.
        """
        return replace(random.choice(self._out), environ)
    
    def executePost(self, environ):
        """
        Executa as ações da tag post.
        """
        if self._post:
            for action in self._post:
                action.run(environ=environ)
