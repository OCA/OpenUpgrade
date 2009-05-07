from osv import osv, fields

class portal_training_purchase_line_supplier(osv.osv):
    _inherit = 'purchase.order.line'

    _columns = {
        'confirmed_supplier' : fields.boolean('Confirmed by Supplier'),
    }

portal_training_purchase_line_supplier()

class portal_training_subscription(osv.osv):
    _name = 'portal.training.subscription'

    _columns = {
        'date' : fields.date('Date', select=1, readonly=True),
        'course_id' : fields.many2one('training.course', 'Course', select=1, readonly=True),
        'seance_id' : fields.many2one('training.seance', 'Seance', readonly=True),
        'session_id' : fields.many2one('training.session', 'Session', readonly=True),
        'partner_id' : fields.many2one('res.partner', 'Partner', readonly=True),
        'contact_id' : fields.many2one('res.partner.contact', 'Contact', select=1, readonly=True),
        'examen' : fields.boolean('Is Examen', readonly=True),
        'note' : fields.text('Note', readonly=True),
    }

portal_training_subscription()

