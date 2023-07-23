from . import g

from mkdocs.structure.nav import Navigation
from mkdocs.structure.files import Files
from mkdocs import utils
from mkdocs.utils.meta import get_data
from mkdocs.exceptions import PluginError

import logging
import os
import os.path
import time

log = logging.getLogger("mkdocs.plugins")

def on_nav(
        nav: Navigation,
        config: dict,
        files: Files
    ):
    
    save_recent_articles(nav, config, files)


def save_recent_articles(
        nav: Navigation,
        config: dict,
        files: Files
    ):

    for page in nav.pages:
        file = page.file

        if page.url == "":
            g.welcome_page = page
            continue

        post = {
            "meta": {},
            "url": page.url,
            "content": "",
            "path": file.src_uri
        }

        # but at this point, page.meta is empty
        # so we have to read the file and get meta data from it
        with open(file.abs_src_path, "r", encoding="utf-8") as f:
            markdown, meta = get_data(f.read())

            post["meta"] = dict(meta)

            if "date" in meta:
                log.warning("meta field \"date\" is ignored in file: " + file.src_path)
            if "update_time" in meta:
                post["meta"]["date"] = meta["update_time"]
            elif "create_time" in meta:
                post["meta"]["date"] = meta["create_time"]
            else:
                # read last modified time from file
                timestamp = os.path.getmtime(file.abs_src_path)
                date_str = time.strftime("%Y-%m-%d", time.localtime(timestamp))
                post["meta"]["date"] = date_str
            post["meta"]["date_format"] = post["meta"]["date"]
        
        g.articles.append(post)