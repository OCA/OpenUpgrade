from osv import osv, fields

class training_course(osv.osv):
    _inherit = 'training.course'

    _columns = {
        'display_name' : fields.char('Display Name', size=38,
                                     help="Allows to show a short name for this course"),
    }

training_course()
