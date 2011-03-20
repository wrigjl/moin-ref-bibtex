
"""
    RefText Macro

    Generate the pretty printed output from the BIB database
    for a given key.

    @copyright: 2011 Jason L. Wright <jason@thought.net>
    @license: BSD
"""

from MoinMoin import config, wikiutil
import xml.dom.minidom
from subprocess import Popen, PIPE

bib2xml = '/usr/local/bin/bib2xml'
bibfile = '/home/wrigjl/Desktop/reading/reading.bib'

Dependencies = ["time"]

def execute(macro, args):
    request = macro.request
    formatter = macro.formatter
    if not hasattr(request, 'refbibtex_bibdb'):
        request.refbibtex_bibdb = {}
        load_bibdb(request.refbibtex_bibdb)
    return printDocument(request, formatter, request.refbibtex_bibdb, args)

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
        return ''.join(rc)

def load_bibdb(bibdb):
    pipe = Popen([bib2xml, bibfile], stdout=PIPE, stderr=PIPE)
    sout = pipe.stdout.read()
    serr = pipe.stderr.read()
    rv = pipe.wait()
    # XXX handle error
    dom = xml.dom.minidom.parseString(sout)
    for ent in dom.getElementsByTagName("bibtex:entry"):
        id = ent.getAttribute('id')
        bibdb[id] = {}
        for ip in ent.childNodes:
            if ip.nodeType == ip.ELEMENT_NODE:
                bibdb[id][u'documentclass'] = ip.localName
                for attr in ip.childNodes:
                    if attr.nodeType == ip.ELEMENT_NODE:
                        name = attr.localName
                        value = getText(attr.childNodes)
                        bibdb[id][name] = value

def printDocument(req, formatter, bibdb, key):
    if not bibdb.has_key(key):
        return 'bibkey(%s): not found' % (key)
    doc = bibdb[key]
    if not doc.has_key('documentclass'):
        return 'bibkey(%s): missing documentclass' % (key)
    try:
        fun = eval("print_doc_%s" % doc['documentclass'])
    except NameError:
        return 'bibkey(%s): no parser for documentclass: %s' % (
            key, doc['documentclass'])
    return fun(req, formatter, key, doc)

def simple_if(doc, key, res):
    if doc.has_key(key):
        res.append(', %s' % (doc[key]))
        
def print_doc_article(req, formatter, key, doc):
    res = []
    res.append('%s' % (doc['author']))
    res.append(', "%s"' % (doc['title']))
    res.append(", ''%s''" % (doc['journal']))
    if doc.has_key('volume'):
        res.append(', %s' % (doc['volume']))
        if doc.has_key('number'):
            res.append('(%s)' % (doc['number']))
    simple_if(doc, 'month', res)
    res.append(', %s' % (doc['year']))
    if doc.has_key('pages'):
        res.append(', pp. %s' % (doc['pages']))
    if doc.has_key('note'):
        res.append(', <i>%s</i>' % (doc['note']))
    if doc.has_key('doi'):
        res.append(', [[http://dx.doi.org/%s|DOI]]' % doc['doi'])
    res.append('.')
    return ''.join(res)

def print_doc_inproceedings(req, formatter, key, doc):
    res = []
    res.append('%s' % (doc['author']))
    res.append(', "%s"' % (doc['title']))
    res.append(', in<i>%s</i>' % (doc['booktitle']))
    if doc.has_key('editor'):
        res.append(', Ed. %s' % (doc['editor']))
    simple_if(doc, 'series', res)
    simple_if(doc, 'month', res)
    res.append(', %s' % (doc['year']))
    simple_if(doc, 'organization', res)
    simple_if(doc, 'publisher', res)
    simple_if(doc, 'address', res)
    if doc.has_key('pages'):
        res.append(', pp. %s' % (doc['pages']))
    if doc.has_key('note'):
        res.append(', <i>%s</i>' % (doc['note']))
    return ''.join(res)

def print_doc_book(req, formatter, key, doc):
    res = []
    if doc.has_key('author'):
        res.append('%s' % (doc['author']))
        res.append(', %s' % (doc['title']))
        if doc.has_key('editor'):
            res.append(', Ed. %s' % (doc['editor']))
    else:
        res.append('%s (Ed.)' % (doc['editor']))
        res.append(', %s' % (doc['title']))
    if doc.has_key('edition'):
        res.append(', %s Edition' % (doc['edition']))
    simple_if(doc, 'series', res)
    res.append(', %s' % (doc['publisher']))
    simple_if(doc, 'address', res)
    simple_if(doc, 'month', res)
    res.append(', %s' % (doc['year']))
    if doc.has_key('note'):
        res.append(', <i>%s</i>' % (doc['note']))
    return ''.join(res)

if __name__ == "__main__":
    bibdb = {}
    load_bibdb('foo.xml', bibdb)

    for i in bibdb.keys():
        print '%s' % (i)
        print '%s' % (printDocument(bibdb, i))

