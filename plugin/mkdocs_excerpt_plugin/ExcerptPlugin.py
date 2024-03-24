from tempfile import gettempdir
from typing import Any
import jinja2
from mkdocs.config import base, config_options as c
from mkdocs import utils
from mkdocs.utils.meta import get_data
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure.files import Files, File
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation
from mkdocs.exceptions import PluginError

import sys
import os
import os.path
import time
import datetime
from copy import copy
import re

from lxml.html import fragment_fromstring, tostring

log = get_plugin_logger(__name__)


class ExcerptPlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__()
    
    def _reset(self):
        self.welcome_page = None
        self.articles = []
        self.recent_articles = []
        self.tempdir = gettempdir()

    def on_config(self, config):
        self._reset()
        return config

    def on_nav(
            self, 
            nav: Navigation,
            config: dict,
            files: Files
    ):
        """
        here we get the meta data of each page
        """
        for page in nav.pages:
            file = page.file

            if page.url == "":
                self.welcome_page = page
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

                if meta.get("disable_excerpt"):
                    continue

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
                    post["meta"]["date"] = datetime.date.fromtimestamp(timestamp)
                post["meta"]["date_format"] = post["meta"]["date"]
            
            self.articles.append(post)
    

    def on_env(
            self,
            env: jinja2.Environment, 
            config: dict, 
            files: Files
    ):
        """
        generate an excerpt for each article
        """

        if self.welcome_page is None:
            raise PluginError("Welcome page not found")
        
        # Copy configuration and enable 'toc' extension
        config                    = copy(config)
        config.mdx_configs["toc"] = copy(config.mdx_configs.get("toc", {}))

        # Ensure that post titles are links
        config.mdx_configs["toc"]["anchorlink"] = True
        config.mdx_configs["toc"]["permalink"]  = False

        def __register_file(path, config, files=Files([])):
            file = files.get_file_from_path(path)
            if not file:
                urls = config.use_directory_urls
                file = File(path, self.tempdir, config.site_dir, urls)
                files.append(file)

                # Mark file as generated, so other plugins don't think it's part
                # of the file system. This is more or less a new quasi-standard
                # for plugins that generate files which was introduced by the
                # git-revision-date-localized-plugin - see https://bit.ly/3ZUmdBx
                file.generated_by = "material/blog" # type: ignore

            # Return file
            return file
        
        for article in self.articles:
            base = files.get_file_from_path(article["path"])

            if not base:
                log.error("Base not found: " + article["path"])
                sys.exit(1)

            file = base
            page = file.page # ????

            if not page:
                log.error("Page not found: " + file.src_path)
                sys.exit(1)

            temp = __register_file(file.src_uri, config)
            excerpt = Page(page.title, temp, config)

            # Ensure separator at the end to strip footnotes and patch h1-h5
            separator = "<!-- more -->"
            markdown = page.markdown or "##"
            if separator not in markdown: # type: ignore
                log.warning("Excerpt separator not found: " + file.src_path)
                markdown = re.sub(
                    r"^(##.*)$", 
                    f"\n\n{separator}\n\n\\1", 
                    markdown, 
                    count=1, flags=re.MULTILINE
                )

                if separator not in markdown: # type: ignore
                    markdown += "\n\n" + separator
            markdown = re.sub(r"(^#{1,5})", "#\\1", markdown, flags = re.MULTILINE)

            # Extract content and metadata from original post
            excerpt.file.url = base.url
            excerpt.markdown = markdown
            excerpt.meta     = page.meta

            # Render excerpt
            excerpt.render(config, files)
            excerpt.file.url = page.url

            # Find all anchor links
            expr = re.compile(
                r"<a[^>]+href=['\"]?#[^>]+>",
                re.IGNORECASE | re.MULTILINE
            )

            # Replace callback
            first = True
            def replace(match):
                value = match.group()

                # Handle anchor link
                el = fragment_fromstring(value.encode("utf-8"))
                if el.tag == "a":
                    nonlocal first

                    # Fix up each anchor link of the excerpt with a link to the
                    # anchor of the actual post, except for the first one – that
                    # one needs to go to the top of the post. A better way might
                    # be a Markdown extension, but for now this should be fine.
                    url = utils.get_relative_url(
                        excerpt.file.url, 
                        self.welcome_page.file.url
                    ) # type: ignore
                    if first:
                        el.set("href", url)
                    else:
                        el.set("href", url + el.get("href"))

                    # From now on reference anchors
                    first = False

                # Replace link opening tag (without closing tag)
                return tostring(el, encoding = "unicode")[:-4]

            # Extract excerpt from post and replace anchor links
            content = expr.sub(
                replace, # type: ignore
                excerpt.content.split(separator)[0] # type: ignore
            )

            # Find all image links and fix them
            expr = re.compile(
                r"<img[^>]+src.*?\\?>",
                re.IGNORECASE | re.MULTILINE
            )

            def replace_img_src(match):
                value = match.group()
                el = fragment_fromstring(value.encode("utf-8"))
                if el.tag == "img":
                    file_url = excerpt.file.url
                    src_url = el.get("src")

                    if src_url[0:1] in ("/", "."):
                        src_url = file_url + src_url
                        el.set("src", src_url)

                return tostring(el, encoding = "unicode")
            
            content = expr.sub(replace_img_src, content)

            article["content"] = content
            del article["path"]
        
        # Sort articles by date
        self.articles.sort(key = lambda a: a["meta"]["date"], reverse = True)
        self.recent_articles = self.articles[:10]
    
    def on_page_context(
            self,
            context: dict[str, Any], 
            page: Page, 
            config,
            nav: Navigation
    ):
        """
        attach recent article information to welcome page
        """
        if page.file.src_path == "README.md":
            context["recent_articles"] = self.recent_articles
        
        return context
