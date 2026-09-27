"""Pin derico's pages to light: the design has no dark palette."""

import re

from plone.transformchain.interfaces import ITransform
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

from plonetheme.derico.interfaces import IPlonethemeDericoLayer


LIGHT = 'data-bs-theme="light"'
_HTML_TAG = r"<html\b(?![^>]*\bdata-bs-theme=)"
_TEXT = re.compile(_HTML_TAG, re.I)
_BYTES = re.compile(_HTML_TAG.encode(), re.I)


@implementer(ITransform)
@adapter(Interface, IPlonethemeDericoLayer)
class LightColorMode:
    order = 100

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def _is_html(self):
        content_type = self.request.response.getHeader("Content-Type") or ""
        return content_type.startswith("text/html")

    def transformUnicode(self, result, encoding):
        if not self._is_html():
            return None
        new, count = _TEXT.subn(f"<html {LIGHT}", result, count=1)
        return new if count else None

    def transformBytes(self, result, encoding):
        if not self._is_html():
            return None
        new, count = _BYTES.subn(f"<html {LIGHT}".encode(), result, count=1)
        return new if count else None

    def transformIterable(self, result, encoding):
        if not self._is_html():
            return None
        return self.transformBytes(b"".join(result), encoding)
