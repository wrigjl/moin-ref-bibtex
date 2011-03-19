"""
    MoinMoin - Ref Macro

    Collect and emit footnotes. Note that currently footnote
    text cannot contain wiki markup.

    @copyright: 2011 Jason L. Wright <jason@thought.net>
    @license: BSD
"""

from MoinMoin import config, wikiutil
from MoinMoin.parser.text_moin_wiki import Parser as WikiParser
from MoinMoin.support.python_compatibility import hash_new
import MoinMoin.macro.FootNote as FootNote
import MoinMoin.macro.RefText as RefText

Dependencies = ["time"] # footnote macro cannot be cached

def execute(macro, args):
    request = macro.request
    formatter = macro.formatter
    txt = RefText.execute(macro, args)
    return FootNote.execute(macro, txt)
