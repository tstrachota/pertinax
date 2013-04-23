# -*- coding: utf-8 -*-
#
# Copyright © 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

"""
Centralized logic for handling the series of expected exceptions coming from
server operations (i.e. the 400 series of HTTP status codes). The handling
includes displaying consistent error messages and indicating the appropriate
exit code.

The main entry point is the handle_exception call that will detect the type of
error and handle it accordingly.

Individual handling methods are also available in the event an extension needs
to catch and display an exception using the consistent formatting but still
react to it in the extension itself.
"""

import os
from gettext import gettext as _
from pertinax.logutil import getLogger

from katello.client.server import ServerRequestError

# -- constants ----------------------------------------------------------------

CODE_BAD_REQUEST = os.EX_DATAERR
CODE_NOT_FOUND = os.EX_DATAERR
CODE_CONFLICT = os.EX_DATAERR
CODE_PULP_SERVER_EXCEPTION = os.EX_SOFTWARE
CODE_APACHE_SERVER_EXCEPTION = os.EX_SOFTWARE
CODE_CONNECTION_EXCEPTION = os.EX_IOERR
CODE_PERMISSIONS_EXCEPTION = os.EX_NOPERM
CODE_UNEXPECTED = os.EX_SOFTWARE
CODE_INVALID_CONFIG = os.EX_DATAERR
CODE_WRONG_HOST = os.EX_DATAERR
CODE_UNKNOWN_HOST = os.EX_CONFIG
CODE_SOCKET_ERROR = os.EX_CONFIG

_log = getLogger(__name__)

# -- classes ------------------------------------------------------------------

class ExceptionHandler:
    """
    Default implementation of the client-side exception middleware. Subclasses
    may override the individual handle_* methods to customize the error message
    displayed to the user, however care should be taken to return the
    appropriate exit code.
    """

    def __init__(self, prompt, config):
        """
        :param prompt: prompt instance used to display error messages
        :type  prompt: Prompt

        :param config: client configuration
        :type  config: ConfigParser
        """
        self.prompt = prompt
        self.config = config

    def handle_exception(self, e):
        """
        Analyzes the type of exception passed in and calls the appropriate
        method to handle it.

        @param e:
        @return:
        """

        # Determine which method to call based on exception type
        mappings = (
            (ServerRequestError,      self.handle_server_error),
            # (BadRequestException,   self.handle_bad_request),
            # (NotFoundException,     self.handle_not_found),
            # (ConflictException,     self.handle_conflict),
            # (ConnectionException,   self.handle_connection_error),
            # (PermissionsException,  self.handle_permission),
            # (InvalidConfig,         self.handle_invalid_config),
            # (WrongHost,             self.handle_wrong_host),
            # (gaierror,              self.handle_unknown_host),
            # (socket_error,          self.handle_socket_error),
            # (ApacheServerException, self.handle_apache_error),
        )

        handle_func = self.handle_unexpected
        for exception_type, func in mappings:
            if isinstance(e, exception_type):
                handle_func = func
                break

        exit_code = handle_func(e)
        return exit_code

    def handle_unexpected(self, e):
        """
        Catch-all to handle any exception that wasn't explicitly handled by
        any of the other handle_* methods in this class.

        @return: appropriate exit code for this error
        """

        self._log_client_exception(e)

        msg = _('An unexpected error has occurred. More information '
                'can be found in the client log file %(l)s.')
        msg = msg % {'l' : self._log_filename()}

        #self.prompt.render_failure_message(msg)
        self.prompt.write(msg)
        raise
        return CODE_UNEXPECTED

    def handle_server_error(self, e):
        try:
            if "displayMessage" in e[1]:
                msg = e[1]["displayMessage"]
            elif e[0] == 401:
                msg = _("Invalid credentials or unable to authenticate")
            elif e[0] == 500:
                msg = _("Server is returning 500 - try later")
            elif "errors" in e[1]:
                msg = ", ".join(e[1]["errors"])
            elif "message" in e[1]:
                msg = e[1]["message"]
            else:
                msg = str(e[1])
        except IndexError:
            msg = e[1]
        except:  # pylint: disable=W0702
            msg = _("Unknown error: ") + str(e)

        self.prompt.write(msg)
        return e[0]

    def _log_server_exception(self, e):
        """
        Dumps all information from an exception that came from the server
        to the log.

        @type e: RequestException
        """
        template = """Exception occurred:
        href:      %(h)s
        method:    %(m)s
        status:    %(s)s
        error:     %(e)s
        traceback: %(t)s
        data:      %(d)s
        """

        data = {'h' : e.href,
                'm' : e.http_request_method,
                's' : e.http_status,
                'e' : e.error_message,
                't' : e.traceback,
                'd' : e.extra_data}

        _log.error(template % data)

    def _log_client_exception(self, e):
        """
        Dumps all information from a client-side originated exception to the log.

        @type e: Exception
        """
        _log.exception('Client-side exception occurred')

    def _log_filename(self):
        """
        Syntactic sugar for reading the log filename out of the config.

        @return: full path to the log file
        """
        #return self.config['logging']['filename']
        return "/some/log/file.log"
