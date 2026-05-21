from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Null ``path`` on the todo action, as the schema upgrade pre-populates
    it and the module data XML then trips the unique constraint on its own
    row.
    """
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_act_window
           SET path = NULL
         WHERE path = 'to-do'
        """,
    )
