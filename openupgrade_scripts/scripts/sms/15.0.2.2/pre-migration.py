from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [
            (
                "sms.sms",
                "sms_sms",
                "error_code",
                "failure_type",
            )
        ],
    )
