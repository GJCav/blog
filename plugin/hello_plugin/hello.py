from mkdocs.config import base, config_options as c
from mkdocs.plugins import BasePlugin
from mkdocs.plugins import get_plugin_logger

log = get_plugin_logger(__name__)

class _ValidationOptions(base.Config):
    enabled = c.Type(bool, default=True)
    verbose = c.Type(bool, default=False)
    skip_checks = c.ListOfItems(c.Choice(('foo', 'bar', 'baz')), default=[])

class MyPluginConfig(base.Config):
    definition_file = c.File()  # required
    checksum_file = c.Optional(c.File(exists=True))  # can be None but must exist if specified
    validation = c.SubConfig(_ValidationOptions)

class HelloworldPlugin(BasePlugin[MyPluginConfig]):
    def on_config(self, config):
        log.info("hello world")
        return config