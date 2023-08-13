from typing import Any
from mkdocs.config import base, config_options as C
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files
import datetime

log = get_plugin_logger(__name__)

class _Config(base.Config):
    pass


class PageMeta(base.Config):
    """
    Page meta declaration. 

    All pages should contain metas declared bellow.
    """

    create_time = C.Type(datetime.date)
    update_time = C.Optional(C.Type(datetime.date))

class JCavMetaPlugin(BasePlugin[_Config]):
    def on_page_markdown(
            self,
            markdown: str, 
            page: Page,
            config: dict[str, Any],
            files: Files
    ):
        self.check_page_meta(page)
    
    def check_page_meta(self, page):
        if not page.meta:
            log.error(f"Page {page.file.src_path} has no meta data")
            # raise PluginError(f"Page {page.file.src_path} has no meta data") # ignore it

        meta = PageMeta()
        meta.load_dict(dict(page.meta))
        failed, warnings = meta.validate()
        if failed:
            log.error(f"Page {page.file.src_path} meta data error:")
            for error in failed:
                log.error(f'  "{error[0]}": {error[1]}')
            # raise PluginError(f"Page meta check failed.") # ignore it