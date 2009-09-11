# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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

import time

def obt_date(self, date, items=3, sep='-'):
    if items==1:
        res = time.strftime('%Y', time.strptime(date, '%Y-%m-%d %H:%M:%S'))
    elif items==2:
        res = time.strftime('%m'+sep+'%Y', time.strptime(date, '%Y-%m-%d %H:%M:%S'))
    else:
        res = time.strftime('%d'+sep+'%m'+sep+'%Y', time.strptime(date, '%Y-%m-%d %H:%M:%S'))
    return res

def obt_time(self, date, items=3, sep=':'):
    if items==1:
        res = time.strftime('%H', time.strptime(date, '%Y-%m-%d %H:%M:%S'))
    elif items==2:
        res = time.strftime('%H'+sep+'%M', time.strptime(date, '%Y-%m-%d %H:%M:%S'))
    else:
        res = time.strftime('%H'+sep+'%M'+sep+'%S', time.strptime(date, '%Y-%m-%d %H:%M:%S'))
    return res

