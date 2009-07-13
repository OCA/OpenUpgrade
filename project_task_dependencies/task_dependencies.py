# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) P. Christeas, 2009
# all rights reserved
# created 2008-07-05
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
from osv import fields,osv
import pooler


class task(osv.osv):
    _inherit = "project.task"
    

    def _check_recursion(self, cr, uid, ids):
                level = 100
                while len(ids):
                        cr.execute('select distinct next_task_id from project_task_rel where prior_task_id in ('+','.join(map(str,ids))+')')
                        ids = filter(None, map(lambda x:x[0], cr.fetchall()))
                        if not level:
                                return False
                        level -= 1
                return True
    #_constraints = [
        #(_check_recursion, 'Error ! You can not create recursive tasks.', ['next_task_id']),       
    #]

    _columns = {
      'prior_task_ids': fields.many2many('project.task', 'project_task_rel', 'next_task_id', 'prior_task_id', 'Leading Tasks'),
    }

task()