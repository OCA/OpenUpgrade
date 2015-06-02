# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 OpenUpgrade Community All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import orm, fields


class ModelTest3(orm.Model):
    _name = 'test_sql_contraint.model_3'

    _description = 'Model Test 3'

    _columns = {
        'model_1_id': fields.many2one(
            'test_sql_contraint.model_1',
            'Field 3 A',
        )
    }
