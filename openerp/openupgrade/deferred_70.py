# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
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

"""
This module contains a set of functions that should be called at the end of the
migration. A migration may be run several times after corrections in the code
or the configuration, and there is no way for OpenERP to detect a succesful
result. Therefore, the functions in this module should be robust against
being run multiple times on the same database.
"""

import logging

from psycopg2 import sql

from openupgradelib.openupgrade import logged_query, savepoint
from openerp import SUPERUSER_ID

logger = logging.getLogger("OpenUpgrade")


def sync_commercial_fields(cr, pool):
    """
    Take care of propagating the commercial fields
    in the new partner model.
    """
    partner_obj = pool.get('res.partner')
    partner_ids = partner_obj.search(
        cr, SUPERUSER_ID,
        [('parent_id', '!=', False)],
        context={'active_test': False})
    # This will be just ['vat'] unless you have installed addons that
    # add more fields to sync; all core addons that override this method are
    # supported; without weird scenarios, it will be optimized
    commercial_fields = partner_obj._commercial_fields(cr, SUPERUSER_ID)
    for field in commercial_fields:
        # TODO: Support m2m field optimization, if ever needed
        if partner_obj._all_columns[field].column._type == 'many2many':
            logger.warning(
                'Field %s cannot be optimized; falling back to ORM sync',
                field,
            )
            _sync_commercial_fields_orm(cr, pool, partner_ids)
            break
    else:
        # Use optimized sync for most records
        _sync_commercial_fields_sql(cr, pool, commercial_fields)
        # Companies with parent_id are subcompanies; this is a rare case,
        # which requires recursion to find its commercial partner
        subcompanies_ids = partner_obj.search(
            cr, SUPERUSER_ID,
            [('is_company', '=', True), ('parent_id', '!=', False)],
            context={'active_test': False},
        )
        _sync_commercial_fields_orm(cr, pool, subcompanies_ids)


def _sync_commercial_fields_sql(cr, pool, commercial_fields):
    """Perform optimized commercial fields sync."""
    ResPartner = pool.get("res.partner")
    # Separate raw from property fields
    property_fields, raw_fields = [], []
    for field in commercial_fields:
        multi = getattr(ResPartner._all_columns[field].column, '_multi', None)
        if multi == 'properties':
            property_fields.append(field)
        else:
            raw_fields.append(field)
    # Sync raw fields
    logger.info(
        "Syncing raw commercial fields between all partners using SQL")
    set_sentence = sql.SQL(", ").join(
        sql.SQL("{0} = parent.{0}").format(sql.Identifier(field))
        for field in raw_fields
    )
    logged_query(
        cr,
        sql.SQL(
            """
            UPDATE res_partner AS contact
            SET {set_sentence}
            FROM res_partner AS parent
            WHERE
                NOT contact.is_company AND
                contact.parent_id = parent.id
            """
        ).format(set_sentence=set_sentence),
    )
    # Sync property fields
    logger.info(
        "Syncing property commercial fields between all partners using SQL")
    # Delete property fields from contacts that belong to a company
    logged_query(
        cr,
        """
        DELETE FROM ir_property
        WHERE
            name = ANY(%(property_fields)s) AND
            res_id IN (
                SELECT 'res.partner,' || id
                FROM res_partner
                WHERE
                    NOT is_company AND
                    parent_id IS NOT NULL
            )
        """,
        {'property_fields': property_fields},
    )
    logged_query(
        cr,
        """
        INSERT INTO ir_property (
            company_id,
            create_date,
            create_uid,
            fields_id,
            name,
            res_id,
            type,
            value_binary,
            value_datetime,
            value_float,
            value_integer,
            value_reference,
            value_text,
            write_date,
            write_uid
        )
        SELECT
            company_id,
            create_date,
            create_uid,
            fields_id,
            name,
            subpartner.child_ref,
            type,
            value_binary,
            value_datetime,
            value_float,
            value_integer,
            value_reference,
            value_text,
            write_date,
            write_uid
        FROM ir_property
        INNER JOIN
            (
                SELECT
                    'res.partner,' || id AS child_ref,
                    'res.partner,' || parent_id AS parent_ref
                FROM res_partner
                WHERE
                    NOT is_company AND
                    parent_id IS NOT NULL
            ) AS subpartner
            ON ir_property.res_id = subpartner.parent_ref
        WHERE
            name = ANY(%(property_fields)s)
        """,
        {'property_fields': property_fields},
    )


def _sync_commercial_fields_orm(cr, pool, partner_ids):
    """Sync commercial fields using ORM with slow core methods."""
    logger.info(
        "Syncing commercial fields between %s partners using ORM",
        len(partner_ids))
    partner_obj = pool.get('res.partner')
    good = True
    for partner in partner_obj.browse(
            cr, SUPERUSER_ID, partner_ids):
        try:
            with savepoint(cr):
                partner_obj._commercial_sync_from_company(
                    cr, SUPERUSER_ID, partner)
        except Exception:
            good = False
            logger.exception(
                "Failed syncing commercial fields for partner %d %r",
                partner.id,
                (partner.name, partner.vat, partner.commercial_partner_id,
                 partner.commercial_partner_id.name),
            )
    if not good:
        raise Exception(
            "Syncing partners' commercial fields failed. "
            "Check the logs, fix and retry."
        )


def migrate_deferred(cr, pool):
    sync_commercial_fields(cr, pool)
    # Newly introduced _parent_store on menu items leaves gaps
    # after upgrade of other modules for *some* reason. See lp:1226086
    pool.get('ir.ui.menu')._parent_store_compute(cr)
