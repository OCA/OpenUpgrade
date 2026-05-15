from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Reset "lang" field for these records, as they were set in previous
    version in XML, but not in this one, and Odoo doesn't reset non present
    fields.
    """
    for xmlid in ("mail_template_gift_card", "mail_template_loyalty_card"):
        template = env.ref(f"loyalty.{xmlid}", False)
        if template:
            template.lang = False
