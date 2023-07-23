import datetime
from typing import Any
import logging

from mkdocs.structure.pages import Page
from mkdocs.structure.files import Files
from mkdocs.exceptions import PluginError
from mkdocs.config import base as cfg_base, config_options as C

log = logging.getLogger("mkdocs.plugins")

def on_page_markdown(
        markdown: str, 
        page: Page,
        config: dict[str, Any],
        files: Files
    ):

    check_page_meta(page)



class PageMeta(cfg_base.Config):
    create_time = C.Type(datetime.date)
    update_time = C.Optional(C.Type(datetime.date))


def check_page_meta(page: Page):

    if not page.meta:
        raise PluginError(f"Page {page.file.src_path} has no meta data")

    meta = PageMeta()
    meta.load_dict(dict(page.meta))
    failed, warnings = meta.validate()
    if failed:
        log.error(f"Page {page.file.src_path} meta data error:")
        for error in failed:
            log.error(f'"{error[0]}": {error[1]}')
        raise PluginError(f"Page meta check failed.")