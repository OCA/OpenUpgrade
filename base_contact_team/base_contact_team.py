from osv import osv, fields

class res_partner_team(osv.osv):
    _name = 'res.partner.team'

    _columns = {
        'name' : fields.char('Name', size=64, required=True, select=True),
        'description' : fields.text('Description'),
    }

res_partner_team()

class res_partner_job(osv.osv):
    _inherit = 'res.partner.job'

    _columns = {
        'team_id' : fields.many2one('res.partner.team', 'Team'),
    }

res_partner_job()
