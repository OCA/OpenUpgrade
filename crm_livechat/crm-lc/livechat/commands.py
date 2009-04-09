# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
"""This module contains functions called from console script entry points."""

import os
import sys

from os.path import dirname, exists, join

import pkg_resources
pkg_resources.require("TurboGears")

import turbogears
import cherrypy

cherrypy.lowercase_api = True

class ConfigurationError(Exception):
    pass

def start():
    """Start the CherryPy application server."""

    setupdir = dirname(dirname(__file__))
    curdir = os.getcwd()

    # First look on the command line for a desired config file,
    # if it's not on the command line, then look for 'setup.py'
    # in the current directory. If there, load configuration
    # from a file called 'dev.cfg'. If it's not there, the project
    # is probably installed and we'll look first for a file called
    # 'prod.cfg' in the current directory and then for a default
    # config file called 'default.cfg' packaged in the egg.
    if len(sys.argv) > 1:
        configfile = sys.argv[1]
    elif exists(join(setupdir, "setup.py")):
        configfile = join(setupdir, "dev.cfg")
    elif exists(join(curdir, "prod.cfg")):
        configfile = join(curdir, "prod.cfg")
    else:
        try:
            configfile = pkg_resources.resource_filename(
              pkg_resources.Requirement.parse("crn-lc"),
                "config/default.cfg")
        except pkg_resources.DistributionNotFound:
            raise ConfigurationError("Could not find default configuration.")

    turbogears.update_config(configfile=configfile,
        modulename="livechat.config")

    from livechat.controllers import Root

    turbogears.start_server(Root())
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

