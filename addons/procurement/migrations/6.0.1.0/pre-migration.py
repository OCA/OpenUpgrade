# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012 Therp BV (<http://therp.nl>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from openupgrade import openupgrade

logger = logging.getLogger('OpenUpgrade: procurement')

renamed_xmlids = [
    ('mrp.wkf', 'procurement.wkf_procurement'),
    ('mrp.act_draft', 'procurement.act_draft'),
    ('mrp.act_cancel', 'procurement.act_cancel'),
    ('mrp.act_confirm', 'procurement.act_confirm'),
    ('mrp.act_confirm_wait', 'procurement.act_confirm_wait'),
    ('mrp.act_confirm_mts', 'procurement.act_confirm_mts'),
    ('mrp.act_confirm_mto', 'procurement.act_confirm_mto'),
    ('mrp.act_make_to_stock', 'procurement.act_make_to_stock'),
    ('mrp.act_produce_check', 'procurement.act_produce_check'),
    ('mrp.act_produce_service', 'procurement.act_produce_service'),
    ('mrp.act_make_done', 'procurement.act_make_done'),
    ('mrp.act_wait_done', 'procurement.act_wait_done'),
    ('mrp.act_done', 'procurement.act_done'),
    ('mrp.trans_draft_confirm', 'procurement.trans_draft_confirm'),
    ('mrp.trans_confirm_cancel2', 'procurement.trans_confirm_cancel2'),
    ('mrp.trans_confirm_wait_done', 'procurement.trans_confirm_wait_done'),
    ('mrp.trans_confirm_cancel', 'procurement.trans_confirm_cancel'),
    ('mrp.trans_confirm_confirm_wait', 'procurement.trans_confirm_confirm_wait'),
    ('mrp.trans_confirm_wait_confirm_mto', 'procurement.trans_confirm_wait_confirm_mto'),
    ('mrp.trans_confirm_wait_confirm_mts', 'procurement.trans_confirm_wait_confirm_mts'),
    ('mrp.trans_confirm_mts_cancel', 'procurement.trans_confirm_mts_cancel'),
    ('mrp.trans_confirm_waiting_cancel', 'procurement.trans_confirm_waiting_cancel'), 
    ('mrp.trans_confirm_mts_confirm', 'procurement.trans_confirm_mts_confirm'),
    ('mrp.trans_confirm_mto_cancel', 'procurement.trans_confirm_mto_cancel'),
    ('mrp.trans_confirm_mto_confirm', 'procurement.trans_confirm_mto_confirm'),
    ('mrp.trans_draft_cancel', 'procurement.trans_draft_cancel'),
    ('mrp.trans_confirm_mts_make_to_stock', 'procurement.trans_confirm_mts_make_to_stock'),
    ('mrp.trans_confirm_mto_produce_check', 'procurement.trans_confirm_mto_produce_check'),
    ('mrp.trans_product_check_produce_service', 'procurement.trans_product_check_produce_service'),
    ('mrp.trans_confirm_mto_buy', 'procurement.trans_confirm_mto_purchase'),
    ('mrp.trans_make_to_stock_make_done', 'procurement.trans_make_to_stock_make_done'),
    ('mrp.trans_produce_service_cancel', 'procurement.trans_produce_service_cancel'),
    ('mrp.trans_produce_service_make_done', 'procurement.trans_produce_service_make_done'),
    ('mrp.trans_make_done_done', 'procurement.trans_make_done_done'),
    ('mrp.trans_make_done_confirm', 'procurement.trans_make_done_confirm'),
    ('mrp.sequence_mrp_op_type', 'procurement.sequence_mrp_op_type'),
    ('mrp.sequence_mrp_op', 'procurement.sequence_mrp_op'),
    ('mrp.ir_cron_scheduler_action', 'procurement.ir_cron_scheduler_action'),
]     
   
# Cannot use the OpenUpgrade decorator
# as in this case, do not return immediately when 
# version is False. We need to facilitate the
# functionality move from the mrp module

def migrate(cr, version):
    logger.info("pre-migration.py called with version %s" % version)
    try:
        if openupgrade.table_exists(cr, 'mrp_procurement'):
            logger.info("moving functionality from the OpenERP 5 MRP module")
            openupgrade.rename_tables(cr, [('mrp_procurement', 'procurement_order')])
            openupgrade.rename_models(cr, [('mrp.procurement', 'procurement.order')]) 
            openupgrade.rename_xmlids(cr, renamed_xmlids)
    except Exception, e:
        logger.error("error in pre-migration.py: %s" % e)
        raise

