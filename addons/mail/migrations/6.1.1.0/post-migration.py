# -*- coding: utf-8 -*-

from osv import osv
import pooler, logging
from openerp.openupgrade import openupgrade

from openerp import SUPERUSER_ID

logger = logging.getLogger('OpenUpgrade')
me = __file__

defaults = {
    # False results in column value NULL
    # None value triggers a call to the model's default function 
    'mail.message': [
        ('subtype', 'plain'),
        ],    
    }

def signal_html_messages(cr, pool):
    msg_obj = pool.get('mail.message')
    messages = msg_obj.search(
        cr, SUPERUSER_ID, [('body_text', '=', '<html>')],
        limit=0, context={'active_test': False})
    found = 0
    for msg in messages:
        found += 1
        msg_obj.write(
            cr, SUPERUSER_ID, {
                'subtype': 'html',
                'body_html':  msg.body_text,
                'body_text': False,
                }
            )
    logger.info("%s: found %d HTML messages", me, found)

def migrate(cr, version):
    try:
        logger.info("%s called", me)
        pool = pooler.get_pool(cr.dbname)
        openupgrade.set_defaults(cr, pool, defaults)
        signal_html_messages(cr, pool)
        openupgrade.load_data(cr, 'mail', 'migrations/6.1.1.0/data/mail_data.xml')
        openupgrade.load_data(cr, 'mail', 'migrations/6.1.1.0/data/ir.model.access.csv')
    except Exception, e:
        raise osv.except_osv("OpenUpgrade", '%s: %s' % (me, e))
