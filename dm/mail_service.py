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

class dm_mail_service(osv.osv):
    _name = "dm.mail_service"
#    _inherits = {'ir.actions.server':'mail_action_id'}
    def _default_name(self, cr, uid, ids, name, args, context={}):
        res = {}
        for rec in self.browse(cr, uid, ids):
            res[rec.id] = (rec.partner_id and rec.partner_id.name or '') + ' for ' + (rec.media_id and rec.media_id.name or '')
        return res 

    _columns = {
        'name' : fields.function(_default_name, method=True, string='Name',store=True ,type='char' ,size=128),
        'partner_id' : fields.many2one('res.partner','Partner',domain=[('category_id','ilike','Mail Service')],context={'category':'Mail Service'}),
        'media_id' : fields.many2one('dm.media','Media'),
        'action_interval': fields.integer('Interval'),
        'unit_interval': fields.selection( [('minutes', 'Minutes'),
            ('hours', 'Hours'), ('work_days','Work Days'), ('days', 'Days'),\
            ('weeks', 'Weeks'), ('months', 'Months')], 'Interval Unit'),
        'default_for_media' : fields.boolean('Default Mail Service for Media'),
        'action_id' : fields.many2one('ir.actions.server','Server Action'),
    }

    def _check_unique_mail_service(self, cr, uid, ids, media_id, default_for_media):
        if default_for_media :
            res = self.search(cr, uid, [('media_id', '=', media_id), ('default_for_media', '=', True)])
            if res and (ids and (res in ids) or True) : 
                return {'value':{'default_for_media':False}}
#                raise osv.except_osv("Error!!","You cannot create more than one default mail service for same media")
        else :
            return True 

    def create(self, cr, uid, vals, context={}):
        new_mail_service = super(dm_mail_service, self).create(cr, uid, vals, context)
        mail_service = self.browse(cr, uid, new_mail_service)
        new_vals = {
                    'name'           : mail_service.name,
                    'interval_number': mail_service.action_interval,
                    'interval_type'  : mail_service.unit_interval,
                    'model'          : 'dm.mail_service',
                    'function'       : '_check_action'  }
        self.pool.get('ir.cron').create(cr, uid, new_vals)
        return new_mail_service

dm_mail_service()


class dm_campaign_mail_service(osv.osv):
    _name = "dm.campaign.mail_service"
    _rec_name = 'mail_service_id'
    _columns = {
        'mail_service_id' : fields.many2one('dm.mail_service','Mail Service'),
        'campaign_id' : fields.many2one('dm.campaign','Campaign'),
        'offer_step_id' : fields.many2one('dm.offer.step','Offer Step'),
    }
dm_campaign_mail_service()
