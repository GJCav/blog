from typing import Any
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation

import os
import os.path
import time

def on_page_context(
        context: dict[str, Any], 
        page: Page, 
        config,
        nav: Navigation
    ):

    if page.file.src_path == "README.md":
        attach_statistics(context, page, config, nav)

    attach_time_info(context, page, config, nav)

    return context


def attach_time_info(
        context: dict[str, Any], 
        page: Page, 
        config,
        nav: Navigation
    ):

    if page.meta and page.meta.get("update_time", None):
        context["update_time"] = page.meta.get("update_time", None)
    
    if page.meta and page.meta.get("create_time", None):
        context["create_time"] = page.meta.get("create_time", None)


def attach_statistics(
        context: dict[str, Any], 
        page: Page, 
        config,
        nav: Navigation
    ):
    # Get the number of pages
    context["num_pages"] = len(nav.pages)

    # Get the number of tags
    tags = set()
    for page in nav.pages:
        tags.update(page.meta.get("tags", []))
    context["num_tags"] = len(tags)

    # Get the number of categories
    cat_nums = 0
    docs_path = config["docs_dir"]
    for name in os.listdir(docs_path):
        if name in ["assets", "javascripts"]:
            continue
        if os.path.isdir(os.path.join(docs_path, name)):
            cat_nums += 1
    context["num_categories"] = cat_nums