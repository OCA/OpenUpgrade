# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openupgradelib import openupgrade, openupgrade_merge_records

_logger = logging.getLogger(__name__)


def harmonize_groups(env):
    """Unfold manual groups per company + proper company assignation"""

    # step 1: Generate the generic account groups for each company. Later code will
    # do it for manually created groups

    companies = env["res.company"].with_context(active_test=False).search([])
    for company in companies.filtered("chart_template_id"):
        company.chart_template_id.generate_account_groups(company)

    # step 2: For manually created groups, we check if such group is used in more than
    # one company. If so, we unfold it. We also assure proper company for existing one

    def _get_all_children(groups):
        children = env["account.group"].search([("parent_id", "in", groups.ids)])
        if children:
            children |= _get_all_children(children)
        return children

    def _get_all_parents(groups):
        parents = groups.mapped("parent_id")
        if parents:
            parents |= _get_all_parents(parents)
        return parents

    AccountGroup = env["account.group"]
    AccountGroup._parent_store_compute()
    env.cr.execute(
        """SELECT ag.id FROM account_group ag
        LEFT JOIN ir_model_data imd
            ON ag.id = imd.res_id AND imd.model = 'account.group'
                AND imd.module != '__export__'
        WHERE imd.id IS NULL"""
    )
    all_groups = AccountGroup.browse([x[0] for x in env.cr.fetchall()])
    all_groups = all_groups | _get_all_parents(all_groups)
    relation_dict = {}
    for group in all_groups.sorted(key="parent_path"):
        subgroups = group | _get_all_children(group)
        accounts = env["account.account"].search([("group_id", "in", subgroups.ids)])
        companies = accounts.mapped("company_id").sorted()
        for i, company in enumerate(companies):
            if company not in relation_dict:
                relation_dict[company] = {}
            if i == 0:
                if group.company_id != company:
                    group.company_id = company.id
                relation_dict[company][group] = group
                continue
            # Done by SQL for avoiding ORM derived problems
            env.cr.execute(
                """INSERT INTO account_group (parent_id, parent_path, name,
                code_prefix_start, code_prefix_end, company_id,
                create_uid, write_uid, create_date, write_date)
            SELECT {parent_id}, parent_path, name, code_prefix_start,
                code_prefix_end, {company_id}, create_uid,
                write_uid, create_date, write_date
            FROM account_group
            WHERE id = {id}
            RETURNING id
            """.format(
                    id=group.id,
                    company_id=company.id,
                    parent_id=group.parent_id
                    and relation_dict[company][group.parent_id].id
                    or "NULL",
                )
            )
            new_group = AccountGroup.browse(env.cr.fetchone())
            relation_dict[company][group] = new_group

    # step 3: Merge repeated groups

    env.cr.execute(
        """SELECT array_agg(id order by id DESC), name,
            code_prefix_start, company_id
        FROM account_group
        GROUP BY name, code_prefix_start, company_id
        """
    )
    group_ids = [x[0] for x in env.cr.fetchall()]
    for group in group_ids:
        if len(group) > 1:
            openupgrade_merge_records.merge_records(
                env,
                "account.group",
                group[1:],
                group[0],
                field_spec=None,
                method="sql",
                delete=True,
                exclude_columns=None,
                model_table="account_group",
            )

    AccountGroup._parent_store_compute()


@openupgrade.migrate()
def migrate(env, version):
    harmonize_groups(env)
    # Launch a recomputation of the account groups after previous changes
    env["account.account"].search([])._compute_account_group()
