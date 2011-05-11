A Linguagem de marcação Aerolito
================================

Aerolito é uma linguagem de marcação baseada em YAML com influências da AIML e 
RiveScript. A ideia é criar uma linguagem mais clara e fácil de se escrever (em
contraste com a AIML) sem criar uma formato novo (como a RiveScript).

Exemplo de uso:

.. code-block:: python

    from aerolito import Kernel
    kernel = Kernel('config.yml')

    print kernel.respond(u'Oi')


Definição do esquema
--------------------

A base de dados é dividida em vários arquivos, chamados de **arquivos de 
conversação**. Esses arquivos possuem um esquema básico:

.. code-block:: yaml

    version    : (Versão)
    name       : (Nome do tópico coberto pelo arquivo)
    description: (Descrição do arquivo)

    patterns:
        ... (Padrões)


Cada padrão é um conjunto de *(ENTRADAS-DO-USUÁRIO => RESPOSTA-PARA-USUÁRIO)*. 
Esses padrões são chamados de **padrões de conversação**.

Os padrões de conversação podem conter as seguintes tags:

- **after**: Contém um conjunto de strings que são comparadas com a última 
  resposta. Para que o padrão seja selecionado é necessário que a última 
  resposta seja igual a qualquer uma das strings definidas nessa tag.
- **in**: Contém um conjunto de strings que são comparadas com a entrada do 
  usuário, para que o padrão seja selecionado é necessário que a entrada seja
  aceita por qualquer uma das string definidas nessa tag.
- **when**: Contém um conjunto de ações que serão executadas depois da entrada
  ser aceita pelas tags ``after`` e ``in``. É necessário que todas ações 
  retornem um valor verdadeiro para que o padrão seja selecionado.
- **out**: Conjunto de respostas caso o padrão seja selecionado. Se houver mais
  de uma resposta, é selecionado uma aleatoriamente.
- **post**: Ações que serão executadas depois do padrão ser aceito e uma 
  resposta for selecionada.

Exemplo de um padrão de conversação:

.. code-block:: yaml

    patterns:
        - in:
            - Hello
            - Hi
          out:
            - Hello my friend
            - Hiho


Exemplos
--------


Sinônimos
~~~~~~~~~

Aerolito:

.. code-block:: yaml

    patterns:
        - in:
            - Hello
            - Hi
            - Hi there
            - Howdy
            - Hola
          out:
            - Hi There!

AIML:

.. code-block:: xml

    <category> 
    <pattern>HELLO</pattern> 
    <template>Hi there!</template> 
    </category>

    <category>
    <pattern>HI</pattern> 
    <template><srai>HELLO</srai></template>
    </category>

    <category>
    <pattern>HI THERE</pattern> 
    <template><srai>HELLO</srai></template>
    </category>

    <category>
    <pattern>HOWDY</pattern> 
    <template><srai>HELLO</srai></template>
    </category>

    <category>
    <pattern>HOLA</pattern> 
    <template><srai>HELLO</srai></template>
    </category>
        

Knock Knock Joke
~~~~~~~~~~~~~~~~

Aerolito:

.. code-block:: yaml

    patterns:
        - in  : Knock Knock
          out : Who is there?

        - after : Who is there?
          in    : '*'
          out   : <star> who?
        
        - after : <star> who?
          in    : '*'
          out   : Ha ha very funny, <name>.


AIML:

.. code-block:: xml

    <category>
    <pattern>KNOCK KNOCK</pattern>
    <template>Who is there?</template>
    </category>

    <category>
    <pattern>*</pattern>
    <that>WHO IS THERE</that>
    <template><person/> who?</template>
    </category>

    <category>
    <pattern>*</pattern>
    <that>* WHO</that>
    <template>Ha ha very funny, <get name="name"/>.</template>
    </category>

