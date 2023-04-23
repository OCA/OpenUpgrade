from lxml import etree
from openupgradelib import openupgrade


def deprecate_website_crm_privacy_policy(env):
    module_website_crm_privacy_policy = env["ir.module.module"].search(
        [("name", "=", "website_crm_privacy_policy")]
    )
    if module_website_crm_privacy_policy.state in ("installed", "to upgrade"):
        module_website_form_require_legal = env["ir.module.module"].search(
            [("name", "=", "website_form_require_legal")]
        )
        module_website_crm_privacy_policy.state = "to remove"
        module_website_form_require_legal.state = "to install"
        # Remove possible remnants of the old view and add the new checkbox
        views = env["ir.ui.view"].search([("key", "=", "website_crm.contactus_form")])
        new_checkbox_form = etree.fromstring(
            """
        <div
            class="col-12 s_website_form_legal form-group
                s_website_form_field s_website_form_required s_website_form_custom"
            data-name="Legal Terms">
            <div class="row s_col_no_resize s_col_no_bgcolor">
                <div style="width: 200px" class="s_website_form_label"/>
                <div class="col-sm">
                    <div class="form-check">
                        <input type="checkbox" required="1"
                            class="s_website_form_input form-check-input"/>
                        <span class="form-check-label">
                            Agree to <a href="#">terms and conditions</a>
                        </span>
                        <div class="invalid-feedback">
                            You must agree before submitting.
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        )
        for view in views:
            arch_tree = etree.fromstring(view.arch)
            div_checkbox = arch_tree.xpath("//input[@id='privacy_policy']/../../..")
            if div_checkbox:
                div_checkbox[0].getparent().remove(div_checkbox[0])
            div_button_send = arch_tree.xpath(
                "//a[hasclass('o_website_form_send')]/../.."
            )
            if div_button_send:
                div_button_send[0].addprevious(new_checkbox_form)
            view.write({"arch": etree.tostring(arch_tree, encoding="unicode")})


@openupgrade.migrate()
def migrate(env, version):
    deprecate_website_crm_privacy_policy(env)
