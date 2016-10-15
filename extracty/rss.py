"""

     extracy.rss -- rss information extraction

"""

import lxml.html

__all__ = ('extract_rss',)

def extract_rss(doc, url):
    """ Extract the rss alternative from a page

    :param doc:
        HTML as a string or as ElementTree node
    :param url:
        URL of a document

    """

    if isinstance(doc, basestring):
        doc = lxml.html.fromstring(doc)

    return map(str, doc.xpath('//head/link[@rel="alternate"][@type="application/rss+xml"]/@href'))
