# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2011-2013 Therp BV (<http://therp.nl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import warnings

_short_name = __name__.split(".")[-1]
warnings.warn(
    "Importing %(full_name)s is deprecated. "
    "Use from openupgradelib import %(short_name)s" % {
        'full_name': __name__,
        'short_name': _short_name,
    }, DeprecationWarning, stacklevel=2)

_new_name = "openupgradelib.%s" % _short_name

_modules = __import__(_new_name, globals(), locals(), ['*'])
for _i in dir(_modules):
    locals()[_i] = getattr(_modules, _i)
