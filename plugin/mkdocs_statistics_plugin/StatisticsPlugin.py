import os
from typing import Any
from mkdocs.config import base, config_options as c
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation

log = get_plugin_logger(__name__)

class _Config(base.Config):
    pass

class StatisticsPlugin(BasePlugin[_Config]):
    
    def on_page_context(
            self,
            context: dict[str, Any], 
            page: Page, 
            config,
            nav: Navigation
    ):
        if page.file.src_path == "README.md":
            self.attach_statistics(context, page, config, nav)
        
        self.attach_time_info(context, page, config, nav)
    
    def attach_time_info(
            self,
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
            self,
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
