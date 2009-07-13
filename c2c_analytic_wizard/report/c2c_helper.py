##############################################################################
#
# Copyright (c) Camptocamp (http://www.camptocamp.com) All Rights Reserved.
#
# $Id$
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
from osv import osv

import time
import os.path
import tools
import re


class c2c_helper(osv.osv):
    """ a class that provide useful methods for addons developement """
    
    # format of the dates
    timeformat = " %d.%m.%y"

    @staticmethod
    def comma_me(amount):
        """ transform a number into a number with thousand separators """
        if  type(amount) is float :
            amount = str('%.2f'%amount)
        else :
            amount = str(amount)
        orig = amount
        new = re.sub("^(-?\d+)(\d{3})", "\g<1>'\g<2>", amount)
        if orig == new:
            return new
        else:
            return c2c_helper.comma_me(new)


        
    @staticmethod
    def format_date(date, timeformat=None):
        """transform an english formated date into a swiss formated date (the format define is define as a class constant c2c_helper.timeformat """
        if timeformat == None:
            timeformat = c2c_helper.timeformat
        if date:
            return time.strftime(timeformat, time.strptime(date, "%Y-%m-%d"))
        return None