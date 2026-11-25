from odoo import fields

env = locals().get("env")
# set company_registry in v15 to be sure we migrate it correctly to v16
env.ref("base.main_company").company_registry = "424242"

# translated name and help of a user-created scheduled action: ir.actions.*
# translations are excluded from the generic pre-migration update, the base
# post-migration must merge them
action = env["ir.actions.server"].create(
    {
        "name": "OpenUpgrade Test Action",
        "help": "<p>OpenUpgrade action help</p>",
        "model_id": env.ref("base.model_res_partner").id,
        "state": "code",
        "code": "pass",
    }
)
env["ir.cron"].create(
    {
        "ir_actions_server_id": action.id,
        "cron_name": "OpenUpgrade Test Action",
        "user_id": env.uid,
        "interval_number": 1,
        "interval_type": "months",
        "nextcall": fields.Datetime.now(),
    }
)
action.with_context(lang="fr_FR").write({"name": "Action de test OpenUpgrade"})
# the html help is translated term by term, as in v15 for callable translations
env["ir.translation"].create(
    {
        "type": "model_terms",
        "name": "ir.actions.server,help",
        "res_id": action.id,
        "lang": "fr_FR",
        "src": "OpenUpgrade action help",
        "value": "Aide OpenUpgrade",
        "state": "translated",
    }
)
env.cr.commit()
