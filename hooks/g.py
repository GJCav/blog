from tempfile import gettempdir
from mkdocs.structure.pages import Page

welcome_page: Page | None = None
articles = []
recent_articles = []
tempdir: str = "/tmp/"


def reset():
    global welcome_page, articles, recent_articles
    welcome_page = None
    articles = []
    recent_articles = []
    tempdir = gettempdir()