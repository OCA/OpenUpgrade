from osv import osv, fields

class document_ifbl(osv.osv):
    _inherit = 'ir.attachment'

    _columns = {
        'state' : fields.selection([('locked', 'Locked'),('unlocked', 'Unlocked')], 'State', readonly=True),
    }

    _defaults = {
        'state' : lambda *a: 'unlocked'
    }

document_ifbl()
