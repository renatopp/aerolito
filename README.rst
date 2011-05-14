Aerolito
========

Aerolito is a markup language YAML based influenced by AIML and RiveScript. The 
motivation is to have a more clean and easy language than AIML without create a 
new file format, like RiveScript.

Use example::

    from aerolito import Kernel
    kernel = Kernel('config.yml')

    print kernel.Respond(u'Hello')


YAML Schema
-----------

YAML was chosed because is more clean, and easy to maintain and read. It's easy 
to define python types as lists, strings and dictionaries. For example::

    # YAML File
    key:
        - this is a list item
        - 999                   # integer
        - [1, 2, 3, 4]          # list
        - {1:2, 3:4}            # dict
        - some string           # string

The example above above generate following structure in Python::

    {key: [
        'this is a list item',
        999,
        [1, 2, 3, 4],
        {1:2, 3:4}
        'some string'
    ]}

Is important to understand the yaml structure to create a correct structure for 
aerolito. 


Configuration File
~~~~~~~~~~~~~~~~~~

To provide a simple structure for encapsulation, Aerolito knowledge base is 
divided at least in 2 main files: a configuration and a conversation file.

The **configuration file** (e.g. config.yml) will registry every global variable
and specify the conversation and special files. An example of a config.yml::


    # config.yml
    version   : v0.1-alpha
    botname   : chapolin
    variable1 : value
    variable2 : value
    variableN : value

    conversations:
        - conversations/file1.yml
        - conversations/file2.yml

    synonyms:
        - specials/file1.yml
        - specials/file2.yml
    

Notice, the first 5 tags are global variables, accessed in patterns by 
"<variable>" expression. Also notice the tags "conversations" and "synonyms", 
these tags define conversations pattern file and special synonym files, 
respectively. Conversations tag is the only one required in config file, with
at least one entry.


Conversation Files
~~~~~~~~~~~~~~~~~~

The **conversation files** contains the definition of **conversation patterns**
(i.e., the set of user-inputs patterns and responses texts). Theses files must 
have the "patterns" tag, with at least one element. The "patterns" tags defines
the list of conversation patterns.

Example of file::

    patterns:
        - in:
            - Hello
            - Hi there!
          out: 
            - Hi!


