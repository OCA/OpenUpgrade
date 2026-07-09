from openupgradelib import openupgrade


def fix_template_lang(env):
    """Reset "lang" field for these records, as they were set in previous
    version in XML, but not in this one, and Odoo doesn't reset non present
    fields.
    The templates are not marked as noupdate, so this change is not caught by
    upgrade_analysis
    """
    env.cr.execute(
        """
        UPDATE mail_template
        SET lang=NULL
        FROM
        ir_model_data imd
        WHERE
        imd.module='loyalty' and imd.name in (
            'mail_template_gift_card',
            'mail_template_loyalty_card'
        )
        and mail_template.id=imd.res_id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    fix_template_lang(env)
