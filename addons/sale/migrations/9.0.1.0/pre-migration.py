# -*- coding: utf-8 -*-
# © 2015 Microcom
# © 2016 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2016 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# © 2016 Opener B.V. - Stefan Rijnhart
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


column_renames = {
    'sale_order': [
        ('section_id', 'team_id'),
    ],
    'account_invoice': [
        ('section_id', 'team_id'),
    ],
    # 'invoice_id' in 8.0 already referred to invoice lines
    'sale_order_line_invoice_rel': [
        ('invoice_id', 'invoice_line_id'),
    ],
    'sale_order_tax': [
        ('order_line_id', 'sale_order_line_id'),
        ('tax_id', 'account_tax_id'),
    ],
}

table_renames = [
    ('sale_order_tax', 'account_tax_sale_order_line_rel'),
]

column_copies = {
    'sale_order': [
        ('state', None, None),
    ],
    'sale_order_line': [
        ('state', None, None),
    ],
}


def map_order_state(cr):
    """ Map values for state field in sale.order and sale.order.line.
    Do this in the pre script because it influences the automatic calculation
    of the computed fields wrt. invoicing """
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('state'), 'state', [
            ('waiting_date', 'sale'), ('progress', 'sale'),
            ('manual', 'sale'), ('shipping_except', 'sale'),
            ('invoice_except', 'sale')],
        table='sale_order')
    cr.execute("""
        UPDATE sale_order_line sol
        SET state = so.state
        FROM sale_order so
        WHERE sol.order_id = so.id""")


def prepopulate_fields(cr):
    """ Recomputing a fields will be very expensive via the ORM, so do it
    here for fields where the computation is trivial"""
    cr.execute('alter table sale_order_line add column qty_invoiced numeric')
    cr.execute(
        """\
        with line2qty_invoiced(id, qty_invoiced) as (
            select l.id, sum(
                case
                    when i.type='out_invoice' then il.quantity
                    when i.type='out_refund' then -il.quantity
                end * uom_invoice.factor / uom_sale.factor
            ) s
            from sale_order_line l
            join sale_order_line_invoice_rel r on r.order_line_id=l.id
            join account_invoice_line il on r.invoice_line_id=il.id
            join account_invoice i on i.id=il.invoice_id
            join product_uom uom_invoice on il.uom_id=uom_invoice.id
            join product_uom uom_sale on l.product_uom=uom_sale.id
            group by l.id
        )
        update sale_order_line
        set qty_invoiced=line2qty_invoiced.qty_invoiced
        from line2qty_invoiced where line2qty_invoiced.id=sale_order_line.id
        """)
    cr.execute('alter table sale_order_line add column qty_to_invoice numeric')
    cr.execute(
        """\
        update sale_order_line
        set qty_to_invoice=product_uom_qty - coalesce(qty_invoiced, 0)
        from product_product p
        join product_template pt on p.product_tmpl_id=pt.id
        where sale_order_line.product_id=p.id
        """)
    cr.execute('alter table sale_order_line add column currency_id integer')
    cr.execute(
        """\
        update sale_order_line l set currency_id=p.currency_id
        from sale_order o join product_pricelist p on o.pricelist_id=p.id
        where l.order_id=o.id
        """)
    cr.execute('alter table sale_order_line add column invoice_status varchar')
    cr.execute("update sale_order_line set invoice_status='no'")
    cr.execute(
        """\
        update sale_order_line
        set invoice_status=(
            case when coalesce(qty_to_invoice, 0)<=0 then 'invoiced'
            else 'to invoice' end
        )
        where state in ('sale', 'done')
        """)
    cr.execute('alter table sale_order add column invoice_status varchar')
    cr.execute("update sale_order set invoice_status='no'")
    cr.execute(
        """\
        update sale_order o
        set invoice_status='to invoice'
        from sale_order_line l
        where o.id=l.order_id and l.invoice_status='to invoice'
        """)
    cr.execute(
        """\
        update sale_order o
        set invoice_status='invoiced'
        where exists (
            select id from sale_order_line
            where invoice_status='invoiced' and order_id=o.id
        ) and not exists (
            select id from sale_order_line
            where invoice_status<>'invoiced' and order_id=o.id
        )
        """)


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_tables(cr, table_renames)
    map_order_state(cr)
    prepopulate_fields(cr)
