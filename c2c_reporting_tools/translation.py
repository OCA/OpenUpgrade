# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) Camptocamp SA
# Author: Arnaud Wüst
#
#
#    This file is part of the c2c_report_tools module.
#
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################



###
#
# Provide a replacement method for the _() call for 4.2 versions
#
###


import inspect
import tools

class GettextAlias_42(object):
    """provide a replacement method _() to use "code" translations 
       _() works only where 'cr' and 'context['lang']' are available in local context. 
       in short: use this method only in code run by users' actions, not in code run when the server start (because there is no lang defined at this moment...)
       
       in PythonReport objects, use self._() instead when cr and context are not available in local context
    """
    
    def __call__(self, source):
        frame = inspect.stack()[1][0]
        cr = frame.f_locals.get('cr')
        lang = frame.f_locals.get('context', {}).get('lang', False)
        filename= frame.f_code.co_filename
        if not (lang and cr):
            result = source
        else:
            result = tools.translate(cr, None, filename, 'code', lang, source) or source
        return result
        


_ = GettextAlias_42()
