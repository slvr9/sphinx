"""
    sphinx.ext.optionspecs
    ~~~~~~~~~~~~~~~~~~~

EN:-------------------------------------------------------------------

Trigger for Directive[*1] options.

Use different settings (values) of the Directive options, 
depending on the selected Builders[*2] and the format.

RU:----------------------------------------------------------------------

Триггер срабатывания опций Директив[*1].

Использование различных настроек (значений) опций Директив в
зависимости от выбранного Builders[*2] и формата.

----------------------------------------------------------------------
[*1] https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
[*2] https://www.sphinx-doc.org/en/master/usage/builders/index.html
----------------------------------------------------------------------

use
---

``` rst

.. dective::
   option[:builder][:format]: value

```   

setup
-----

file `conf.py`
```  
extensions = [
    ..
    'sphinx.ext.optionspecs', #< add a line
    ..
] 
```

example
-------

file `index.rst`
```  
.. tocTREE::
  :caption:           Title for the GENERAL case
  :caption:html:html: Title for `builder:html` and `format:html`
  :caption::html:     Header of other builders with `format:html`
  :caption:epub:      Header for `epub` builder
``` 



"""
from typing import Any, Dict, List

import sphinx
from sphinx.application import Sphinx

import docutils.parsers.rst
import docutils.nodes
import docutils.utils 
from docutils.utils import DuplicateOptionError
from docutils import nodes, utils

from sphinx.util import logging
from sphinx.util.console import bold  # type: ignore

logger = logging.getLogger(__name__)


optionspecs_builder_name=''
optionspecs_builder_format=''



def calculate_spec_weight(specs:list) -> int:
    weight = 1
    #
    if (1<len(specs)):
        s = str.strip(specs[1])
        if s:
            if (s==optionspecs_builder_name):
                weight = weight + 100
            else:
                return -1    
    #
    if (2<len(specs)):
        s = str.strip(specs[2])
        if s:
            if (s==optionspecs_builder_format):
                weight = weight + 10
            else:
                return -1    
    #
    return weight



def assemble_option_dict(option_list, options_spec):
    """
    Return a mapping of option names to values.

    :Parameters:
        - `option_list`: A list of (name, value) pairs (the output of
          `extract_options()`).
        - `options_spec`: Dictionary mapping known option names to a
          conversion function such as `int` or `float`.

    :Exceptions:
        - `KeyError` for unknown option names.
        - `DuplicateOptionError` for duplicate options.
        - `ValueError` for invalid option values (raised by conversion
           function).
        - `TypeError` for invalid option value types (raised by conversion
           function).
    """
    options = {}
    weights = {}
    applied = {}
    for name, value in option_list:
        specs = name.split(':')
        convertor = options_spec[specs[0]]  # raises KeyError if unknown
        if convertor is None:
            raise KeyError(name)        # or if explicitly disabled

        weight = calculate_spec_weight(specs)
        if weight<0:
           continue         
        
        if specs[0] in options:
            if weights[specs[0]]==weight:
                if applied[specs[0]]==name: 
                    raise DuplicateOptionError('duplicate option "%s"' % name)
                else:
                    raise DuplicateOptionError('duplicate options "%s" and "%s"' 
                                               % (name,applied[specs[0]]))
            else:
                if weight<weights[specs[0]]:
                    continue

        try:
            applied[specs[0]] = name
            weights[specs[0]] = weight
            options[specs[0]] = convertor(value)
        except (ValueError, TypeError) as detail:
            raise detail.__class__('(option: "%s"; value: %r)\n%s'
                                   % (name, value, ' '.join(detail.args)))
    return options



def dockutils_utils__extract_extension_options(field_list, options_spec):
        option_list = utils.extract_options(field_list)
        option_dict = assemble_option_dict(option_list, options_spec)
        return option_dict

#def class_parse_extension_options(obj: docutils.parsers.rst.states.Body, option_spec, datalines):
def body_parse_extension_options(obj: docutils.parsers.rst.states.Body, option_spec, datalines):
        node = nodes.field_list()
        newline_offset, blank_finish = obj.nested_list_parse(
              datalines, 0, node, initial_state='ExtensionOptions',
              blank_finish=True)
        if newline_offset != len(datalines): # incomplete parse of block
            return 0, 'invalid option block'
        try:
            #application.Sphinx.builders
            #sphinx.application.builtin_extensions builders.builder.name
            #app.abui  
            # 
            options = dockutils_utils__extract_extension_options(node, option_spec)
        except KeyError as detail:
            return 0, ('unknown option: "%s"' % detail.args[0])
        except (ValueError, TypeError) as detail:
            return 0, ('invalid option value: %s' % ' '.join(detail.args))
        except utils.ExtensionOptionError as detail:
            return 0, ('invalid option data: %s' % ' '.join(detail.args))
        if blank_finish:
            return 1, options
        else:
            return 0, 'option data incompletely parsed'




################################################################################################
### f*ck up classes for override default methods

class Body(docutils.parsers.rst.states.Body):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class BulletList(docutils.parsers.rst.states.BulletList):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class DefinitionList(docutils.parsers.rst.states.DefinitionList):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class EnumeratedList(docutils.parsers.rst.states.EnumeratedList):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class FieldList(docutils.parsers.rst.states.FieldList):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class OptionList(docutils.parsers.rst.states.OptionList):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class LineBlock(docutils.parsers.rst.states.LineBlock):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class ExtensionOptions(docutils.parsers.rst.states.ExtensionOptions):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class Explicit(docutils.parsers.rst.states.Explicit):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class Text(docutils.parsers.rst.states.Text):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class Definition(docutils.parsers.rst.states.Definition):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class Line(docutils.parsers.rst.states.Line):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class SubstitutionDef(docutils.parsers.rst.states.SubstitutionDef):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class RFC2822Body(docutils.parsers.rst.states.RFC2822Body):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)

class RFC2822List(docutils.parsers.rst.states.RFC2822List):
    def parse_extension_options(self, option_spec, datalines):
        return body_parse_extension_options(self, option_spec, datalines)


################################################################################################
### f*ck up default values

def setup_fckUP_obj(arr: List, object: Any, objName: str) -> int:
    #
    for index, item in enumerate(arr, start=0):
        if issubclass(object, item):
            arr[index]=object 
            #logger.info(('optionSpecs: replaced "%s"'), objName)
            return 1
    #
    logger.warn(('optionSpecs: no FOUND "%s"'), objName)
    return 0
   
 
def setup_fckUP() -> None:
    cnt = 0
    lst=list(docutils.parsers.rst.states.state_classes)
    #
    cnt = cnt + setup_fckUP_obj(lst, Body, 'Body') 
    cnt = cnt + setup_fckUP_obj(lst, BulletList, 'BulletList') 
    cnt = cnt + setup_fckUP_obj(lst, DefinitionList, 'DefinitionList') 
    cnt = cnt + setup_fckUP_obj(lst, EnumeratedList, 'EnumeratedList') 
    cnt = cnt + setup_fckUP_obj(lst, FieldList, 'FieldList')
    cnt = cnt + setup_fckUP_obj(lst, OptionList, 'OptionList') 
    cnt = cnt + setup_fckUP_obj(lst, LineBlock, 'LineBlock') 
    cnt = cnt + setup_fckUP_obj(lst, ExtensionOptions, 'ExtensionOptions') 
    cnt = cnt + setup_fckUP_obj(lst, Explicit, 'Explicit') 
    cnt = cnt + setup_fckUP_obj(lst, Text, 'Text')
    cnt = cnt + setup_fckUP_obj(lst, Definition, 'Definition') 
    cnt = cnt + setup_fckUP_obj(lst, Line, 'Line') 
    cnt = cnt + setup_fckUP_obj(lst, SubstitutionDef, 'SubstitutionDef') 
    cnt = cnt + setup_fckUP_obj(lst, RFC2822Body, 'RFC2822Body') 
    cnt = cnt + setup_fckUP_obj(lst, RFC2822List, 'RFC2822List')
    #
    docutils.parsers.rst.states.state_classes = tuple(lst)
    #
    logger.info(bold(  ('optionSpecs...')), nonl=True)
    if len(docutils.parsers.rst.states.state_classes)==cnt:
        logger.info('done')
    else:
        logger.info('NOT done')


################################################################################################
###

def setup_builder_inited(app: Sphinx) -> None:
    global optionspecs_builder_name
    global optionspecs_builder_format
    optionspecs_builder_name=app.builder.name
    optionspecs_builder_format=app.builder.format
    logger.info(bold(  ('optionSpecs')), nonl=True)
    logger.info((' %s:%s'), optionspecs_builder_name, optionspecs_builder_format)
    return


def setup(app: Sphinx) -> Dict[str, Any]:
    setup_fckUP()
    app.connect('builder-inited', setup_builder_inited)
    return {
        'version': sphinx.__display_version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }