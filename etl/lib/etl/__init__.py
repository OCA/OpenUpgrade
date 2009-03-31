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
##############################################################################
"""
I{ETL} (Extract, transform, and load) is a module for python 2.5 or greater 
that implements ETL concepts for data import,export and also perform some operation 
beween import/export.  

This packages has different sub-packages to define ETL job process, 
ETL components (Input/Source, transform/process, control, Output/Destination),
ETL connectors, ETL transition.

ETL job means to define etl process which can run, stop, pause.

ETL components means to define components which used in etl job like 
- Input Component     : to get data from external sources
- Output Component    : to store data into external destination
- Transform Component : to perform a series of rules or functions to the extracted data 
from the source to derive the data for loading into the end target.

ETL connectors means to connect with external systems or server which are used by ETL Components

ETL transition means to define data flow with different transition channels between 
source etl components and destination etl components

ETL is written entirely in python and is
released under the GNU General Public License.

Website: U{http://www.openerp.com/}

@version: 1.0.0
@author: Tiny SPRL
@contact: support@tinyerp.com
@license: GNU General Public License
"""
import sys
if sys.version_info < (2, 2):
    raise RuntimeError('You need python 2.2 for this module.')


__author__ = "Tiny SPRL"
__date__ = "01 Aprl 2009"
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__license__ = "GNU General Public License"

from signal import signal
from statistic import statistic
from job import job
from transition import transition
from transformer import transformer

import logger
import component
import connector
import tools

# fix module names for epydoc
for c in locals().values():
    if issubclass(type(c), type) or type(c).__name__ == 'classobj':
        # classobj for exceptions :/
        c.__module__ = __name__
del c


__all__ = [ 'signal',
            'statistic',
            'job',
            'transition',
            'transformer',
            'logger',
            'component',
            'connector',
            'tools' ]


