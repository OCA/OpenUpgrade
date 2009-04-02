from osv import osv, fields

class portal_training_subscription(osv.osv):
    _name = 'portal.training.subscription'

    _columns = {
        'date' : fields.date('Date', select=1, readonly=True),
        'course_id' : fields.many2one('training.course', select=1, readonly=True),
        'seance_id' : fields.many2one('training.seance', readonly=True),
        'session_id' : fields.many2one('training.session', readonly=True),
        'partner_id' : fields.many2one('res.partner', readonly=True),
        'contact_id' : fields.many2one('res.partner.contact', select=1, readonly=True),
        'examen' : fields.boolean('Is Examen', readonly=True),
        'note' : fields.text('Note', readonly=True),
    }

portal_training_subscription()

