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

    def _get_child_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids):
            child_ids = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', obj.analytic_account_id.id)])
            res[obj.id] = self.search(cr, uid, [('analytic_account_id', 'in', child_ids)])

        return res

    _columns = {
        'analytic_account_id' : fields.many2one('account.analytic.account', 'Analytic Account'),
        'description' : fields.text('Description', help="Description of the course category"),
        'child_ids' : fields.function(_get_child_ids, method=True, type='one2many',
                                      relation="training.course", string='Children'),
    }

training_course_category()

class training_course_type(osv.osv):
    _name = 'training.course_type'
    _description = 'The type of a course'

    _columns = {
        'name' : fields.char('Name', size=32, required=True, select=1, help="The course type's name"),
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

    def _check_limits(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        return obj.min_limit <= obj.max_limit

    _constraints = [
        (_check_limits,
         'The minimum limit is greater than the maximum limit',
         ['min_limit', 'max_limit']),
    ]

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

    def _total_duration_compute(self, cr, uid, ids, name, args, context=None):
        res = dict.fromkeys(ids, 0.0)

        for course in self.browse(cr, uid, ids, context=context):
            for child in course.children:
                res[course.id] = res[course.id] + child.duration

        return res

    def _has_support(self, cr, uid, ids, name, args, context=None):
        res = dict.fromkeys(ids, 0)
        cr.execute("SELECT res_id, count(1) FROM %s WHERE res_id in (%s) and res_model = '%s' GROUP BY res_id" % (
            self.pool.get('ir.attachment')._table,
            ','.join(map(str, ids)),
            self._name,)
        )
        for x in cr.fetchall():
            res[x[0]] = x[1]
        return res

    _columns = {
        'duration' : fields.float('Duration', required=True, help="The duration for a standalone course"),
        'p_id' : fields.many2one('training.course', 'Parent Course', help="The parent course", readonly=True),
        'children' : fields.one2many('training.course', 'p_id', string="Children",
                                     help="A course can be completed with some subcourses"),

        'total_duration' : fields.function(_total_duration_compute,
                                           string='Total Duration',
                                           readonly=True,
                                           store=True,
                                           method=True,
                                           type="float",
                                           help="The total duration is computed if there is any subcourse"),

        'sequence' : fields.integer('Sequence', help="The sequence can help the user to reorganize the order of the courses"),

        'target_public' : fields.char('Target Public',
                                      size=256,
                                      help="Allows to the participants to select a course whose can participate"),

        'reference_id' : fields.many2one('training.course',
                                         'Master Course',
                                         help="The master course is necessary if the user wants to link certain courses together to easy the managment"),

        'analytic_account_id' : fields.many2one('account.analytic.account', 'Account'),
        'course_type_id' : fields.many2one('training.course_type', 'Type', required=True),
        'lecturer_ids' : fields.many2many('res.partner.contact',
                                          'training_course_partner_rel',
                                          'course_id',
                                          'partner_id',
                                          'Lecturers',
                                          help="The lecturers who give the course",
                                         ),

        'internal_note' : fields.text('Note', 
                                      help="The user can write some internal note for this course"),

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
                                          help="The state of the course"
                                         ),

        'purchase_line_ids' : fields.one2many('training.course.purchase_line', 'course_id',
                                              'Supplier Commands',
                                              help="The purchase line helps to create a purchase order for the seance"),

        'preliminary_course_ids' : fields.many2many('training.course',
                                                    'training_course_pre_course_rel',
                                                    'course_id',
                                                    'prelim_course_id',
                                                    'Preliminary Courses'),

        'complementary_course_ids' : fields.many2many('training.course',
                                                      'training_course_cpl_course_rel',
                                                      'course_id',
                                                      'cpl_course_id',
                                                      'Complementary Courses'),
        'has_support' : fields.function(_has_support, method=True, type="boolean", string="Has Support"),
        'display_name' : fields.char('Display Name', size=38, help='Allows to show a short name for this course'),
    }

    _defaults = {
        'state_course' : lambda *a: 'draft',
        'duration' : lambda *a: 0.0,
    }

training_course()

class training_offer(osv.osv):
    _name = 'training.offer'
    _description = 'Offer'
    _columns = {
        'name' : fields.char('Name', size=64, required=True, select=1, help="The name's offer"),
        'product_id' : fields.many2one('product.product',
                                       'Product',
                                       #required=True,
                                       help="An offer can be a product for invoicing",
                                      ),
        'course_ids' : fields.many2many('training.course',
                                        'training_course_offer_rel',
                                        'offer_id',
                                        'course_id',
                                        'Courses',
                                        domain="[('state_course', '=', 'validated')]",
                                        help="An offer can contain some courses",
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
                                   select=1,
                                   help="The status of the course",
                                  ),
        'kind' : fields.selection([('standard', 'Standard'),
                                   ('intra', 'Intra')],
                                  'Kind',
                                  required=True,
                                 ),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),

        #'sale_price' : fields.float('Sale Price'),
        #'total_cost' : fields.float('Total Cost'),
        #'margin' : fields.float('Margin'),
        #'margin_rate' : fields.float('Margin Rate'),

        'costs' : fields.related('analytic_account_id', 'costs', type='float', string='Costs',
                                 readonly=True),
        'revenues' : fields.related('analytic_account_id', 'revenues', type='float',
                                    string='Revenues', readonly=True),
        'profit' : fields.related('analytic_account_id', 'profit', type='float', string='Profit',
                                  readonly=True),
        'profit_margin' : fields.related('analytic_account_id', 'profit_margin',
                                         type='float',string='Profit Margin', readonly=True),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
        'kind' : lambda *a: 'standard',
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
                                    ('validated', 'Validated'),
                                    ('inprogress', 'In Progress'),
                                    ('deprecated', 'Deprecated'),
                                    ('cancelled','Cancelled'),
                                   ],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1,
                                   help="The status of the catalog",
                                  ),
    }

    _defaults = {
        'year' : lambda *a: int(time.strftime('%Y'))+1,
        'state' : lambda *a: 'draft',
    }

training_catalog()

class training_seance(osv.osv):
    _name = 'training.seance'

training_seance()

class training_session(osv.osv):
    _name = 'training.session'
    _description = 'Session'

    def _is_intra(self, cr, uid, ids, name, args, context=None):
        res = dict.fromkeys(ids, 0)
        for obj in self.browse(cr, uid, ids):
            if obj.offer_id:
                res[obj.id] = (obj.offer_id.kind == 'intra')
        return res

    def _get_seances(self, cr, uid, ids, context=None):
        if not ids:
            return '0'
        return '0'


    _columns = {
        'name' : fields.char('Name',
                             size=64,
                             required=True,
                             select=1,
                             help="The session's name"),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('opened', 'Opened'),
                                    ('opened_confirmed', 'Opened Confirmed'),
                                    ('closed_confirmed', 'Closed Confirmed'),
                                    ('inprogress', 'In Progress'),
                                    ('closed', 'Closed'),
                                    ('cancelled', 'Cancelled')],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1,
                                   help="The status of the session",
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
        'seance_ids' : fields.many2many('training.seance', 'training_session_seance_rel',
                                        'session_id', 'seance_id', 'Seances', ondelete='cascade',
                                        help='List of the events in the session'),
        'date' : fields.datetime('Date',
                                 required=True,
                                 help="The date of the planned session"
                                ),

        'purchase_line_ids' : fields.one2many('training.session.purchase_line', 'session_id', 
                                              'Supplier Commands',
                                              help="The supplier commands will create a purchase order for each command for the session"
                                             ),
        'user_id' : fields.many2one('res.users', 'Responsible', required=True),
        'available_seats' : fields.integer('Available Seats'),
        'draft_seats' : fields.integer('Draft Seats'),
        'is_intra' : fields.function(_is_intra, method=True, store=True, type="boolean", string="Is Intra"),
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
        'user_id' : lambda obj,cr,uid,context: uid,
    }

    def action_create_seance(self, cr, uid, ids, context=None):
        session = self.browse(cr, uid, ids, context=context)[0]
        seance_ids = []

        for course in session.offer_id.course_ids:
            seance_proxy = self.pool.get('training.seance')
            seance_id = seance_proxy.create(cr, uid, {
                'name' : 'Seance - %s' % (session.name,),
                'course_id' : course.id,
                'min_limit' : course.course_type_id.min_limit,
                'max_limit' : course.course_type_id.max_limit,
                'user_id' : session.user_id.id,
            })
            seance_ids.append(seance_id)

        return self.write(cr, uid, ids,
                          {'seance_ids' : [(6, 0, seance_ids)]},
                          context=context)

training_session()

class training_session_purchase_line(osv.osv):
    _name = 'training.session.purchase_line'

    _rec_name = 'session_id'

    _columns = {
        'session_id' : fields.many2one('training.session', 
                                       'Session', 
                                       required=True,
                                       help="The session for this purchase order",
                                      ),
        'product_id' : fields.many2one('product.product', 
                                       'Product', 
                                       required=True,
                                       help="The product for the purchase order",
                                      ),
        'product_qty' : fields.integer('Quantity', 
                                       required=True,
                                       help="The quantity of the product for the purchase order",
                                      ),
        'product_uom_id' : fields.many2one('product.uom', 'Product UoM', 
                                           required=True,
                                           help="The unit of mesure for the product",
                                          ),
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

class training_group(osv.osv):
    _name = 'training.group'
    _description = 'Group'
    _columns = {
        'name': fields.char('Name', 
                            size=64, 
                            required=True, 
                            select=True,
                            help="The group's name",
                           ),
    }
training_group()

class training_subscription(osv.osv):
    _name = 'training.subscription'
training_subscription()

class training_participation(osv.osv):
    _name = 'training.participation'
    _description = 'Participation'
    _columns = {
        'seance_id' : fields.many2one('training.seance', 'Seance', select=True, required=True, readonly=True),
        'subscription_id' : fields.many2one('training.subscription', 'Subscription', select=True, required=True, readonly=True),
        'present' : fields.boolean('Present', help="Allows to know if a participant was present or not", select=1),
        'contact_id' : fields.related('subscription_id', 'contact_id',
                                      type='many2one',relation='res.partner.contact',
                                      string='Contact', readonly=True, select=1),
        'partner_id' : fields.related('subscription_id', 'partner_id', 
                                      type='many2one', relation='res.partner',
                                      string='Partner', readonly=True, select=2),
        'date' : fields.related('seance_id', 'date', type='datetime', string='Date', 
                                readonly=True, select=1),
    }

    _defaults = {
        'present' : lambda *a: 0,
    }

training_participation()

class training_seance(osv.osv):
    _name = 'training.seance'
    _description = 'Seance'

    def _check_date(self,cr,uid,ids,context=None):
        return self.browse(cr, uid, ids)[0].date > time.strftime('%Y-%m-%d')

    def _support_ok_get( self, cr, uid, ids, name, args, context ):
        return {}.fromkeys(ids, True)

    def _participant_count(self, cr, uid, ids, name, args, context=None):
        res = dict.fromkeys(ids, 0)
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = len(obj.participant_ids)
        return res

    _columns = {
        'name' : fields.char('Name', size=64, select=1, required=True),
        'session_ids' : fields.many2many('training.session',
                                         'training_session_event_rel',
                                         'seance_id',
                                         'session_id',
                                         'Sessions',
                                         ondelete='cascade'),
        # Attention, la date doit etre obligatoire
        'date' : fields.datetime('Date', required=False, select=1),
        'duration' : fields.float('Duration', required=False, select=1),
        'participant_ids' : fields.many2many('training.subscription',
                                             'training_participation',
                                             'seance_id',
                                             'subscription_id',
                                             'Participants',
                                             domain="[('group_id', '=', group_id)]" ),
        'group_id' : fields.many2one('training.group', 'Group'),
        'support_received' : fields.function(_support_ok_get,
                                       method=True,
                                       type="boolean",
                                       string="Support Received",
                                       readonly=True),
        'state' : fields.selection([('draft', 'Draft'),
                                    ('opened', 'Opened'),
                                    ('opened_confirmed', 'Opened Confirmed'),
                                    ('closed_confirmed', 'Closed Confirmed'),
                                    ('inprogress', 'In Progress'),
                                    ('closed', 'Closed'),
                                    ('cancelled', 'Cancelled')],
                                   'State',
                                   required=True,
                                   readonly=True,
                                   select=1
                                  ),
        'location' : fields.char('Location', size=32),
        'room' : fields.char('Room', size=32),
        'reserved' : fields.boolean('Reserved'),
        'layout' : fields.char('Layout', size=32),
        'partner_ids' : fields.many2many('res.partner', 'training_seance_partner_rel', 'seance_id', 'partner_id', 'StakeHolders'),
        'course_id' : fields.many2one('training.course', 'Course', required=True),
        'purchase_line_ids' : fields.one2many('training.seance.purchase_line', 'seance_id', 'Supplier Commands'),
        'min_limit' : fields.integer("Minimum Limit"),
        'max_limit' : fields.integer("Maximum Limit"),
        'evaluation' : fields.boolean('Evaluation'),
        'invoice' : fields.boolean('Invoice'),
        'user_id' : fields.many2one('res.users', 'Responsible', required=True),
        'available_seats' : fields.integer('Available Seats'),
        'draft_seats' : fields.integer('Draft Seats'),
        'presence_form' : fields.boolean('Presence Form'),
        'participant_count' : fields.function(_participant_count, method=True, store=True,
                                              type="integer", string="Number of Participants"),
    }

    def on_change_course_id(self, cr, uid, course_id):
        course = self.pool.get('training.course').browse(cr, uid, course_id)
        return {
            'value' : {
                'min_limit' : course.course_type_id.min_limit,
                'max_limit' : course.course_type_id.max_limit,
            }
        }

    def _check_limits(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        return obj.min_limit <= obj.max_limit

    _constraints = [
        ( _check_date, "Error, Can you check your start date", ['date']),
        (_check_limits, 'The minimum limit is greater than the maximum limit', ['min_limit', 'max_limit']),
    ]

    _defaults = {
        'reserved' : lambda *a: False,
        'min_limit' : lambda *a: 0,
        'max_limit' : lambda *a: 0,
        'evaluation' : lambda *a: 0,
        'invoice' : lambda *a: 0,
        'user_id' : lambda obj,cr,uid,context: uid, 
        'presence_form' : lambda *a: 0,
        'state' : lambda *a: 'draft',
        'date' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
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

    def search(self, cr, user, domain, offset=0, limit=None, order=None,context=None, count=False):
        session_id = context and context.get('session_id', False) or False

        if session_id:
            #cr.execute('SELECT s.id FROM training_session_event_rel rel, training_seance s where rel.session_id = %s and rel.event_id = s.event_id', (session_id,))
            #return [x[0] for x in cr.fetchall()]
            #TODO
            return []
        else:
            return super(training_seance, self).search(cr, user,
                                                       domain,
                                                       offset=offset,
                                                       limit=limit,
                                                       order=order,
                                                       context=context,
                                                       count=count)

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

    def _notification_text_compute(self, cr, uid, ids, name, args, context=None):
        res = {}

        for obj in self.browse(cr, uid, ids):
            notifications = []
            if obj.partner_id.notif_contact_id:
                notifications.append(_('Partner'))
            if obj.partner_id.notif_participant:
                notifications.append(_('Participant'))
            res[obj.id] = _(" and ").join(notifications)

        return res

    _columns = {
        'name' : fields.char('Reference', size=32, required=True, select=1, readonly=True, help='The unique identifier is generated by the system (customizable)'),
        'create_date' : fields.datetime('Creation Date', select=True, readonly=True),
        'state' : fields.selection([('draft', 'Draft'), ('confirmed','Confirmed'), ('cancelled','Cancelled'), ('done', 'Done') ], 'State', readonly=True, required=True, select=1),

        'partner_id' : fields.many2one('res.partner', 'Partner', select=1, required=True,),
        'address_id' : fields.many2one('res.partner.address', 'Invoice Address', select=1, required=True,),
        'subscription_line_ids' : fields.one2many('training.subscription.line', 'subscription_id', 'Subscription Lines'),

        'pricelist_id' : fields.many2one('product.pricelist', 'Pricelist', domain=[('type', '=', 'sale')]),
        'responsible_id' : fields.many2one('res.users', 'Responsible', required=True),
        'payment_term_id' : fields.many2one('account.payment.term', 'Payment Term'),
        'origin' : fields.char('Origin', size=64),

        'rest_seats' : fields.integer('Rest Seats'),
        'max_seats' : fields.integer('Maximum Seats'),
        'draft_seats' : fields.integer('Draft Seats'),

        'notification_active' : fields.boolean('Active'),
        'notification_text' : fields.function(_notification_text_compute, method=True,
                                              string='Kind', type='char', size=64),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
        'name' : lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'training.subscription'),
        'max_seats' : lambda *a: 0,
        'draft_seats' : lambda *a: 0,
        'responsible_id' : lambda obj, cr, uid, context: uid,
    }

    def _get_courses_with_attendance(self, cr, uid, ids, context=None):
        if not ids:
            return []
        #cr.execute("SELECT ts.course_id FROM training_seance ts, training_participation tp WHERE \
        #           ts.event_id = tp.event_id AND tp.present = %s AND tp.subscription_id = %s",
        #           (True, ids[0],))
        #return self.pool.get('training.course').browse(cr, uid, [x[0] for x in cr.fetchall()], context=context)
        return []

    def on_change_partner(self, cr, uid, ids, partner_id):
        """
        This function returns the invoice address for a specific partner, but if it didn't find an
        address, it takes the first address from the system
        """

        values = {}

        price_list_id = self.pool.get('res.partner').browse(cr, uid, partner_id).property_product_pricelist
        if price_list_id:
            values['pricelist_id'] = price_list_id.id

        proxy = self.pool.get('res.partner.address')
        ids = proxy.search(cr, uid, [('partner_id', '=', partner_id),('type', '=', 'invoice')])

        if not ids:
            ids = proxy.search(cr, uid, [('partner_id', '=', partner_id)])

        if ids:
            values['address_id'] = ids[0]

        return {'value' : values}


    # Don't forget to add the session_id field in the domain for the participants in the seance
    # form view
    #def search(self, cr, user, domain, offset=0, limit=None, order=None,context=None, count=False):
    #    session_id = context and context.get('session_id', False) or False
    #    if session_id:
    #        #cr.execute('SELECT s.id FROM training_session_event_rel rel, training_seance s where rel.session_id = %s and rel.event_id = s.event_id', (session_id,))
    #        #return [x[0] for x in cr.fetchall()]
    #        return []
    #    else:
    #        return super(training_seance, self).search(cr, user,
    #                                                   domain,
    #                                                   offset=offset,
    #                                                   limit=limit,
    #                                                   order=order,
    #                                                   context=context,
    #                                                   count=count)


    def _get_subscription(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('training.subscription.line').browse(cr, uid, ids, context=context):
            result[line.subscription_id.id] = True
        return result.keys()

    _order = 'create_date desc'

training_subscription()

class training_subscription_line(osv.osv):
    _name = 'training.subscription.line'
    _description = 'Subscription Line'
    _rec_name = 'contact_id'

    def _invoiced_paid(self, cr, uid, ids, name, args, context=None):
        res = dict.fromkeys(ids, False)

        for obj in self.browse(cr, uid, ids):
            if obj.invoice_id:
                res[obj.id]['paid'] = obj.invoice_id.state == 'paid'
                res[obj.id]['invoiced'] = obj.invoice_id.state == 'open'

        return res

    _columns = {
        'subscription_id' : fields.many2one('training.subscription', 'Subscription', required=True),

        'session_id' : fields.many2one('training.session', 'Session', select=1, required=True),
        'partner_id' : fields.related('subscription_id', 'partner_id', type='many2one', relation='res.partner'),
        'contact_id' : fields.many2one('res.partner.contact', 'Contact', select=1, required=True,
                                       domain="[('partner_id', '=', parent.partner_id)]"),
        'contact_email' : fields.related('contact_id', 'email', type='char', string='Email'),

        'group_id' : fields.many2one('training.group', 'Group'),
        'invoice_id' : fields.many2one('account.invoice', 'Invoice'),
        'paid' : fields.boolean('Paid'),
        'invoiced' : fields.boolean('Invoiced'),
        #'paid' : fields.function(_invoiced_paid, method=True, type="boolean", string="Paid",
        #                        store = True,
        #                        multi="invoiced_paid"),

        #'invoiced' : fields.function(_invoiced_paid, method=True, type="boolean", string="Invoiced",
        #                        store = True,
        #                        multi="invoiced_paid"),
    }

    _defaults = {
        'paid' : lambda *a: False,
        'invoiced' : lambda *a: False,
    }

training_subscription_line()

class training_participation_skateholder(osv.osv):

    _name = 'training.participation.skateholder'

    _columns = {
        'seance_id' : fields.many2one('training.seance', 'Seance'),
        'partner_id' : fields.many2one('res.partner', 'Partner'),
        'skateholder_id' : fields.many2one('res.partner.contact', 'Contact'),
        'evaluation' : fields.integer('Evaluation'),
        'payment_mode' : fields.selection([('contract','Contract'),('invoice','Invoice')],
                                          'Payment Mode'),
        'date' : fields.related('seance_id', 'date', type='datetime', string='Date', readonly=True),
        'course_id' : fields.related('seance_id', 'course_id',
                                     type='many2one', relation='training.course',
                                     string='Course', readonly=True),
    }

training_participation_skateholder()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
