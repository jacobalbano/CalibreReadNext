from calibre.customize import InterfaceActionBase

class InterfacePluginDemo(InterfaceActionBase):
    name                = 'Read Next'
    description         = 'Marks the first unrated book in each series'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Jacob Albano'
    version             = (1, 0, 1)
    minimum_calibre_version = (0, 7, 53)

    actual_plugin       = 'calibre_plugins.readnext.ui:InterfacePlugin'
    def is_customizable(self):
        return False

