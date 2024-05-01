# Copyright 2023 Coop IT Easy SC
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def convert_service_to_purchase_to_company_dependent(env):
    """The product.template.service_to_purchase field became company-dependent.
    this means that it is no longer stored in the product_template table,
    but in the ir_property table.

    for such cases, openupgrade.convert_to_company_dependent() should
    normally be used, but that function does not seem to support converting
    a field to company-dependent without changing its name at the same time.
    moreover, it stores boolean values even when they are false (what odoo
    does not), and it creates values for all companies, which does not make
    sense when a record is linked to a particular company only.
    """
    service_to_purchase_field_id = (
        env.ref("sale_purchase.field_product_template__service_to_purchase").id,
    )
    # this boolean property stores its value in the value_integer column, and
    # it is only stored if it is true.
    openupgrade.logged_query(
        env.cr,
        """
        insert into ir_property (
            company_id, fields_id, value_integer, name, res_id, type
        )
        select
            company_id,
            %(field_id)s,
            1,
            'service_to_purchase',
            'product.template,' || id,
            'boolean'
        from product_template
        where
            company_id is not null and
            service_to_purchase
        order by id
        """,
        {"field_id": service_to_purchase_field_id},
    )
    # for product.template records that are not linked to a company, create an
    # ir.property record for each company.
    openupgrade.logged_query(
        env.cr,
        """
        insert into ir_property (
            company_id,
            fields_id,
            value_integer,
            name,
            res_id,
            type
        )
        select
            rc.id,
            %(field_id)s,
            1,
            'service_to_purchase',
            'product.template,' || pt.id,
            'boolean'
        from product_template as pt
        inner join res_company as rc on
            pt.company_id is null and
            pt.service_to_purchase
        order by pt.id, rc.id
        """,
        {"field_id": service_to_purchase_field_id},
    )


@openupgrade.migrate()
def migrate(env, version):
    convert_service_to_purchase_to_company_dependent(env)
    openupgrade.delete_records_safely_by_xml_id(
        env, ["sale_purchase.constraint_product_template_service_to_purchase"]
    )
