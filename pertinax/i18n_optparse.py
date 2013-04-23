#
# Make optparse friendlier to i18n/l10n
#
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

"""
Make optparse friendlier to i18n/l10n

Just use this instead of optparse, the interface should be the same.

For some backgorund, see:
http://bugs.python.org/issue4319
"""

import sys

from okaara.cli import CommandUsage
from optparse import OptionParser as _OptionParser
from optparse import BadOptionError, OptionValueError

class OptionParserExitError(Exception):
    """
    Exception to indicate exit call from OptionParser.
    Takes error code as it's only argument.
    """
    pass

# pylint: disable=R0904
class OptionParser(_OptionParser):

    # These are a bunch of strings that are marked for translation in optparse,
    # but not actually translated anywhere. Mark them for translation here,
    # so we get it picked up. for local translation, and then optparse will
    # use them.
    @classmethod
    def __no_op(cls):
        _("Usage: %s\n")
        _("Usage")
        _("%prog [options]")
        _("Options")

        # stuff for option value sanity checking
        _("no such option: %s")
        _("ambiguous option: %s (%s?)")#dont_check_gettext
        _("%s option requires an argument")
        _("%s option requires %d arguments")#dont_check_gettext
        _("%s option does not take a value")
        _("integer")
        _("long integer")
        _("floating-point")
        _("complex")
        _("option %s: invalid %s value: %r")#dont_check_gettext
        _("option %s: invalid choice: %r (choose from %s)")#dont_check_gettext

        # default options
        _("show this help message and exit")
        _("show program's version number and exit")


    def get_option_by_dest(self, dest):
        for opt in self.option_list:
            if opt.dest == dest:
                return opt
        return None

    def get_option_by_name(self, name):
        for opt in ['--'+name, '-'+name]:
            if self.has_option(opt):
                return self.get_option(opt)
        return None

    def get_options(self):
        return self._long_opt.keys() + self._short_opt.keys()

    def get_long_options(self):
        return self._long_opt.keys()

    def get_short_options(self):
        return self._short_opt.keys()


class NoCatchErrorParser(OptionParser):
    """
    OptionParser's default behavior for handling errors is to print the output
    and exit. I'd rather go through the rest of the CLI's output methods, so
    change this behavior to throw my exception instead.
    """
    def exit(self, status=0, msg=None):
        raise CommandUsage(other_messages=msg)

    def error(self, msg):
        self.exit(0, msg)

    def print_help(self, file=None):
        # The CLI will take care of formatting the options for a --help call,
        # so do nothing here.
        pass

    def parse_args(self, args=None, values=None):
        """
        Copied directly from optparse with the change that an exception on
        _process_args isn't passed to error but rather converted into a
        CommandUsage. Bad optparse, passing a string version of the exception
        to error instead of the programmatically accessible data and letting
        error() do with it as it wishes.
        """
        rargs = self._get_args(args)
        if values is None:
            values = self.get_default_values()

        self.rargs = rargs
        self.largs = largs = []
        self.values = values

        try:
            self._process_args(largs, rargs, values)
        except BadOptionError, e:
            # Raise with the data, not a string version of the exception
            raise CommandUsage(unexpected_options=[e.opt_str])

        args = largs + rargs
        return self.check_values(values, args)
