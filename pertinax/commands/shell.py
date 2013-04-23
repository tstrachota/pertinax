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

import os

from katello.client.core.base import BaseAction

import pertinax.shell
from pertinax.cli import PertinaxCommand

# shell action ------------------------------------------------------------

class Shell(PertinaxCommand):

    name = "shell"
    description = _('run the cli as a shell')

    def __init__(self, context):
        super(Shell, self).__init__(context)
        self.cli = context.cli

    def run(self, options):
        self.cli.remove_command(self.name)
        shell = pertinax.shell.Shell(self.cli, prompt="foreman> ")
        shell.cmdloop()

        return os.EX_OK
