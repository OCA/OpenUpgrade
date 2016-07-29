# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from openupgradelib import openupgrade
logger = logging.getLogger('OpenUpgrade')


def map_expense_state(cr):
    # Mapping values of state field for hr_expense
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('state'), 'state',
        [('confirm', 'submit'), ('accepted', 'approve'), ('done', 'post'),
         ('paid', 'done'), ('cancelled', 'cancel')],
        table='hr_expense')


def hr_expense(cr):
    # Sets hr_expense_line product values to hr_expense
    cr.execute("""
    UPDATE hr_expense h SET product_id = l.product_id, unit_amount =
    l.unit_amount, quantity = l.unit_quantity,
    analytic_account_id = l.analytic_account FROM hr_expense_line l
    WHERE l.expense_id = h.id
    """)

    # Counting one2many hr_expense_line and later creating hr_expense record
    # for it.
    cr.execute("""
    SELECT * from (SELECT expense_id, COUNT(expense_id) AS "no_of_expenses",
    case when COUNT(expense_id)>1 then true else null end as "consider"
    FROM hr_expense_line GROUP BY expense_id) as voila where consider is
    not null""")
    expense_count = cr.dictfetchall()
    for x in expense_count:
        expense = x['expense_id']
        no_of_expense = x['no_of_expenses']
        cr.execute("""
            select id from hr_expense_line where expense_id = %s
            """ % expense)
        expense_line_ids = cr.fetchall()
        line_ids = [n[0] for n in expense_line_ids[1:]]
        for z, p in zip(range(no_of_expense-1), line_ids):
            cr.execute("""
            INSERT INTO hr_expense
                (company_id, currency_id, journal_id, employee_id, state,
                date, account_move_id, name, bank_journal_id,
                untaxed_amount, payment_mode, analytic_account_id,
                create_date, write_date, create_uid, write_uid,
                product_uom_id, unit_amount, quantity, product_id)
                SELECT company_id, currency_id, journal_id, employee_id,
                state, date, account_move_id, name, bank_journal_id, 0.00.
                'own_account',
                (select analytic_account from hr_expense_line where id =
                %(a)s),
                (select create_date from hr_expense_line where id = %(a)s),
                (select write_date from hr_expense_line where id = %(a)s),
                (select create_uid from hr_expense_line where id = %(a)s),
                (select write_uid from hr_expense_line where id = %(a)s),
                (select uom_id from hr_expense_line where id = %(a)s),
                (select unit_amount from hr_expense_line where id = %(a)s),
                (select unit_quantity from hr_expense_line where id = %(a)s),
                (select product_id from hr_expense_line where id = %(a)s)
                FROM hr_expense where id = %(b)s
            """ % {'a': p, 'b': expense})
    cr.execute("""
        UPDATE hr_expense h SET total_amount =
        (select cast(round(unit_amount*quantity) as
        decimal(18,2)) from hr_expense e where e.id=h.id)
    """)


@openupgrade.migrate()
def migrate(cr, version):
    map_expense_state(cr)
    hr_expense(cr)
