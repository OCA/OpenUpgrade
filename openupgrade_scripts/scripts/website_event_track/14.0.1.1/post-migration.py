from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "website_event_track", "14.0.1.1/noupdate_changes.xml"
    )

    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["website_event_track.event_type_data_tracks"],
    )

    openupgrade.delete_record_translations(
        env.cr,
        "website_event_track",
        [
            "mail_template_data_track_confirmation",
        ],
    )
