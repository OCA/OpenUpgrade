# -*- encoding: utf-8 -*-
##############################################################################
#
#    ETL system- Extract Transfer Load system
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""
 To  provide internal logging system.

 Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
 GNU General Public License.

"""
import logging
import logging.handlers
import sys
import os

LOG_INFO = 'info'
LOG_WARNING = 'warn'
LOG_ERROR = 'error'


def init_logger():
    logger = logging.getLogger()
    # create a format for log messages and dates
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(name)s: %(message)s', '%a %b %d %Y %H:%M:%S')

    logf = '/tmp/etl_log.out'
    handler = logging.handlers.TimedRotatingFileHandler(logf, 'D', 1, 30)

    # tell the handler to use this format
    handler.setFormatter(formatter)
    # add the handler to the root logger
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class logger(object):

    def __getstate__(self):
        pass

    def __setstate__(self, state):
        pass

    def notifyChannel(self, name, level, msg):
        log = logging.getLogger(name)
        level_method = getattr(log, level)
        msg = unicode(msg)

        result = msg.strip().split('\n')
        if len(result) > 1:
            for idx, s in enumerate(result):
                level_method('[%02d]: %s' % (idx + 1, s,))
        elif result:
            level_method(result[0])

    def shutdown(self):
        logging.shutdown()

init_logger()

