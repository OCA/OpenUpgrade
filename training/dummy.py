from osv import osv, fields

class support_delivery(osv.osv):
    _name = 'dummy.support.delivery'

    _columns = {
        'name' : fields.char('Name', size=32),
    }

support_delivery()
