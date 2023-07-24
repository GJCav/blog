import re
import sys
from . import g

import jinja2

from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Navigation
from mkdocs.structure.files import Files, File
from mkdocs import utils
from mkdocs.utils.meta import get_data
from mkdocs.exceptions import PluginError

import logging
import os
import os.path
import time
from copy import copy

from lxml.html import fragment_fromstring, tostring

log = logging.getLogger("mkdocs.plugins")

def on_env(
        env: jinja2.Environment, 
        config: dict, 
        files: Files
    ):

    generate_excerpt(config, files)


def generate_excerpt(
        config, 
        files: Files
    ):
    
    if g.welcome_page is None:
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
            file = File(path, g.tempdir, config.site_dir, urls)
            files.append(file)

            # Mark file as generated, so other plugins don't think it's part
            # of the file system. This is more or less a new quasi-standard
            # for plugins that generate files which was introduced by the
            # git-revision-date-localized-plugin - see https://bit.ly/3ZUmdBx
            file.generated_by = "material/blog" # type: ignore

        # Return file
        return file
    
    for article in g.articles:
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
                url = utils.get_relative_url(excerpt.file.url, g.welcome_page.file.url) # type: ignore
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

        article["content"] = content
        del article["path"]
    
    # Sort articles by date
    g.articles.sort(key = lambda a: a["meta"]["date"], reverse = True)
    g.recent_articles = g.articles[:10]