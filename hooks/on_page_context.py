from typing import Any
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation

import os
import os.path
import time

from . import g

def on_page_context(
        context: dict[str, Any], 
        page: Page, 
        config,
        nav: Navigation
    ):

    if page.file.src_path == "README.md":
        attach_articles(context, page, config, nav)
    return context


def attach_articles(
        context: dict[str, Any],
        page: Page,
        config,
        nav: Navigation
    ):
    context["recent_articles"] = g.recent_articles