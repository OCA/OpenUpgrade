from osv import fields,osv

AVAILABLE_STATES = [
    ('draft','Draft'),
    ('open','Open'),
    ('cancel', 'Canceled'),
    ('done', 'Closed'),
    ('pending','Pending')
]
class report_crm_case_section_categ2(osv.osv):
    _name = "report.crm.case.section.categ2"
    _description = "Cases by section and category2"
    _auto = False
    _columns = {
        'user_id':fields.many2one('res.users', 'User', readonly=True),
        'section_id':fields.many2one('crm.case.section', 'Section', readonly=True),
        'category2_id':fields.many2one('crm.case.category2', 'Type', readonly=True),
        'stage_id':fields.many2one('crm.case.stage', 'Stage', readonly=True),
        'nbr': fields.integer('# of Cases', readonly=True),
        'state': fields.selection(AVAILABLE_STATES, 'State', size=16, readonly=True),        
        'delay_close': fields.char('Delay Close', size=20, readonly=True),
                }
    _order = 'category2_id, section_id'
    
    def init(self, cr):
        cr.execute("""
              create or replace view report_crm_case_section_categ2 as (
                select
                    min(c.id) as id,
                    c.user_id,
                    c.state,
                    c.category2_id,
                    c.stage_id,
                    c.section_id,
                    count(*) as nbr,
                    to_char(avg(date_closed-c.create_date), 'DD"d" HH24:MI:SS') as delay_close
                from
                    crm_case c
                where c.category2_id is not null
                group by c.user_id, c.state, c.stage_id, c.category2_id, c.section_id)""")

report_crm_case_section_categ2()