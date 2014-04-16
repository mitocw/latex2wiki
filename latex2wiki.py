#!/usr/bin/python
#
# File:   latex2wiki.py
# Date:   30-Sep-09
# Author: I. Chuang <ichuang@mit.edu>
#
# Note: edit mediawiki math/texutil.ml to include the line
#    | "\\rule"             -> (tex_use_ams () ; FUN_AR2 "\\rule ")
# near the similar dfrac line
#
# 28-Oct-09 add matrix environment, wikitext command
# 30-Oct-09 add multi-level lists, wiki option on inlinepsfig, fix unicode forward quote
# 24-Sep-10 fix $a_x$ -> <math>a_ x</math> problem

import os, sys, string, time, re

from plasTeX import Base
from plasTeX.Renderers import Renderer
from plasTeX.TeX import TeX

footnotetab = []

class BOX(Base.Command):
    """ \BOX{ref}{label}{caption} """
    args = 'ref label caption'
    def invoke(self, tex):
        Base.Command.invoke(self, tex)

class wikitext(Base.Command):
    """ \wikitext{wiki_text} """
    args = 'wikitext'
    def invoke(self, tex):
        Base.Command.invoke(self, tex)

class inlinepsfig(Base.Command):
    """ \inlinepsfig{file}{size} """
    args = 'file size'
    def invoke(self, tex):
        Base.Command.invoke(self, tex)

class matrix(Base.Environment):
    args = ''
    def invoke(self, tex):
        Base.Environment.invoke(self,tex)

class Renderer(Renderer):
    
    #def do_math(self,node):
    #    return '<math>%s</math>' % node.source

    def fixmath(self,ns):

        # fix $a_x$ -> <math>a_ x</math> problem
        ns = re.sub('(.)_ ([A-Za-z])','\\1_\\2',ns)

        # fix bf -> mathbf
        ns = ns.replace('\\bf ','\\mathbf ')

        # fix em -> delete
        ns = ns.replace('\\em ','')

        # fix cal -> mathcal
        ns = ns.replace('\\cal ','\\mathcal ')

        # fix lefteqn -> &
        ns = ns.replace('\\lefteqn','&')

        # no funny e's
        ns = ns.replace('\\`{e}','e')

        # fix \mbox{$foo$} problem
        #m = re.search('(.*)\\mbox{\$(.*)\$}(.*)'
        #ns = ns.replace('\\mbox{','{\\rm ')
        def fixspace(m):
            m1 = m.group(1).replace(' ','~')
            return('{\\rm %s}' % m1)
        ns = re.sub(r'\\mbox{([^}]+)}',fixspace,ns)

        # remove hspace*
        ns = re.sub(r'\\hspace\*{[^}]+}','',ns)
        ns = re.sub(r'\\hspace{[^}]+}','',ns)

        return(ns) 

    def default(self, node):
        """ Rendering method for all non-text nodes """
        s = []

        # Handle characters like \&, \$, \%, etc.
        if len(node.nodeName) == 1 and node.nodeName not in string.letters:
            return self.textDefault(node.nodeName)

        procset = [
            ('center','<center>','</center>'),
            ('quote','<blockquote>','</blockquote>'),
            ('em',"''","''"),
            ('bf',"'''","'''"),
            ('document','',''),
            ('enumerate','<ul>','</ul>'),
            ('itemize','<ul>','</ul>'),
            ('bgroup','',''),
            ('hline','',''),
            ('proof','',''),
            ('verbatim','<pre>','</pre>'),
            ('notes','',''),
            ('vspace','',''),
            ('vskip','',''),
            ('textsc','',''),
            ('hrule','',''),
            ('underline','',''),
            ('flushleft','',''),
            ('copyright','',''),
            ('def','',''),		# leftover after ifCUP?
            ('sc','<font color=green>','</font>'),
            ('hspace','',''),
            ('noindent','',''),
            ('par','','\n\n'),
            ('active::~',' ',''),
            ]

        list_procset = ['enumerate','itemize']

        def do_section_type(sep):
            #s = '\n==== %s ====\n %s' % (node.attributes['title'],unicode(node))
            #return s
            s.append('<br style="clear: both" />\n%s %s %s\n' % (sep,node.attributes['title'],sep))
            s2 = unicode(node)
            if (s2[0]==' '):
                s2 = s2[1:]
            s.append(s2)	# recurse 

        if (node.nodeName=='document'):
            s.append(unicode(node))	# recurse 
            s = u'\n'.join(s)
            s = s.replace('\n <span','\n<span')
            s = s.replace('</center>\n\n ','</center>\n\n')
            s = s.replace('</blockquote>\n\n ','</blockquote>\n\n')
            s = s.replace('\n\n<li>','\n<li>')
            s = s.replace('\n\n<li>','\n<li>')
            s = s.replace('\n\n<ul>','\n<ul>')
            s = s.replace('\n\n<ul>','\n<ul>')
            s = s.replace('\n\n</ul>','\n</ul>')
            s = s.replace('\n\n</ul>','\n</ul>')
            s = s.replace('</ul>\n\n','</ul>\n')
            s = s.replace('</ul>\n\n','</ul>\n')
            s = s.replace('</ul>\n ','</ul>\n')
            s = s.replace('</pre>\n\n ','</pre>\n\n')
            s = s.replace('</pre>\n ','</pre>\n')
            s = s.replace('\n\n\n<item>','\n\n<item>')
            s = s.replace('\n<item>','<br style="clear: both" />\n\n*')
            s = s.replace(u'\u2018',"''")	# unicode single forward quote
            s = s.replace(u'\u2019',"'")	# unicode single quote
            s = s.replace(u'\u201d',"''")	# unicode double quote
            s = s.replace('</math>\n\n ','</math>\n\n')
            s = s.replace('<ENDMATH>\n\n ','\n\n')
            s = s.replace('<ENDMATH>\n ','\n')
            s = s.replace('<ENDMATH>\n','\n')
            s = s.replace('<END>\n\n\n ','\n\n')
            s = s.replace('<END>\n\n ','\n\n')
            s = s.replace('<END>\n ','\n')
            s = s.replace('<END>\n','\n')

            if len(footnotetab)>0:
                s = s + "==== Footnotes ====\n"
                #s = s + '<references group="note"/>\n'
                s = s + '<references />\n'

            if s[0]==' ':
                s = s[1:]
            return s

        elif (node.nodeName=='section'):
            do_section_type('==')
            return u'\n'.join(s)

        elif (node.nodeName=='subsection'):
            do_section_type('===')
            return u'\n'.join(s)

        elif (node.nodeName=='subsubsection'):
            do_section_type('====')
            return u'\n'.join(s)

        elif (node.nodeName=='index'):
            #s.append('<span id="%s"></span>' % string.join(node.attributes['entry'],''))
            s.append('<span id="%s"></span>' % node.source)
            return u'\n'.join(s)

        elif (node.nodeName=='label'):
            #s = ('<span id="label:%s"></span>' % node.attributes['label'])
            s = ('<span id="%s"></span>' % node.attributes['label'])
            return(s)

        elif (node.nodeName=='ref'):
            an = node.source[5:-1]	# anchor name
            #s = '[[{{SUBPAGENAME}}#label:%s|%s]]' % (an,an)
            s = '[[{{SUBPAGENAME}}#%s|%s]]' % (an,an)
            return(s)

        elif (node.nodeName=='item'):
            #itemtxt = unicode(node).replace('\n\n','\n')
            itemtxt = unicode(node)
            s.append('<li> %s\n' % itemtxt)
            return u'\n'.join(s)

        # psfig (inline)

        elif (node.nodeName=='inlinepsfig'):
            #print "in psfig: "
            n_file = node.attributes['file']
            n_size = node.attributes['size']
            #for key, value in node.attributes.items():
            #    print " attribute ",key," = ",value
            #print node.source
            #s = '[[Image:%s|thumb|600px|]]' % (n_file)
            m = re.search('wiki:(.*)',unicode(n_size))
            if m:
                opts = m.group(1)
            else:
                opts = ''
            s = '[[Image:%s|%s]]' % (n_file,opts)
            return(s)

        # table

        elif (node.nodeName=='table'):

            caption = ''
            for k in node.allChildNodes:
                if (k.nodeName=='caption'):
                    #caption = k.source[9:-1]
                    caption = unicode(k).replace('\n',' ')
                    #print "caption = ",caption
                    kcn = k
            #node.allChildNodes.remove(kcn)
            ns = node.source
            #print "table: allChildNodes ",repr(node.allChildNodes)
            #print "node: ",dir(node)

            ntxt = unicode(node)
            ntxt2 = ''
            mode = 0
            for k in ntxt.split('\n'):
                if k.count('<caption>'):
                    #print "caption line found: ",k
                    mode = 1
                if mode==0:
                    ntxt2 += k + '\n'
                if k.count('</caption>'):
                    mode = 0

            s = '<table align=right style="width:auto; border: 1px solid #aaa; font-size: 100%; padding: 4px; margin: 0.5em 0 0.8em 1.4em; float: right; clear: right; background: #f9f9f9;">\n'
            s += '<tr><td>%s</td></tr>\n' % ntxt2
            s += '<tr><td>%s</td></tr>\n' % caption
            s += '</table><END>\n'	# "<END>" to get rid of following space

            #print "Table: ",s
            #print "-----------"

            return(s)

        # tabular

        elif (node.nodeName=='tabular'):
            #print "in tabular: "
            #print dir(node)
            s.append('<table border=1>')
            for k in node.childNodes:	# should be ArrayRow's
                if (k.nodeName=='ArrayRow'):
                    s.append('<tr>')
                    for m in k.childNodes:	# should be ArrayCell
                        if (m.nodeName=='ArrayCell'):
                            s.append('<td>%s</td>' % unicode(m).rstrip())
                    s.append('</tr>')
            s.append('</table>')
            return u'\n'.join(s)

        # wikitext

        elif (node.nodeName=='wikitext'):
            ns = node.source[1:-1]
            s = '%s' % ns.replace('wikitext{','')
            return(s)

        # BOX (special for NC00)

        elif (node.nodeName=='BOX'):
            #print "in Box: "
            #for k in node.allChildNodes:
            #    print "box child: ",k.nodeName
            n_ref = node.attributes['ref']
            n_label = node.attributes['label']
            #n_caption = unicode(node.attributes['caption']).replace('\n',' ')
            n_caption = unicode(node.attributes['caption'])
            s.append('<table border="1" style="width:75%; color:blue" align="center">')
            s.append('<tr align=center><td>%s</td></tr>' % n_label)
            s.append('<tr><td>%s' % n_caption)
            s.append('</td></tr></table>')
            return u'\n'.join(s)

        # footnote

        elif (node.nodeName=='footnote'):
            #print "math dir: ",dir(node)
            print "footnote node: ",node.source
            ns = node.source[1:-1]

            # get footnote number
            num = "num%d" % node.attributes['num']
            print "footnote num: ",num

	    footnotetab.append(num)

            # render
            #s.append('<ref group="note" name="%s">%s</ref>' % (num,unicode(node)))
            s.append('<ref name="%s">%s</ref>' % (num,unicode(node)))
            return u'\n'.join(s)

        # math

        elif (node.nodeName=='math'):
            # print "math dir: ",dir(node)
            # print "math node: ",node.source
            ns = node.source[1:-1]
            
            ns = self.fixmath(ns)

            s = '<math>%s</math>' % ns
            return(s)

        elif (node.nodeName=='displaymath'):
            ns = node.source[2:-2]
            # print "displaymath node: ",ns[2:-2]
            ns = self.fixmath(ns)
            s = '<math>%s</math>' % ns
            return(s)

        elif (node.nodeName=='eqnarray'):
            ns = node.source.replace('eqnarray','align')
            ns = ns.replace('\\nonumber','')

            ns = self.fixmath(ns)

            # check to see if it uses a label; if so, use template
            if (ns.count('\\label')>0):
                m = re.search('(.*)\label{([^}]+)}(.*)',ns)
                math = m.group(1) + ' ' + m.group(3)

                # remove other instances of label (FIXME)
                math = re.sub(r'\\label{([^}]+)}','',math)

                label = m.group(2)
                s = '<br style="clear: both" />\n'
                s += '{{EqL\n|math=<math>%s</math>\n|num=%s\n}}<ENDMATH>' % (math.replace('\n',' '),label)
            else:
                s = ':<math>%s</math>' % ns
            return(s)

        elif (node.nodeName=='equation'):
            ns = node.source.replace('equation','align')
            ns = ns.replace('\\nonumber','')
            #print "math equation node: ",node.source

            ns = self.fixmath(ns)
            #print "ns: ",ns

            # check to see if it uses a label; if so, use template
            if (ns.count('\\label')>0):
                m = re.search('(.*)\label{([^}]+)}(.*)',ns)
                math = m.group(1) + ' ' + m.group(3)
                label = m.group(2)
                s = '{{EqL\n|math=<math>%s</math>\n|num=%s\n}}<ENDMATH>' % (math.replace('\n',' '),label)
            else:
                s = ':<math>%s</math>' % ns
            return(s)

        # figures (assume simple figure format)
        
        elif (node.nodeName=='figure'):
            #print dir(node)
            #print node.allChildNodes
            caption = ''
            for k in node.allChildNodes:
                if (k.nodeName=='caption'):
                    #caption = k.source[9:-1]
                    caption = unicode(k).replace('\n',' ')
                    #print "caption = ",caption
            ns = node.source
            #print "in figure, source = ",ns
            if (ns.count('\\psfig')>1):
                print "Oops!  figure too complex: ",ns

            m = re.search('\\psfig\s*{file=([^},]+)([^}]*)}',ns)
            if m:
                fn = m.group(1)
                #fn = m.group(1).replace('/',':')
                size = m.group(2)
            else:
                m = re.search('\\includegraphics\s*\[([^]]+)\]{([^}]+)}',ns)
                if m:
                    fn = m.group(2)
                    size = m.group(1)
                else:
                    print "error in figure: ",ns
            #m = re.search('\\caption\s*{([^}]+)}',ns)
            #if m:
            #    caption = m.group(1)
            #else:
            #    caption = ''
            m = re.search('\\label\s*{([^}]+)}',ns)
            if m:
                label = '<span id="%s"></span>\n' % m.group(1)
            else:
                label = ''
            #s = label + '[[Image:%s|frame|thumb|600px|%s]]' % (fn,caption)
            s = label + '[[Image:%s|thumb|600px|%s]]' % (fn,caption)
            return(s)

        # simple nodes
        
        else:
            for name, stag, etag in procset:	# handle simple node processing

                if (node.nodeName==name):
                    s.append(stag + unicode(node) + etag)
                    return u'\n'.join(s)

        # unknown tag - just output
        s.append('<%s>' % node.nodeName)
        if node.hasAttributes():
            s.append('<attributes>')
            for key, value in node.attributes.items():
                # If the key is 'self', don't render it
                # these nodes are the same as the child nodes
                if key == 'self':
                    continue
                s.append('<%s>%s</%s>' % (key, unicode(value), key))
            s.append('</attributes>')
        s.append(unicode(node))	# recurse 
        s.append('</%s>' % node.nodeName)
        return u'\n'.join(s)

    def textDefault(self, node):
        """ Rendering method for all text nodes """
        return node.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')        


# Instantiate a TeX processor and parse the input text

fn = sys.argv[1]
print "fn=",fn

tex = TeX()
tex.ownerDocument.config['files']['split-level'] = -100
tex.ownerDocument.config['files']['filename'] = fn+'.wiki'

tex.ownerDocument.context.importMacros({1:BOX})
tex.ownerDocument.context.importMacros({2:inlinepsfig})
tex.ownerDocument.context.importMacros({3:matrix})
tex.ownerDocument.context.importMacros({4:wikitext})

ifn = fn + '.tex'

tex.input(open(ifn).read())
document = tex.parse()

# Render the document
renderer = Renderer()
renderer.render(document)

#print document
