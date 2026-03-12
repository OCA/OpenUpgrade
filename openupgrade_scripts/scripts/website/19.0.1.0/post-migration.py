from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_rule
        SET domain_force = '["|", ("group_ids", "=", False), ("group_ids", "in", user.all_group_ids.ids)]'
        WHERE id IN (
            SELECT res_id 
            FROM ir_model_data 
            WHERE model = 'ir.rule' 
              AND module = 'website' 
              AND name = 'website_menu'
        )
        """
    )