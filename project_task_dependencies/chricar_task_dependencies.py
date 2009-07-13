##############################################
#
# ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
# created 2008-07-05
#
###############################################
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
    _constraints = [
        (_check_recursion, 'Error ! You can not create recursive tasks.', ['next_task_id']),       
    ]

    _columns = {
      'next_task_ids' : fields.many2many('project.task', 'project_task_rel', 'prior_task_id', 'next_task_id', 'Dependent Tasks '),
      'prior_task_ids': fields.many2many('project.task', 'project_task_rel', 'next_task_id', 'prior_task_id', 'Leading Tasks'),
    }


task()