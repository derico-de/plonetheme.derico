"""The blocks view links `static-blocks/blocks.css` outside Plone's resource
registry, so it ships minified."""

import re

from . import clara_css as css_tools


STALE = "blocks.css is not minified: run `pnpm build`"


@css_tools.needs_block_sheets
def test_the_block_sheets_ship_without_comments():
    for path in css_tools.BLOCK_SHEETS:
        assert "/*" not in path.read_text(), STALE


@css_tools.needs_block_sheets
def test_the_block_sheets_ship_without_indentation():
    for path in css_tools.BLOCK_SHEETS:
        assert not re.search(r"^\s", path.read_text(), re.MULTILINE), STALE
