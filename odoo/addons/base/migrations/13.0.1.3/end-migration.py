# © 2020 Opener B.V. (stefan@opener.amsterdam)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def delete_obsolete_model_relations(env):
    # solves https://github.com/OCA/OpenUpgrade/issues/2985
    env.cr.execute("SELECT id FROM ir_model;")
    all_model_ids = [x[0] for x in env.cr.fetchall()]
    correct_models_ids = env["ir.model"].search(
        [("model", "in", list(env.registry.models.keys()))]).ids
    wrong_model_ids = list(set(all_model_ids) - set(correct_models_ids))
    if wrong_model_ids:
        openupgrade.logged_query(
            env.cr,
            """
            DELETE FROM ir_model_relation
            WHERE model IN %s""", (tuple(wrong_model_ids),))


def fix_translation_terms(env):
    """There is an unresolved bug in versions <=12 (probably coming from web_editor)
    that causes wrong translation states. This causes crashes when those terms
    get edited in v13. We also want to normalize states to the expected ones when
    they are null."""
    openupgrade.logged_query(
        env.cr,
        "UPDATE ir_translation SET state = NULL WHERE state = 'false'"
    )
    openupgrade.logged_query(
        env.cr,
        "UPDATE ir_translation SET state = 'translated' "
        "WHERE state IS NULL and value IS NOT NULL"
    )
    openupgrade.logged_query(
        env.cr,
        "UPDATE ir_translation SET state = 'to_translate' "
        "WHERE state IS NULL and value IS NULL"
    )


@openupgrade.migrate()
def migrate(env, version):
    """ Call disable_invalid_filters in every edition of openupgrade """
    openupgrade.disable_invalid_filters(env)
    delete_obsolete_model_relations(env)
    fix_translation_terms(env)
