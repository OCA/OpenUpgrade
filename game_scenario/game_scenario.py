# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2008 Tiny SPRL (http://tiny.be) All Rights Reserved.
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
###############################################################################
from osv import fields, osv
import pooler
import time
from mx import DateTime
import datetime

import netsvc
from service import security
from service import web_services

class game_scenario_step(osv.osv):
    _name="game.scenario.step"
    _columns = {
        'name':fields.char('Name',size=64, required=True),
        'description' : fields.text('Description'),
        'menu_id' : fields.many2one('ir.ui.menu', 'Menu', required=True),
        'accepted_users' : fields.one2many('res.users', 'user_id', 'User'),
        'tip' : fields.text('Tip'),
        'error' : fields.text('Error'),
        'pre_process_object' : fields.char('Preprocess Object', size=64),
        'pre_process_method' : fields.char('Preprocess Method', size=64),
        'pre_process_args' : fields.text('Preprocess Args'),
        'post_process_object' : fields.char('Postprocess Object', size=64),
        'post_process_method' : fields.char('Postprocess Method', size=64),
        'post_process_args' : fields.text('Postprocess Args')
        }
game_scenario_step()

class game_scenario(osv.osv):
    _name="game.scenario"
    _columns = {
        'name':fields.char('Name',size=64, required=True),
        'note':fields.text('Note'),
        'step_ids':fields.many2many('game.scenario.step', 'game_scenario_step_rel', 'scenario_id', 'scenario_step_id', 'Steps'),
        'state' : fields.selection([('draft','Draft'), ('running','Running'), ('done','Done'), ('cancel','Cancel')], 'State')
    }
    _defaults = {
        'state' : lambda *a : 'running',
        }
game_scenario()

class users(osv.osv):
    _inherit="res.users"
    _columns={
        'user_id' : fields.many2one('game.scenario.step', 'accepted_users',)
        }
users()

class scenario_objects_proxy(web_services.objects_proxy):

    def execute(self, db, uid, passwd, object, method, *args):
        security.check(db, uid, passwd)
        service = netsvc.LocalService("object_proxy")
        cr = pooler.get_db_only(db).cursor()
        pool = pooler.get_pool(cr.dbname)
        step_obj=pool.get('game.scenario.step')
        cr.execute("select scenario_step_id from game_scenario_step_rel rel left join game_scenario s on s.id=rel.scenario_id where s.state='running' ")
        step_ids=map(lambda x:x[0],cr.fetchall())

        for step in step_obj.browse(cr,uid,step_ids):
            if not step.state=='running':
                continue
            pre_process_object = step.pre_process_object
            pre_process_method = step.pre_process_method
            try:
                res = service.execute(db, uid, pre_process_object, pre_process_method, *args)

            except AttributeError:
                step_obj.write(cr,uid,step_ids,{'error': AttributeError.__dict__['__doc__']})
                cr.commit()

            if not res:
                res = service.execute(db, uid, object, method, *args)
            else:
                post_process_object = step.post_process_object
                post_process_method = step.post_process_method
                res = service.execute(db, uid, object, method, *args)
                res = service.execute(db, uid, post_process_object, post_process_method, *args)

        return res

scenario_objects_proxy()


