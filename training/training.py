# -*- coding: UTF-8 -*-
# training/training.py
from osv import osv, fields
import time

class res_partner_contact_technical_skill(osv.osv):
    _name = 'res.partner.contact_technical_skill'

    _columns = {
        'name' : fields.char('Name', size=32, select=True),
    }

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Unique name for the technical skill')
    ]

res_partner_contact_technical_skill()

class res_partner_contact(osv.osv):
    _inherit = 'res.partner.contact'

    _columns = {
        'matricule' : fields.char( 'Matricule', size=32, required=True ),
        'birthplace' : fields.char( 'BirthPlace', size=64 ),
        'education_level' : fields.char( 'Education Level', size=128 ),
                'technical_skill_ids' : fields.many2many('res.partner.contact_technical_skill', 
                                                 'res_partner_contact_technical_skill_rel', 
                                                 'contact_id', 
                                                 'skill_id', 
                                                 'Technical Skill'),
    }
res_partner_contact()

class res_partner_job(osv.osv):
    _inherit = 'res.partner.job'
    _columns = {
        'external_matricule' : fields.char( 'Matricule', size=32 ),
        'departments' : fields.text( 'Departments' ),
        'orientation' : fields.text( 'Orientation' ),
    }
res_partner_job()


class training_course_category(osv.osv):
    _name = 'training.course_category'
    _inherits = {
        'account.analytic.account' : 'analytic_account_id',
    }

    def _get_child_ids( self, cr, uid, ids, name, args, context ):
        res = {}
        for object in self.browse(cr, uid, ids):
            child_ids = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', object.analytic_account_id.id)])
            print "object.id: %s" % repr(object.id)
            print "child_ids: %s" % repr(child_ids)
            res[object.id] = self.search(cr, uid, [('analytic_account_id', 'in', child_ids)])

        print "res: %s" % repr(res)
        return res

    _columns = {
        'analytic_account_id' : fields.many2one( 'account.analytic.account', 'Analytic Account' ),
        'description' : fields.text('Description'),
        'child_ids' : fields.function( _get_child_ids, method=True, type='one2many', relation="training.course", string='Children'),
    }

training_course_category()

class training_course_type(osv.osv):
    _name = 'training.course_type'
    _inherits = {
        'account.analytic.account' : 'analytic_account_id',
    }
    
    _columns = {
        'analytic_account_id' : fields.many2one( 'account.analytic.account', 'Analytic Account' ),
    }
    
training_course_type()

class training_offer(osv.osv):
    _name = 'training.offer'
training_offer()

class training_course(osv.osv):
    _name = 'training.course'
    _inherits = {
        'account.analytic.account' : 'analytic_account_id'
    }

    def _total_duration_compute(self,cr,uid,ids,name,args,context):
        res = {}
        for object in self.browse( cr, uid, ids, context=context ):
            res[object.id] = 0.0
        return res

    def _get_child_ids( self, cr, uid, ids, name, args, context ):
        res = {}
        for object in self.browse(cr, uid, ids):
            child_ids = self.pool.get('account.analytic.account').search(cr, uid, [('parent_id', '=', object.analytic_account_id.id)])
            res[object.id] = self.search(cr, uid, [('analytic_account_id', 'in', child_ids)])
        return res

    _columns = {
        'display_name' : fields.char('Display Name', 64 ),
        'duration' : fields.time('Duration', required=True),
        'children' : fields.function( _get_child_ids, method=True, type='one2many', relation="training.course", string='Children'),
        'total_duration' : fields.function(_total_duration_compute, string='Total Duration', readonly=True, store=True, method=True, type="time"),
        'sequence' : fields.integer('Sequence'),
        'target_public' : fields.char('Target Public', 256),
        'reference_id' : fields.many2one('training.course', 'Master Course'),

        'analytic_account_id' : fields.many2one( 'account.analytic.account', 'Account' ),
        #'category_id' : fields.many2one( 'training.course_category', 'Category', required=True),
        'course_type_id' : fields.many2one('training.course_type', 'Type', required=True),

        'instructor_ids' : fields.many2many( 
            'res.partner', 'training_course_partner_rel', 
            'course_id', 'partner_id',
            'Instructors'
        ),

        'internal_note' : fields.text('Note'),

        'lang_id' : fields.many2one('res.lang', 'Language', required=True),
        'offer_ids' : fields.many2many( 
            'training.offer', 'training_course_offer_rel', 
            'course_id', 'offer_id',
            'Offers' ),
        'state' : fields.selection([('draft', 'Draft'),('mature', 'Mature'), ('deprecated', 'Deprecated')], 'State'),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
    }

training_course()

class training_questionnaire(osv.osv):
    _name = 'training.questionnaire'
training_questionnaire()

class training_offer(osv.osv):
    _name = 'training.offer'
    _columns = {
        'name' : fields.char('Name', size=64, select=True, required=True ),
        'product_id' : fields.many2one( 'product.product', 'Product' ),
        'course_ids' : fields.many2many( 
            'training.course', 'training_course_offer_rel', 
            'offer_id', 'course_id', 
            'Courses' 
        ),
        'objective' : fields.text('Objective'),
        'description' : fields.text('Description'),
        'questionnaire_ids' : fields.many2many(
            'training.questionnaire', 'training_questionnaire_offer_rel', 
            'offer_id', 'questionnaire_id', 
            'Exams'
        ),
    }
training_offer()

class training_questionnaire(osv.osv):
    _name = 'training.questionnaire'

    _columns = {
        'name' : fields.char( 'Name', size=32, required=True ),
        'course_id' : fields.many2one('training.course', 'Course'),
        'state' : fields.selection([('draft', 'Draft'),('mature', 'Mature'),('deprecated', 'Deprecated')], 'State', required=True),
        'objective' : fields.text('Objective'),
        'description' : fields.text('Description'),
    }
    _defaults = {
        'name': lambda *a: 'draft'
    }

training_questionnaire()

class training_catalog(osv.osv):
    _name = 'training.catalog'
    _rec_name = 'year'
    _columns = {
        'year' : fields.integer('Year', size=4, required=True, select=True),
        'session_ids' : fields.one2many('training.session', 'catalog_id', 'Sessions'),
        'note' : fields.text('Note'),
        'state' : fields.selection([('draft','Draft'),('in_progress', 'In Progress'),('done','Done')], 'State', required=True),
    }

    _defaults = {
        'year' : lambda *a: int(time.strftime('%Y'))+1,
        'state' : lambda *a: 'draft',
    }

training_catalog()


class training_session(osv.osv):
    _name = 'training.session'
    _columns = {
        'name' : fields.char('Name', size=64, required=True, select=True),
        'state' : 
            fields.selection([ 
                ('draft', 'Draft'), 
                ('confirm', 'Confirm'), 
                ('cancel', 'Cancel')], 
                'State', 
                required=True, 
                select=True
            ),
        'offer_id' : fields.many2one('training.offer', 'Offer', select=True, required=True),
        'catalog_id' : fields.many2one('training.catalog', 'Catalog', select=True),
        'event_ids' : fields.one2many('training.event', 'session_id', 'Events', readonly=True, ondelete="cascade"),
        'date_start' : fields.datetime('Date Start', required=True),
    }

    def on_change_course_id( self, cr, uid, ids, course_id ):
        print "on_change_course_id" 
        print "ids: %s" % repr(ids)
        event_ids = []

        if course_id:
            course_proxy = self.pool.get('training.course')
            course = course_proxy.browse(cr,uid,[course_id])[0]

            seance_proxy = self.pool.get('training.seance')

            print "course.name: %s" % repr(course.name)
            print "course.is_alone: %s" % repr(course.is_alone)

            course_ids = course.course_ids

            if course.is_alone:
                vals = {
                    'name' : course.name,
                    'session_id' : ids[0],
                }
                seance_id = seance_proxy.create(cr,uid,vals)
                event_ids.append( seance_id )
            else:
                for m in course.course_ids:
                    print "course.name: %s" % repr(m.name)
                    print "course.is_alone: %s" % repr(m.is_alone)

                    vals = {
                        'name' : m.name,
                        'session_id' : ids[0],
                    }
                    seance_id = seance_proxy.create(cr,uid,vals)
                    event_ids.append( seance_id )

            print "event_ids: %s" % repr(event_ids)
                

        return { 'value' : {'event_ids' : event_ids} }


    def _find_catalog_id(self,cr,uid,data,context=None):
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

training_session()

class training_massive_subscription_wizard(osv.osv_memory):
    _name = 'wizard.training.massive.subscription'

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
                subscription_id = subscription_proxy.create(cr, uid, 
                                                            vals,
                                                            context = context )
        return { 'type' : 'ir.actions.act_window_close' }

    _columns = {
        'partner_ids' : fields.many2many( 'res.partner.contact', 'tmi_partner_rel', 'wiz_id', 'partner_id', 'Partners', required=True ),
        'session_ids' : fields.many2many( 'training.session', 'tmi_session_rel', 'wiz_id', 'session_id', 'Sessions', required=True ),
    }

training_massive_subscription_wizard()

class training_location(osv.osv):
    _name = 'training.location'

    _columns = {
        'name' : fields.char('Name', size=32, select=True, required=True),
    }

training_location()

class training_event(osv.osv):
    _name = 'training.event'

    def _check_date_start(self,cr,uid,ids,context=None):
        obj = self.browse(cr, uid, ids)[0]
        return self.browse(cr,uid,ids)[0].date_start > time.strftime('%Y-%m-%d')

    def _check_dates(self, cr, uid, ids, context = None):
        obj = self.browse( cr, uid, ids )[0]
        return obj.date_start < obj.date_stop

    _columns = {
        'name' : fields.char('Name', size=64, select=True, required=True),
        'session_id' : fields.many2one('training.session', 'Session', required=True, select=True, ondelete="cascade"),
        # Attention, la date doit etre obligatoire
        'date_start' : fields.datetime('Date Start', required=False, select=True),
        'date_stop' : fields.datetime('Date Stop', required=False, select=True),
        'location_id' : fields.many2one('training.location', 'Location', select=True),
    }

    _constraints = [
        #    ( _check_date_start, "Errorr, Can you check your start date", ['date_start']),
        #( _check_dates, "Error with the start date and the stop date", ['date_start', 'date_stop']) 
    ]

    _defaults = {
        'date_start' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_stop' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }

training_event()

class training_plannified_examen(osv.osv):
    _name = 'training.plannified_examen'
    _inherits = {
        'training.event' : 'event_id'
    }
    _columns = {
        'partner_id' : fields.many2one('res.partner', 'Partner', domain=[('is_guardian', '=', True)], select=True, required=True),
        'event_id' : fields.many2one('training.event', 'Event'),
    }

training_plannified_examen()

class training_group(osv.osv):
    _name = 'training.group'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
    }
training_group()

class training_seance(osv.osv):
    _name = 'training.seance'
    _inherits = {
        'training.event' : 'event_id'
    }
    _columns = {
        'partner_id' : fields.many2one('res.partner', 'Partner', domain=[('is_instructor', '=', True)]),
        'event_id' : fields.many2one('training.event', 'Event'),
        'state' : fields.selection([('draft', 'Draft'),('confirm', 'Confirm'),('cancel','Cancel')], 'State', required=True),
        'group_id' : fields.many2one('training.group', 'Group'),
    }
    _defaults = {
        'state' : lambda *a: 'draft',
    }

training_seance()

class training_subscription(osv.osv):
    _name = 'training.subscription'
    _columns = {
        'session_id' : fields.many2one('training.session', 'Session', select=True, required=True),
        'partner_id' : 
            fields.many2one(
                'res.partner', 'Partner', 
                select=True, 
                required=True
            ),
        # Pour le group ID, discuter pour savoir si on doit utiliser le seuil pédagogique du groupe pour savoir si on crée un nouveau group ou non
        'group_id' : fields.many2one('training.group', 'Group', readonly=True),
        'state' : fields.selection([('draft', 'Draft'),('confirm','Confirm'),('cancel','Cancel')], 'State', required=True ),
    }

    _defaults = {
        'state' : lambda *a: 'draft',
    }

training_subscription()

class training_participation(osv.osv):
    _name = 'training.participation'
    _columns = {
        'event_id' : fields.many2one('training.event', 'Event' ),
        'partner_id' : 
            fields.many2one(
                'res.partner', 'Partner', 
                select=True, 
                required=True
            ),
    }

training_participation()

class training_question(osv.osv):
    _name = 'training.question'
    _columns = {
        'questionnaire_id' : 
            fields.many2one(
                'training.questionnaire', 'Questionnaire', 
                select=True, 
                required=True
            ),
    }

training_question()

class training_examen_answers(osv.osv):
    _name = 'training.examen_answers'
    _columns = {
        'plannified_examen_id' : fields.many2one('training.plannified_examen', 'Plannified Examen', select=True, required=True),
        'question_id' : fields.many2one('training.question', 'Question', select=True, required=True),
        'partner_id' : fields.many2one('res.partner', select=True, required=True),
    }

training_examen_answers()

