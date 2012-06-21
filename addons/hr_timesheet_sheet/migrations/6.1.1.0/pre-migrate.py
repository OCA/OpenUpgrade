import logging
from openerp.openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade')

@openupgrade.migrate()
def migrate(cr, version):
    cr.execute("""select id, timesheet_range, name from res_company where 
               timesheet_range='year'""")
    for row in cr.fetchall():
        logger.warning('%s is configured for timesheet validation per year. '+
                       'This was deprecated so validation for %s is changed '+
                       'to monthly.', row[2], row[2])
    cr.execute("""update res_company set timesheet_range='month'
               where timesheet_range='year'""")
