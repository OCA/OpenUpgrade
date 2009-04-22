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

from osv import fields
from osv import osv
import time
import datetime
import random

class dm_simulator(osv.osv):
    _name = "dm.simulator"
    _description = "DM Campaign Simulator"
    _columns = {
        'name' : fields.char('Name',size=64,required=True),
        'campaign_id' : fields.many2one('dm.campaign','Campaign',required=True),
        'date_start' : fields.datetime('Date Start', readonly=False),
        'date_stop' : fields.datetime('Date Stop', readonly=False),
        'duration' : fields.integer('Duration'),
        'duration_unit' : fields.selection([('minutes', 'Minutes'),('hours','Hours'),('days','Days'),('months','Months')], 'Time Unit'),
        'cust_qty' : fields.integer('Customers', readonly=True),
        'action_qty' : fields.integer('Actions', readonly=True),
        'section_qty' : fields.integer('Section', readonly=True),
        'sale_rate' : fields.float('Sale Rate (%)', digits=(16,2), readonly=True),
        'type': fields.selection([('purchase','Purchase Simualtion')],'Type',required=True),
        'note' : fields.text('Description'),
        'logs' : fields.text('Logs'),
        'state': fields.selection([('pending','Pending'),('running','Running'),('done','Done')],'Status', readonly=True),
    }

    def onchange_campaign(self, cr, uid, ids, campaign_id, type):
        value = {}
        if campaign_id:
            camp = self.pool.get('dm.campaign').browse(cr, uid, campaign_id)

            """ Count the quantity customers and actions to simulate"""
            for propo in camp.proposition_ids:
                for seg in propo.segment_ids:
                    if seg.type_src == "internal" and seg.customers_file_id:
                        cust_ids = [cust_id.id for cust_id in seg.customers_file_id.address_ids]
            print "DM SIM - Customers :", cust_ids
            print "DM SIM - Customers qty :", len(cust_ids)
            cust_qty = len(cust_ids)
            value['cust_qty'] = cust_qty

            if type == "purchase":
                """ Count the number of purchase transitions"""
                step_ids = self.pool.get('dm.offer.step').search(cr, uid, [('offer_id','=',camp.offer_id.id)])
                trigger_id = self.pool.get('dm.offer.step.transition.trigger').search(cr, uid, [('code','=','purchase')])
                tr_ids = self.pool.get('dm.offer.step.transition').search(cr, uid, [('step_to_id','in',step_ids),('condition_id','=',trigger_id[0])])
                section_qty = len(tr_ids)
                value['section_qty'] = section_qty 
                print "DM SIM - tr_ids :",tr_ids
                print "DM SIM - len(tr_ids) :",len(tr_ids)
                sect_act_qty = cust_qty
                sect_act = []
                sect = 0
                while (sect < section_qty):
                    sect_act.append(sect_act_qty)
                    sect_act_qty = sect_act_qty/2
                    sect = sect+1
                value['action_qty'] = sum(sect_act)

        return {'value':value}


    def simulation_start(self, cr, uid, ids, *args):
        sim = self.browse(cr, uid, ids)[0]
        now = datetime.datetime.now()
        self.write(cr, uid, ids, {'date_start':now.strftime('%Y-%m-%d  %H:%M:%S')})
        kwargs = {(sim.duration_unit):sim.duration}
        duration = datetime.timedelta(**kwargs)
        date_stop = now + duration
        self.write(cr, uid, ids, {'date_stop':date_stop.strftime('%Y-%m-%d  %H:%M:%S')})

        """ compute duration per section """
        sect_dur = duration // 4
        print "DM SIM - sect_dur :",sect_dur
        print "DM SIM - type sect_dur :",type(sect_dur)

        if sim.type == "purchase":
            sect_act_qty = sim.cust_qty
            sect_act = []
            sect = 0
            while (sect < sim.section_qty):
                """ Compute time range """
                from_time = datetime.datetime.strptime(sim.date_start, '%Y-%m-%d  %H:%M:%S') + (sect_dur * sect)
                print "from_time :",from_time
                to_time = datetime.datetime.strptime(sim.date_start, '%Y-%m-%d  %H:%M:%S') + (sect_dur * (sect+1))
                print "DM SIM - to_time :",to_time

                sect_act.append([sect_act_qty,from_time,to_time])
                sect_act_qty = sect_act_qty/2
                sect = sect+1

            print "DM SIM - Section actions :",sect_act
            trigger_type_id = self.pool.get('dm.offer.step.transition.trigger').search(cr, uid, [('code','=','purchase')])[0]

            for propo in sim.campaign_id.proposition_ids:
                for seg in propo.segment_ids:
                    if seg.type_src == "internal" and seg.customers_file_id:
                            cust_ids = [cust_id.id for cust_id in  seg.customers_file_id.address_ids]
            print "DM SIM - Customers :", cust_ids

            for s in sect_act:
                """ Get offer steps """
                step_ids = self.pool.get('dm.offer.step').search(cr, uid, [('offer_id','=',sim.campaign_id.offer_id.id)])
                trigger_id = self.pool.get('dm.offer.step.transition.trigger').search(cr, uid, [('code','=','purchase')])
                tr_ids = self.pool.get('dm.offer.step.transition').search(cr, uid, [('step_to_id','in',step_ids),('condition_id','=',trigger_id[0])])
                print "DM SIM - tr_ids :",tr_ids
                trs = self.pool.get('dm.offer.step.transition').browse(cr, uid, tr_ids)
                print "DM SIM - trs :",trs
                steps = [tr.step_from_id.id for tr in trs]
                print "steps :",steps
                steps_sorted = sorted(steps)
                print "DM SIM - steps_sorted :",steps_sorted
                for step in steps_sorted:
                    print "Offer step :",step
                    """ Compute action times range"""
                    from_ts = time.mktime(s[1].timetuple())
                    to_ts = time.mktime(s[2].timetuple())

                    """ Generate Actions """
                    for cust in cust_ids[0:s[0]]:
                        action_time = datetime.datetime.fromtimestamp(random.randint(int(from_ts),int(to_ts))).strftime('%Y-%m-%d  %H:%M:%S')
                        print "DM SIM - action_time :",action_time
                        self.pool.get('dm.simulator.action').create(cr, uid, {'simulator_id':sim.id,'trigger_type_id':trigger_type_id,
                            'step_id':step, 'segment_id':cust[1], 'address_id':cust[0],'section':sect_act.index(s),
                            'action_time':action_time})
                    print "DM SIM - Customers :", cust_ids[0:s[0]]

        self.write(cr, uid, ids, {'state':'running'})

        return True

    def simulation_stop(self, cr, uid, ids, *args):

        """ Remove simulation actions """
        sim = self.browse(cr, uid ,ids)[0]
        sim_act_ids = self.pool.get('dm.simulator.action').search(cr, uid, [('simulator_id','=',sim.id),('state','=','pending')])
        self.pool.get('dm.simulator.action').unlink(cr, uid, sim_act_ids)
        self.write(cr, uid, ids, {'state':'done'})

        return True

    def action_do(self, cr, uid, context={}):

        sim_ids = self.search(cr, uid, [('state','=','running')])
        for sim in self.browse(cr, uid, sim_ids):
            print "DM SIM - Doing action for :",sim.name
            logs = []
#            logs.append(sim.logs.split('\n'))
#            if datetime.datetime.strptime(sim.date_stop, '%Y-%m-%d  %H:%M:%S') > datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d  %H:%M:%S'):
#                print "Stop Date :",datetime.datetime.strptime(sim.date_stop, '%Y-%m-%d  %H:%M:%S')
#                print "Now :",datetime.datetime.now()
#                print "Now :",datetime.datetime.now()
#                self.simulation_stop(cr, uid, [sim.id], None)
#                break

            sim_act_ids = self.pool.get('dm.simulator.action').search(cr, uid, [('simulator_id','=',sim.id),('state','=','pending'),
                ('action_time','<=',time.strftime('%Y-%m-%d %H:%M:%S'))])
            print "DM SIM - sim_act_ids :",sim_act_ids
            sim_act = self.pool.get('dm.simulator.action').browse(cr, uid, sim_act_ids)
            for act in sim_act:
                event_ids = self.pool.get('dm.event').create(cr, uid, {'segment_id':act.segment_id.id,'step_id':act.step_id.id,'source':'address_id',
                    'address_id':act.address_id.id,'trigger_type_id':act.trigger_type_id.id})
                self.pool.get('dm.simulator.action').write(cr, uid, act.id, {'state':'done'})
                logs.append('%s - %s purchased at step : %s'% (act.action_time, act.address_id.name,act.step_id.name))

            self.write(cr, uid, sim.id, {'logs':"\n".join(logs)})


        return True

    _defaults = {
        'type' : lambda *a: "purchase",
        'duration' : lambda *a: 1,
        'duration_unit' : lambda *a: "hours",
        'state' : lambda *a: "pending",
    }

dm_simulator()

class dm_simulator_action(osv.osv):
    _name = "dm.simulator.action"
    _description = "DM Campaign Simulator Action"
    _columns = {
        'simulator_id' : fields.many2one('dm.simulator','Simulator',required=True),
        'trigger_type_id' : fields.many2one('dm.offer.step.transition.trigger','Trigger Condition',required=True),
        'step_id' : fields.many2one('dm.offer.step','Offer Step', required=True),
        'segment_id' : fields.many2one('dm.campaign.proposition.segment','Segment', required=True),
        'source' : fields.char('source',size=64),
        'address_id' : fields.many2one('res.partner.address','Customer', required=True),
        'section' : fields.integer('Section'),
        'action_time' : fields.datetime('Action Time'),
        'state' : fields.selection([('pending','Pending'),('done','Done'),('error','Error')],'State',readonly=True),
        'error_msg' : fields.text('Error Message'),
    }

    _defaults = {
        'state' : lambda *a: "pending",
    }
dm_simulator_action()
