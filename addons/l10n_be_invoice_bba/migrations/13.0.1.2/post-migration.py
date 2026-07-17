# Copyright 2023 Coop IT Easy (https://coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_account_journal_invoice_reference_type(env):
    # in odoo 12, res.company.invoice_reference_type control the generation of
    # the payment reference for invoices. the available choices are:
    #
    # * "invoice_number" (INV/2024/0001/01), where 1 is the id of the invoice
    # * "customer” (CUST/12345), where 12345 is the internal reference of the
    #   client or its id if it is not defined
    # * "structured” (if l10n_be_invoice_bba is installed)
    #
    # when "structured" is selected, a belgian structured communication is
    # generated. its contents depend on the selected algorithm (by
    # res.company.l10n_be_structured_comm). 3 algorithms are available:
    #
    # * "random” (+++838/5211/08712+++)
    # * "date” (+++337/2024/00103+++), where 337 is the day number, 2024 is
    #   the year and the last digits (ignoring the last 2 checksum digits) are
    #   incremented for each invoice of the same day, thus limit the number of
    #   invoices per day to 999
    # * "partner_ref” (+++123/4500/00113+++), where 12345 is the internal
    #   refererence of the client and the last digits (ignoring the last 2
    #   checksum digits) are incremented for each invoice for that client,
    #   thus limiting the overal number of invoices per client)
    #
    # in odoo 13, invoice_reference_type is defined on account.journal instead
    # of on res.company. its available choices are similar ("invoice",
    # "partner") but their behavior depend on the value of
    # account.journal.invoice_reference_model, which defines the format of the
    # reference. the available choices are:
    #
    # * "odoo", which behaves similarly as in odoo 12 when
    #   invoice_reference_type is set to "invoice_number" or "customer".
    # * "be", which generates a belgian structured communication.
    #
    # with "be" is selected, although belgian structured communications are
    # generated like in odoo 12, none of the previous algorithms are
    # available. the algorithms are selected by the invoice_reference_type
    # field, and these are the available choices:
    #
    # * "invoice" (+++000/0000/00101+++), which directly uses the id of the
    #   invoice.
    # * "partner" (+++000/0012/34526+++), which directly uses the reference of
    #   the client or its id if no reference is defined; the structured
    #   communication stays the same for all invoices of the same client.
    #
    # because there is no incrementation with the "partner" choice, it could
    # lead to problems if the user expects unique payment references for each
    # invoice. therefore, the "invoice" choice (which is the default) is
    # forced here, regardless of the previously chosen algorithm.
    openupgrade.logged_query(
        env.cr,
        """
        update account_journal
        set
            invoice_reference_type = 'invoice',
            invoice_reference_model = 'be'
        where
            invoice_reference_type = 'structured'
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_account_journal_invoice_reference_type(env)
    openupgrade.load_data(env.cr, "l10n_be_invoice_bba", "migrations/13.0.1.2/noupdate_changes.xml")
