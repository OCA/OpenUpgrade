from openupgradelib import openupgrade


def convert_assets(env):
    for asset in env["ir.asset"].search([("path", "like", ".custom.")]):
        path_1, extra = asset.path.split(".custom.", 1)
        bundle_1, bundle_2, path_2 = extra.split(".", 2)
        path = f"{path_1}.{path_2}"
        bundle = f"{bundle_1}.{bundle_2}"
        new_path = f"/_custom/{bundle}{path}"
        env["ir.attachment"].search([("url", "=", asset.path)]).write({"url": new_path})
        asset.write({"path": new_path})


@openupgrade.migrate()
def migrate(env, version):
    convert_assets(env)
