import html
import re

from bs4 import BeautifulSoup
from openupgradelib import openupgrade

_PY_VAR_PATTERN = "[a-zA-Z_][a-zA-Z0-9_]*"


def _map_activity_type_chaining_type_field(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("force_next"),
        "chaining_type",
        [("true", "trigger"), ("false", "suggest")],
        table="mail_activity_type",
    )


def _map_activity_type_res_model_field(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE mail_activity_type
        SET res_model = ir_model.model
        FROM ir_model
        WHERE mail_activity_type.%s = ir_model.id
        """
        % openupgrade.get_legacy_name("res_model_id"),
    )


def _map_mail_notification_failure_type(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("failure_type"),
        "failure_type",
        [
            ("SMTP", "mail_smtp"),
            ("BOUNCE", "mail_email_invalid"),
            ("RECIPIENT", "mail_email_invalid"),
            ("UNKNOWN", "unknown"),
        ],
        table="mail_notification",
    )


def finish_migration_to_mail_group(env):
    env.cr.execute(
        """
        SELECT 1 FROM ir_module_module
        WHERE name = 'mail_group' AND state = 'to install'""",
    )
    will_have_mail_group = env.cr.rowcount
    if not will_have_mail_group:
        return
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM ir_attachment ia
        USING mail_channel mc
        WHERE ia.res_model = 'mail.channel' AND ia.res_id = mc.id
            AND mc.email_send AND ia.res_field = 'image_128'""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        DELETE FROM mail_channel
        WHERE email_send""",
    )


def _migrate_placeholder_char(string):
    """
    Replace dynamic placeholders in char/text fields:
    Example: "Dear ${object.name}," -> "Dear {{object.name}},"
    """
    if not string:
        return string
    pattern = r"\$\{([^}]*)\}"
    repl = r"{{\1}}"
    return re.sub(pattern, repl, string)


def _migrate_placeholder_html(string):
    """
    Replace dynamic placeholders in HTML fields:
    Example: 'Your name is ${object.name}' -> 'Your name is <t t-out="object.name"></t>'
    """
    pattern = r"\$\{([^}]*)\}"

    def repl(match):
        (expression,) = match.groups()
        expression = html.escape(expression)
        return f'<t t-out="{expression}"></t>'

    return re.sub(pattern, repl, string)


def _migrate_end(string):
    pattern = r"^%\s+end(if|for)\s*$"
    repl = r"</t>"
    return re.sub(pattern, repl, string, flags=re.MULTILINE)


def _migrate_else(string):
    pattern = r"^%\s+else\s*:?\s*$"
    repl = r'<t t-else="">'
    return re.sub(pattern, repl, string, flags=re.MULTILINE)


def _migrate_if(string):
    pattern = r"^%\s+if\s+(.+?)\s*:?\s*$"

    def repl(match):
        (if_expression,) = match.groups()
        if_expression = html.escape(if_expression)
        return f'<t t-if="{if_expression}">'

    return re.sub(pattern, repl, string, flags=re.MULTILINE)


def _migrate_for(string):
    pattern = rf"^%\s+for\s+({_PY_VAR_PATTERN})\s+in\s+(.+?)\s*:?\s*$"

    def repl(match):
        var_name, loop_expression = match.groups()
        loop_expression = html.escape(loop_expression)
        return f'<t t-foreach="{loop_expression}" t-as="{var_name}">'

    return re.sub(pattern, repl, string, flags=re.MULTILINE)


def _migrate_set(string):
    pattern = rf"^%\s+set\s+({_PY_VAR_PATTERN})\s*=\s*(.+?)\s*$"

    def repl(match):
        var_name, var_value = match.groups()
        var_value = html.escape(var_value)
        return f'<t t-set="{var_name}" t-value="{var_value}"/>'

    return re.sub(pattern, repl, string, flags=re.MULTILINE)


def _migrate_html_attributes(string):
    soup = BeautifulSoup(string, multi_valued_attributes=None, features="html.parser")
    # replace placeholders in attributes
    for element in soup.find_all():
        new_attrs = {}
        for attr_name, attr_value in element.attrs.items():
            new_attr_value = _migrate_placeholder_char(attr_value)
            if new_attr_value != attr_value:
                new_attrs[f"t-attf-{attr_name}"] = new_attr_value
            else:
                new_attrs[attr_name] = attr_value
        element.attrs = new_attrs
    return str(soup)


def mako_html_to_qweb(string):
    if not string:
        return string
    return _migrate_set(
        _migrate_end(
            _migrate_else(
                _migrate_for(
                    _migrate_if(
                        _migrate_placeholder_html(
                            _migrate_html_attributes(string),
                        )
                    )
                )
            )
        )
    )


def _migrate_mail_templates(env):
    """
    Migrate all mail templates from jinja2 to qweb
    """
    templates = env["mail.template"].with_context(active_test=False).search([])
    for template in templates:
        template.email_from = _migrate_placeholder_char(template.email_from)
        template.email_to = _migrate_placeholder_char(template.email_to)
        template.reply_to = _migrate_placeholder_char(template.reply_to)
        for lang in env["res.lang"].search([]).mapped("code"):
            template.with_context(lang=lang).subject = _migrate_placeholder_char(
                template.with_context(lang=lang).subject
            )
            template.with_context(lang=lang).body_html = mako_html_to_qweb(
                template.with_context(lang=lang).body_html
            )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "mail", "15.0.1.5/noupdate_changes.xml")
    _map_activity_type_chaining_type_field(env)
    _map_activity_type_res_model_field(env)
    _map_mail_notification_failure_type(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "mail.mail_moderation_rule_user",
            "mail.ir_cron_mail_notify_channel_moderators",
        ],
    )
    finish_migration_to_mail_group(env)
    _migrate_mail_templates(env)
