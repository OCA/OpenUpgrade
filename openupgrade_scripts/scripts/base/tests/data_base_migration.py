env = locals().get("env")
base_test_model = env["ir.model"].create(
    {
        "name": "v19_base_test_model",
        "model": "x_v19_base_test_model",
    }
)
env["ir.model.access"].create(
    {
        "name": "allow read for all",
        "model_id": base_test_model.id,
        "perm_read": True,
    }
)
env["ir.model.access"].create(
    {
        "name": "allow u for portal user",
        "model_id": base_test_model.id,
        "group_id": env.ref("base.group_portal").id,
        "perm_write": True,
    }
)
env["ir.model.access"].create(
    {
        "name": "allow cu for backend user",
        "model_id": base_test_model.id,
        "group_id": env.ref("base.group_user").id,
        "perm_write": True,
        "perm_create": True,
    }
)
env["ir.model.access"].create(
    {
        "name": "allow d for admin",
        "model_id": base_test_model.id,
        "group_id": env.ref("base.group_system").id,
        "perm_unlink": True,
    }
)
env["ir.rule"].create(
    {
        "name": "restrict user group to own records",
        "model_id": base_test_model.id,
        "groups": [(6, 0, env.ref("base.group_user").ids)],
        "domain_force": "[('create_uid', '=', user.id)]",
    }
)
env["ir.rule"].create(
    {
        "name": "lift update restrictions for admin",
        "model_id": base_test_model.id,
        "groups": [(6, 0, env.ref("base.group_erp_manager").ids)],
        "domain_force": "[(1, '=', 1)]",
        "perm_create": False,
        "perm_read": False,
        "perm_write": True,
        "perm_unlink": False,
    }
)
env["ir.rule"].create(
    {
        "name": "lift delete/update restrictions for system",
        "model_id": base_test_model.id,
        "groups": [(6, 0, env.ref("base.group_system").ids)],
        "domain_force": "[(1, '=', 1)]",
        "perm_create": False,
        "perm_read": False,
        "perm_write": True,
        "perm_unlink": True,
    }
)
env["ir.rule"].create(
    {
        "name": "restrict portal group to own records",
        "model_id": base_test_model.id,
        "groups": [(6, 0, env.ref("base.group_portal").ids)],
        "domain_force": "[('create_uid', '=', user.id)]",
    }
)
env["ir.rule"].create(
    {
        "name": "restrict deleting to own records for all",
        "model_id": base_test_model.id,
        "perm_create": False,
        "perm_read": False,
        "perm_write": False,
        "perm_unlink": True,
        "domain_force": "[('create_uid', '=', user.id)]",
    }
)
rule_with_faulty_domain = env["ir.rule"].create(
    {
        "name": "rule with faulty domain",
        "model_id": base_test_model.id,
        "domain_force": "[('create_uid2', '=', user.id)]",
        "perm_create": False,
        "perm_read": False,
        "perm_write": False,
        "perm_unlink": True,
        "active": False,
    }
)
base_test_model2 = env["ir.model"].create(
    {
        "name": "v19_base_test_model2",
        "model": "x_v19_base_test_model2",
    }
)
env["ir.model.access"].create(
    {
        "name": "allow read for all",
        "model_id": base_test_model2.id,
        "perm_read": True,
    }
)
env.cr.execute(
    "UPDATE ir_rule SET active=TRUE WHERE id=%s", (rule_with_faulty_domain.id,)
)
env["ir.actions.client"].create(
    {
        "name": "Test action for params_store",
        "params": {"some": "value"},
        "tag": "some.tag",
    }
)
test_user = env["res.users"].create(
    {
        "name": "test user",
        "login": "test_user_v19",
    }
)
env.cr.commit()
