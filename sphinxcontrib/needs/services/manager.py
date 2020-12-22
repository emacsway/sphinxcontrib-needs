import sphinx
from docutils.parsers.rst import directives
from pkg_resources import parse_version

from sphinxcontrib.needs.directives.needservice import NeedserviceDirective

sphinx_version = sphinx.__version__
if parse_version(sphinx_version) >= parse_version("1.6"):
    from sphinx.util import logging
else:
    import logging

    logging.basicConfig()  # Only need to do this once


class ServiceManager:
    def __init__(self, app):
        self.app = app

        self.log = logging.getLogger(__name__)
        self.services = {}

    def register(self, name, clazz, **kwargs):
        try:
            config = self.app.config.needs_services[name]
        except KeyError:
            self.log.warning(f'No service config found for {name}. Add it in your conf.py to needs_services dictionary.')
            config = {}

        # Register options from service class
        for option in clazz.options:
            if option not in self.app.config.needs_extra_options.keys():
                self.log.debug(f'Register option "{option}" for service "{name}"')
                self.app.config.needs_extra_options[option] = directives.unchanged
                # Register new option directly in Service directive, as its class options got already
                # calculated
                NeedserviceDirective.option_spec[option] = directives.unchanged

        # Init service with custom config
        self.services[name] = clazz(self.app, name, config, **kwargs)

    def get(self, name):
        if name in self.services.keys():
            return self.services[name]
        else:
            raise NeedsServiceException(f'Service {name} could not be found. '
                                        f'Available services are {", ".join(self.services)}')


class NeedsServiceException(BaseException):
    pass
