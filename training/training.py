# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import osv, fields
import netsvc
import time

class training_course_category(osv.osv):
    _name = 'training.course_category'
    _description = 'The category of a course'
    _inherits = {
        'account.analytic.account' : 'analytic_account_id',
    }

    def _get_child_ids(self, cr, uid, ids, name, args, context):
        res = {}
        for object in self.browse(cr, uid, ids):
            child_ids = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', object.analytic_account_id.id)])
            res[object.id] = self.search(cr, uid, [('analytic_account_id', 'in', child_ids)])

        return res

    _columns = {
        'analytic_account_id' : fields.many2one('account.analytic.account', 'Analytic Account'),
        'description' : fields.text('Description'),
        'child_ids' : fields.function(_get_child_ids, method=True, type='one2many', relation="training.course", string='Children'),
    }

training_course_category()

class training_course_type(osv.osv):
    _name = 'training.course_type'
    _description = 'The type of a course'

    _columns = {
        'name' : fields.char('Name', size=32, required=True, select=1),
        'objective' : fields.text('Objective',
                                  help="Allows to the user to write the objectives of the course type"),
        'description' : fields.text('Description',
                                    help="Allows to the user to write the description of the course type"),
        'min_limit' : fields.integer('Minimum Threshold',
                                     required=True,
                                     select=2,
                                     help="The minimum threshold is the minimum for this type of course"),
        'max_limit' : fields.integer('Maximum Threshold',
                                     required=True,
                                     select=2,
                                     help="The maximum threshold is the maximum for this type of course"),
    }

training_course_type()

class training_course(osv.osv):
    _name = 'training.course'
training_course()

class training_course_purchase_line(osv.osv):
    _name = 'training.course.purchase_line'
    _rec_name = 'course_id'
    _columns = {
        'course_id' : fields.many2one('training.course', 'course', required=True,
                                      help="The course attached to this purchase line"),
        'product_id' : fields.many2one('product.product', 'Product', required=True,
                                       help="The product for this purchase line"),
        'product_qty' : fields.integer('Quantity', required=True,
                                       help="The quantity of this product"),
        'product_uom_id' : fields.many2one('product.uom', 'Product UoM', required=True,
                                           help="The unit of mesure for this product"),
    }
training_course_purchase_line()

class training_offer(osv.osv):
    _name = 'training.offer'
training_offer()

class training_course(osv.osv):
    _name = 'training.course'
    _description = 'Course'
    _inherits = {
        'account.analytic.account' : 'analytic_account_id'
    }

    def _total_duration_compute(self,cr,uid,ids,name,args,context):
        return dict.fromkeys(ids, 0.0)

    def _get_child_ids(self, cr, uid, ids, name, args, context):
        res = {}
        for object in self.browse(cr, uid, ids):
            child_ids = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', object.analytic_account_id.id)])
            res[object.id] = self.search(cr, uid, [('analytic_account_id', 'in', child_ids)])
        return res

    def _set_child_ids(self, cr, uid, obj_id, name, value, args, context=None):
        #import tools
        #tools.debug(cr)
        #tools.debug(uid)
        #tools.debug(obj_id)
        #tools.debug(name)
        #tools.debug(value)
        #tools.debug(args)
        #tools.debug(context)
        return True

    _columns = {
        'duration' : fields.float('Duration',
                                 required=True,
                                 help="The duration for a standalone course"),

        'children' : fields.function(_get_child_ids,
                                     method=True,
                                     type='one2many',
                                     relation="training.course",
                                     fnct_inv=_set_child_ids,
                                     string='Children',
                                     help="A course can be completed with some subcourses"),

        'total_duration' : fields.function(_total_duration_compute,
                                           string='Total Duration',
                                           readonly=True,
                                           store=True,
                                           method=True,
                                           type="float",
                                           help="The total dureation is computed if there is any subcourse"),

        'sequence' : fields.integer('Sequence'),

        'target_public' : fields.char('Target Public',
                                      size=256,
                                      help="Allows to the participants to select a course whose can participate"),

        'reference_id' : fields.many2one('training.course',
                                         'Master Course',
                                         help="The master course is necessary if the user wants to link certain courses together to easy the managment"),

        'analytic_account_id' : fields.many2one('account.analytic.account', 'Account'),

        'course_type_id' : fields.many2one('training.course_type', 'Type',
                                           required=True
                                          ),

        'lecturer_ids' : fields.many2many('res.partner.contact',
                                          'training_course_partner_rel',
                                          'course_id',
                                          'partner_id',
                                          'Lecturers',
                                          help="The lecturers who give the course",
                                         ),

        'internal_note' : fields.text('Note'),

        'lang_id' : fields.many2one('res.lang', 'Language', required=True,
                                   help="The language of the course"),

        'offer_ids' : fields.many2many('training.offer',
                                       'training_course_offer_rel',
                                       'course_id',
                                       'offer_id',
                                       'Offers',
                                       help="The offers containing the course"
                                      ),

        'state_course' : fields.selection([('draft', 'Draft'),
                                           ('pending', 'Pending'),
                                           ('inprogress', 'In Progress'),
                                           ('deprecated', 'Deprecated'),
                                           ('validated', 'Validated'),
                                          ],
                                          'State',
                                          required=True,
                                          readonly=True,
                                          select=1,
                                         ),

        'purchase_line_ids' : fields.one2many('training.course.purchase_line', 'course_id',
                                              'Supplier Commands'),
    }

    _defaults = {
        'state_course' : lambda *a: 'draft',
    }

training_course()

class training_offer(osv.osv):
    _name = 'training.offer'
    _description = 'Offer'
    _columns = {
        'name' : fields.char('Name', size=64, required=True, select=1),
        'product_id' : fields.many2one('product.product', 'Product'),
        'course_ids' : fields.many2many('training.course',
                                        'training_course_offer_rel',
                                        'offer_id',
                                        'course_id',
                                        'Courses',
                                        domain="[('state_course', '=', 'validated')]"
                                       ),
        'objective' : fields.text('Objective',
                                  help="Allows to write the objectives of the course",
                                 ),
        'description' : fields.text('Description',
                                    help="Allows to write the description of the course"),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('validated', 'Validated'),
                                    ('deprecated', 'Deprecated')
                                   ],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
    }

training_offer()

class training_catalog(osv.osv):
    _name = 'training.catalog'
    _description = 'Catalog'
    _rec_name = 'year'
    _columns = {
        'year' : fields.integer('Year',
                                size=4,
                                required=True,
                                select=1,
                                help="The year when the catalog has been published",
                               ),
        'session_ids' : fields.one2many('training.session', 'catalog_id',
                                        'Sessions',
                                        help="The sessions in the catalog"),
        'note' : fields.text('Note',
                             help="Allows to write a note for the catalog"),
        'state' : fields.selection([('draft','Draft'),
                                    ('inprogress', 'In Progress'),
                                    ('done','Done')],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1),
    }

    _defaults = {
        'year' : lambda *a: int(time.strftime('%Y'))+1,
        'state' : lambda *a: 'draft',
    }

training_catalog()

class training_event(osv.osv):
    _name = 'training.event'
training_event()

class training_session(osv.osv):
    _name = 'training.session'
    _description = 'Session'
    _columns = {
        'name' : fields.char('Name',
                             size=64,
                             required=True,
                             select=1,
                             help="The session's name"),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('open_pending', 'Open and Pending'),
                                    ('inprogress', 'In Progress'),
                                    ('validated', 'Validated'),
                                    ('closed', 'Closed'),
                                    ('cancelled', 'Cancelled')],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1
                                  ),
        'offer_id' : fields.many2one('training.offer',
                                     'Offer',
                                     select=1,
                                     required=True,
                                     help="Allows to select a validated offer for the session",
                                    ),
        'catalog_id' : fields.many2one('training.catalog', 'Catalog',
                                       select=1,
                                       help="Allows to select a published catalog"
                                      ),
        'event_ids' : fields.many2many('training.event',
                                       'training_session_event_rel',
                                       'session_id',
                                       'event_id',
                                       'Events',
                                       ondelete='cascade',
                                       help="List of the events in the session"),
        'date' : fields.datetime('Date',
                                 required=True,
                                 help="The date of the planned session"
                                ),

        'purchase_line_ids' : fields.one2many('training.session.purchase_line', 'session_id', 
                                              'Supplier Commands'),
    }

    def _find_catalog_id(self, cr, uid, context=None):
        new_year = int(time.strftime('%Y')) + 1
        catalog_proxy = self.pool.get('training.catalog')
        catalog_ids = catalog_proxy.search(cr,uid,[('year', '=', new_year)],context=context)
        if catalog_ids:
            return catalog_ids[0]
        else:
            return None

    _defaults = {
        'catalog_id' : _find_catalog_id,
        'state' : lambda *a: 'draft',
    }

    def action_validate(self, cr, uid, ids, context=None):
        session = self.browse(cr, uid, ids, context=context)[0]
        event_ids = []

        for course in session.offer_id.course_ids:
            seance_proxy = self.pool.get('training.seance')
            seance_id = seance_proxy.create(cr, uid, {
                'name' : 'Seance - %s' % (session.name,),
                'course_id' : course.id,
            })
            event_id = seance_proxy.read(cr,
                                         uid,
                                         [seance_id],
                                         ['event_id'],
                                         context=context)[0]['event_id'][0]
            event_ids.append(event_id)

        values = {
            'state':'validated'
        }

        if event_ids:
            values['event_ids'] = [(6, 0, event_ids)]

        return self.write(cr, uid, ids, values, context=context)

training_session()

class training_session_purchase_line(osv.osv):
    _name = 'training.session.purchase_line'

    _rec_name = 'session_id'

    _columns = {
        'session_id' : fields.many2one('training.session', 'Session', required=True),
        'product_id' : fields.many2one('product.product', 'Product', required=True),
        'product_qty' : fields.integer('Quantity', required=True),
        'product_uom_id' : fields.many2one('product.uom', 'Product UoM', required=True),
    }

training_session_purchase_line()

class training_mass_subscription_wizard(osv.osv_memory):
    _name = 'wizard.training.mass.subscription'
    _description = 'Mass Subscription Wizard'

    def action_cancel(self, cr, uid, ids, context = None):
        return { 'type' : 'ir.actions.act_window_close' }

    def action_apply(self, cr, uid, ids, context = None):
        # Creation des inscriptions dans l'objet training.subscription
        this = self.browse(cr, uid, ids)[0]

        subscription_proxy = self.pool.get('training.subscription')
        for partner in this.partner_ids:
            for session in this.session_ids:
                vals = {
                    'partner_id' : partner.id,
                    'session_id' : session_id,
                }
                subscription_id = subscription_proxy.create(cr, uid, vals, context = context )
        return { 'type' : 'ir.actions.act_window_close' }

    _columns = {
        'partner_ids' : fields.many2many('res.partner.contact',
                                         'tmi_partner_rel',
                                         'wiz_id',
                                         'partner_id',
                                         'Partners',
                                         required=True),
        'session_ids' : fields.many2many('training.session',
                                         'tmi_session_rel',
                                         'wiz_id',
                                         'session_id',
                                         'Sessions',
                                         required=True),
    }

training_mass_subscription_wizard()

class training_location(osv.osv):
    _name = 'training.location'
    _description = 'Location'

    _columns = {
        'name' : fields.char('Name', size=32, select=True, required=True),
        'address_id' : fields.many2one('res.partner.address', 'Address', required=True),
    }

training_location()

class training_group(osv.osv):
    _name = 'training.group'
    _description = 'Group'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
    }
training_group()

class training_subscription(osv.osv):
    _name = 'training.subscription'
training_subscription()

class training_participation(osv.osv):
    _name = 'training.participation'
    _description = 'Participation'
    _columns = {
        'event_id' : fields.many2one('training.event', 'Event' ),
        'subscription_id' : fields.many2one('training.subscription', 'Subscription', select=True, required=True),
    }

training_participation()


class training_event(osv.osv):
    _name = 'training.event'
    _description = 'Event'

    def _check_date(self,cr,uid,ids,context=None):
        return self.browse(cr, uid, ids)[0].date > time.strftime('%Y-%m-%d')

    def _support_ok_get( self, cr, uid, ids, name, args, context ):
        return {}.fromkeys(ids, True)

    _columns = {
        'name' : fields.char('Name', size=64, select=1, required=True),
        'session_ids' : fields.many2many('training.session',
                                         'training_session_event_rel',
                                         'event_id',
                                         'session_id',
                                         'Sessions',
                                         ondelete='cascade'),
        # Attention, la date doit etre obligatoire
        'date' : fields.datetime('Date', required=False, select=1),
        'duration' : fields.time('Duration', required=False, select=1),
        'location_id' : fields.many2one('training.location', 'Location', select=1),
        'participant_ids' : fields.many2many('training.subscription',
                                             'training_participation',
                                             'event_id',
                                             'subscription_id',
                                             'Participants',
                                             domain="[('group_id', '=', group_id)]" ),
        'group_id' : fields.many2one('training.group', 'Group'),
        'support_ok' : fields.function(_support_ok_get,
                                       method=True,
                                       type="boolean",
                                       string="Support OK",
                                       readonly=True),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('open_pending', 'Open and Pending'),
                                    ('validate', 'Validate'),
                                    ('inprogress', 'In Progress'),
                                    ('closed', 'Closed'),
                                    ('cancelled', 'Cancelled')],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1
                                  ),
    }

    _constraints = [
        ( _check_date, "Errorr, Can you check your start date", ['date']),
    ]

    _defaults = {
        'state' : lambda *a: 'draft',
        'date' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

training_event()

class training_seance(osv.osv):
    _name = 'training.seance'
    _description = 'Seance'
    _inherits = { 'training.event' : 'event_id' }

    _columns = {
        'partner_ids' : fields.many2many('res.partner', 'training_seance_partner_rel', 'seance_id', 'partner_id', 'StakeHolders'),
        'event_id' : fields.many2one('training.event', 'Event'),
        'course_id' : fields.many2one('training.course', 'Course', required=True),
        #'copies' : fields.integer('Copies'),
        #'printed' : fields.boolean('Printed'),
        'reserved' : fields.boolean('Reserved'),
        'layout' : fields.char('Layout', size=32),
        'place' : fields.char('Place', size=32),
        'room' : fields.char('Room', size=32),
        #'limit' : fields.integer('Limit'), 
        'purchase_line_ids' : fields.one2many('training.seance.purchase_line', 'seance_id', 'Supplier Commands'),
    }

    def action_validate(self, cr, uid, ids, context=None):
        if not ids:
            return False

        seance = self.pool.get('training.seance').browse(cr, uid, [vals['seance_id']], context=context)[0]

        location_id = self.pool.get('stock.location').search(cr, uid, [('name', '=', 'Physical Locations')], context=context)[0]

        for product in seance.purchase_line_ids:
            # We create a new procurement for this line
            procurement_id = self.pool.get('mrp.procurement').create(cr, uid, {
                'name': "Seance %s - %s" % (seance.name, seance.date),
                'date_planned' : seance.date,
                'product_id' : product.product_id.id,
                'product_qty' : product.product_qty,
                'product_uom' : product.product_uom_id.id,
                'location_id' : location_id,
            })

            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'mrp.procurement', procurement_id, 'button_confirm', cr)

        return self.write(cr, uid, ids, {'state':'validated'}, context=context)

training_seance()

class training_seance_purchase_line(osv.osv):
    _name = 'training.seance.purchase_line'
    _rec_name = 'product_id'

    _columns = {
        'seance_id' : fields.many2one('training.seance', 'Seance', required=True),
        'product_id' : fields.many2one('product.product', 'Product', required=True),
        'product_qty' : fields.integer('Quantity', required=True),
        'product_uom_id' : fields.many2one('product.uom', 'Product UoM', required=True),
        'procurement_id' : fields.many2one('mrp.procurement', readonly=True),
    }


training_seance_purchase_line()

class training_subscription(osv.osv):
    _name = 'training.subscription'
    _description = 'Subscription'
    _columns = {
        'name' : fields.char('Reference',
                             size=32,
                             required=True,
                             select=1,
                             readonly=True,
                             help='The unique identifier is generated by the system (customizable)'),
        'date' : fields.datetime('Date',
                                 required=True,
                                 select=True,
                                ),
        'session_id' : fields.many2one('training.session',
                                       'Session',
                                       select=1,
                                       required=True,
                                      ),
        'partner_id' : fields.many2one('res.partner',
                                       'Partner',
                                       select=1,
                                       required=True,
                                      ),
        'address_id' : fields.many2one('res.partner.address',
                                       'Invoice Address',
                                       select=1,
                                       required=True,
                                      ),
        'contact_id' : fields.many2one('res.partner.contact',
                                       'Contact',
                                       select=1,
                                       required=True,
                                      ),
        # Pour le group ID, discuter pour savoir si on doit utiliser le seuil pédagogique du groupe pour savoir si on crée un nouveau group ou non
        'invoice_id' : fields.many2one('account.invoice', 'Invoice'),
        'group_id' : fields.many2one('training.group', 'Group'),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('confirmed','Confirmed'),
                                    ('cancelled','Cancelled'),
                                    ('done', 'Done')
                                   ],
                                   'State',
                                   readonly=True,
                                   required=True,
                                   select=1),
        'price' : fields.float('Price', digits=(16,2), required=True),
        'paid' : fields.boolean('Paid'),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
        'paid' : lambda *a: False,
        'name' : lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'training.subscription'),
    }

    def on_change_partner(self, cr, uid, ids, partner_id):
        """
        This function returns the invoice address for a specific partner, but if it didn't find an
        address, it takes the first address from the system
        """
        proxy = self.pool.get('res.partner.address')
        ids = proxy.search(cr, uid, [('partner_id', '=', partner_id),('type', '=', 'invoice')])

        if not ids:
            ids = proxy.search(cr, uid, [('partner_id', '=', partner_id)])
            if not ids:
                return {'value':{}}

        return {'value' : {'address_id':ids[0]} }

training_subscription()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
