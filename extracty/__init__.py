"""

    extracty -- metadata extraction from HTML documents
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This library provides a set of tools to extract various metadata from HTML
    documents, such as title, timestamps, authorship and so on.

"""

import argparse
import re
import urlparse
import justext
import lxml.html


from .author import extract_author
from .content import extract_content
from .image import extract_cover_image
from .title import extract_title
from .content import extract_content
from .utils import gen_matches_any, html_to_text, precedings, fetch_url

__all__ = (
    'extract', 'extract_author', 'extract_cover_image', 'extract_title',
    'html_to_text')

def extract(doc, src, author=True, cover_image=True, title=True, content=True, url=True):
    """ Extract metadata from HTML document"""
    if isinstance(doc, basestring):
        doc = lxml.html.fromstring(doc)

    metadata = dict()

    if url:
        metadata['url'] = src

    if author:
        metadata['author'] = extract_author(doc)

    if title:
        metadata['title'] = extract_title(doc)

    if cover_image:
        extracted = extract_cover_image(doc, src)
        if extracted:
            extracted = urlparse.urljoin(src, extracted)
        metadata['cover_image'] = extracted

    # this should go last, because it mutates tree
    if content:
        metadata['content'] = extract_content(doc, src)

    return metadata

FIELDS = TITLE, AUTHOR, COVER_IMAGE, URL, CONTENT = 'title', 'author', 'cover_image', 'url', 'content'

def main():
    PARSER = argparse.ArgumentParser(description='Extract meta data from HTML pages')
    PARSER.add_argument('-u', '--url', type=str, help='url to use in case of filename provided')

    PARSER.add_argument('src', type=str, help='url or filename')

    PARSER.add_argument(
        '--no-title', action='append_const', const=TITLE,
        dest='exclude', help='do not extract title')
    PARSER.add_argument(
        '--no-author', action='append_const', const=AUTHOR,
        dest='exclude', help='do not extract title')
    PARSER.add_argument(
        '--no-cover-image', action='append_const', const=COVER_IMAGE,
        dest='exclude', help='do not extract title')
    PARSER.add_argument(
        '--exclude', '-x', choices=FIELDS,
        dest='exclude', action='append', help='Do not show field')
    PARSER.add_argument(
        '--include', '-i',
        choices=FIELDS, dest='include', action='append', help='Show this field')
    args = PARSER.parse_args()

    import urllib2
    args = PARSER.parse_args()

    if args.src.lower().startswith('http'):
        src_url = args.src
        data = fetch_url(src_url)
    else:
        src_url = args.url or ''
        with open(args.src) as stream:
            data = stream.read()


    included_fields = args.include or FIELDS
    excluded_fields = args.exclude or []

    author = AUTHOR in included_fields and AUTHOR not in excluded_fields
    title = TITLE in included_fields and TITLE not in excluded_fields
    cover_image = COVER_IMAGE in included_fields and COVER_IMAGE not in excluded_fields
    content = CONTENT in included_fields and CONTENT not in excluded_fields
    url = URL in included_fields and URL not in excluded_fields

    metadata = extract(
        data, src=src_url,
        author=author, title=title, cover_image=cover_image,
        content=content, url=url)

    illegal_fields = set(metadata) - set(FIELDS)

    assert not illegal_fields, illegal_fields

    for k, v in metadata.items():
        v = v or ''
        print '%s\t%s' % (k, v.encode('utf8'))
