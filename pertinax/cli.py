#
# Katello Organization actions
# Copyright 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#

import re

from pertinax.i18n_optparse import NoCatchErrorParser
from pertinax.option_validator import OptionValidator
from pertinax.ui.printer import Printer, GrepStrategy, VerboseStrategy

from okaara.cli import Cli, Command, CommandUsage, OptionGroup


# organization actions ---------------------------------------------------------


class PertinaxCommand(Command):

    def __init__(self, context):
        self.method = self.main
        self.parser = self._create_parser()
        self.context = context
        self.prompt = context.prompt
        self.api = context.bindings

        self.options = []
        self.option_groups = []
        self._setup_parser()

    def execute(self, prompt, args):
        self._load_saved_options()
        Command.execute(self, prompt, args)

    # pylint: disable=R0201
    @property
    def name(self):
        """
        Return a string with this command's name.
        By default the name is camel_case version of the Class name
        """
        s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.__class__.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()

    @property
    def description(self):
        """
        Return a string with this command's description
        """
        return _('no description available')

    @property
    def usage_description(self):
        """
        Return a string with this command's usage description
        """
        return ""

    def main(self, **options):
        """
        Main action of the command
        """
        try:
            self.printer = self._create_printer(options)
            self.validator = self._create_validator(options)
            self._check_options(options)
            self._process_option_errors()

            return self.run(options)
        except Exception, e:
            return self.context.exception_handler.handle_exception(e)

    def _create_parser(self):
        return NoCatchErrorParser()

    def _setup_parser(self):
        self._setup_options()
        self._setup_common_options()
        self._init_parser(self.parser)

    def _create_validator(self, options):
        return OptionValidator(self.parser, options)

    def _create_printer(self, options):
        return Printer(self._print_strategy(options), options.get('noheading'))

    def _load_saved_options(self):
        config = self.context.config

        if not config.has_section('options'):
            return
        for opt_name, opt_value in config.items('options'):
            opt = self.parser.get_option_by_name(opt_name)
            if not opt is None:
                self.parser.set_default(opt.get_dest(), opt_value)

    def _print_strategy(self, options):
        config = self.context.config

        if (options.get('g') or (config.has_option('interface', 'force_grep_friendly') \
            and config.get('interface', 'force_grep_friendly').lower() == 'true')):
            return GrepStrategy(delimiter=options.get('d'))

        elif (options.get('v') or (config.has_option('interface', 'force_verbose') \
            and config.get('interface', 'force_verbose').lower() == 'true')):
            return VerboseStrategy()

        else:
            return None

    def _process_option_errors(self):
        errors = self.validator.opt_errors
        if len(errors) > 0:
            raise CommandUsage(other_messages=errors)

    def _setup_common_options(self):
        formatting = OptionGroup("Output formatting:")
        formatting.create_flag('-g', _("grep friendly output"))
        formatting.create_flag('-v', _("verbose, more structured output"))
        formatting.create_flag('--noheading', _("Suppress any heading output. Useful if grepping the output."))
        formatting.create_option('--d', _("column delimiter in grep friendly output, works only with option -g"), required=False)
        self.add_option_group(formatting)

    def _setup_options(self):
        pass

    def _check_options(self, options):
        pass

    def run(self, options):
        pass

    def create_option(self, name, description, **kw_args):
        #commands are not required by default
        kw_args["required"] = kw_args.get("required", False)
        super(PertinaxCommand, self).create_option(name, description, **kw_args)


class PertinaxCli(Cli):

    def __init__(self, context):
        Cli.__init__(self, context.prompt)
        self.context = context

    def run(self, args):
        try:
            exit_code = Cli.run(self, args)
            return exit_code
        except Exception, e:
            exit_code = self.context.exception_handler.handle_exception(e)
            return exit_code


class ClientContext:

    def __init__(self, config, logger, prompt, exception_handler, bindings, cli=None):
        """
        This stuff is created in pulp.client.launcher

        :type server: pulp.bindings.bindings.Bindings
        :type config: pulp.common.config.Config
        :type logger: logging.Logger
        :type prompt: pulp.client.extensions.core.PulpPrompt
        :type exception_handler: pulp.client.extensions.exceptions.ExceptionHandler
        """
        #self.server = server
        self.config = config
        self.logger = logger
        self.prompt = prompt
        self.exception_handler = exception_handler
        self.bindings = bindings
        self.cli = cli
