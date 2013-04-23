# -*- coding: utf-8 -*-
#
# Copyright 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU Lesser General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (LGPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of LGPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/lgpl-2.0.txt.


import re
import sys


from okaara.cli import Section

def parse_tokens(tokenstring):
    """
    Parse string as if it was command line parameters.
    @type tokenstring: string
    @param tokenstring: string with command line tokens
    @return List of tokens
    """
    from katello.client.cli.base import KatelloError

    tokens = []
    try:
        pattern = r'--?\w+|=?"[^"]*"|=?\'[^\']*\'|=?[^\s]+'

        for tok in (re.findall(pattern, tokenstring)):

            if tok[0] == '=':
                tok = tok[1:]
            if tok[0] == '"' or tok[0] == "'":
                tok = tok[1:-1]

            tokens.append(tok)
        return tokens
    except Exception, e:
        #TODO: define dedicated exception
        raise KatelloError("Unable to parse options", e), None, sys.exc_info()[2]


class Completion():

    def __init__(self, root_section):
        self.root_section = root_section

    @classmethod
    def __complete(cls, text, cmd, with_params=False):
        completions = cls.__get_possible_completions(cmd, with_params)
        return [a for a in completions if a.startswith(text)]

    @classmethod
    def __get_possible_completions(cls, cmd, with_params=False):
        """
        Return all possible subcommands and options that can be used to complete
        strings after a command cmd.
        """
        completions = []
        if isinstance(cmd, Section):
            completions += cmd.subsections.keys() + cmd.commands.keys()
        else:
            completions += cmd.parser.get_long_options()
        return completions


    def __get_command(self, names):
        """
        Return instance of last command used on the line. Names represent
        list of commands on the line.
        """
        cmd = self.root_section
        for name in names:
            if isinstance(cmd, Section):
                if name in (cmd.subsections.keys() + cmd.commands.keys()):
                    cmd = cmd.commands.get(name, cmd.subsections.get(name, None))
        return cmd


    def __parse_line(self, line):
        line_parts = parse_tokens(line)

        if line.endswith(" ") or not len(line):
            last_word = ""
            cmd = self.__get_command(line_parts)
        else:
            last_word = line_parts[-1]
            cmd = self.__get_command(line_parts[:-1])
        return (last_word, cmd)


    def complete(self, line):
        """
        Return the next possible completion for 'line'.
        """
        last_word, cmd = self.__parse_line(line)
        return self.__complete(last_word, cmd, with_params=True)


