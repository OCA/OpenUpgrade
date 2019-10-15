# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def keep_old_data_fleet_vehicle_model(cr):
    openupgrade.logged_query(
        cr, """
            DELETE FROM ir_model_data
            WHERE module = 'fleet'
                  AND model = 'fleet.vehicle.model'
                  AND name in (
                     'model_a1',
                     'model_a3',
                     'model_a4',
                     'model_a5',
                     'model_a6',
                     'model_a7',
                     'model_a8',
                     'model_agila',
                     'model_ampera',
                     'model_antara',
                     'model_astra',
                     'model_astragtc',
                     'model_classa',
                     'model_classb',
                     'model_classc',
                     'model_classcl',
                     'model_classcls',
                     'model_classe',
                     'model_classgl',
                     'model_classglk',
                     'model_classm',
                     'model_classr',
                     'model_classs',
                     'model_classslk',
                     'model_classsls',
                     'model_combotour',
                     'model_corsa',
                     'model_insignia',
                     'model_meriva',
                     'model_mokka',
                     'model_q3',
                     'model_q5',
                     'model_q7',
                     'model_serie1',
                     'model_serie3',
                     'model_serie5',
                     'model_serie6',
                     'model_serie7',
                     'model_seriehybrid',
                     'model_seriem',
                     'model_seriex',
                     'model_seriez4',
                     'model_tt',
                     'model_zafira',
                     'model_zafiratourer'
            )
        """
    )


def keep_old_data_fleet_service_type(cr):
    openupgrade.logged_query(
        cr, """
            DELETE FROM ir_model_data
            WHERE module = 'fleet'
                  AND model = 'fleet.service.type'
                  AND name in (
                     'type_contract_leasing',
                     'type_contract_omnium',
                     'type_contract_repairing',
                     'type_service_1',
                     'type_service_10',
                     'type_service_11',
                     'type_service_12',
                     'type_service_13',
                     'type_service_14',
                     'type_service_15',
                     'type_service_16',
                     'type_service_17',
                     'type_service_18',
                     'type_service_19',
                     'type_service_2',
                     'type_service_20',
                     'type_service_21',
                     'type_service_22',
                     'type_service_23',
                     'type_service_24',
                     'type_service_25',
                     'type_service_26',
                     'type_service_27',
                     'type_service_28',
                     'type_service_29',
                     'type_service_3',
                     'type_service_30',
                     'type_service_31',
                     'type_service_32',
                     'type_service_33',
                     'type_service_34',
                     'type_service_35',
                     'type_service_36',
                     'type_service_37',
                     'type_service_38',
                     'type_service_39',
                     'type_service_4',
                     'type_service_40',
                     'type_service_41',
                     'type_service_42',
                     'type_service_43',
                     'type_service_44',
                     'type_service_45',
                     'type_service_46',
                     'type_service_47',
                     'type_service_48',
                     'type_service_49',
                     'type_service_5',
                     'type_service_50',
                     'type_service_51',
                     'type_service_52',
                     'type_service_53',
                     'type_service_6',
                     'type_service_7',
                     'type_service_8',
                     'type_service_9',
                     'type_service_refueling',
                     'type_service_service_1',
                     'type_service_service_10',
                     'type_service_service_11',
                     'type_service_service_12',
                     'type_service_service_13',
                     'type_service_service_14',
                     'type_service_service_15',
                     'type_service_service_16',
                     'type_service_service_17',
                     'type_service_service_18',
                     'type_service_service_19',
                     'type_service_service_2',
                     'type_service_service_3',
                     'type_service_service_5',
                     'type_service_service_6',
                     'type_service_service_7',
                     'type_service_service_8',
                     'type_service_service_9'
            )
        """
    )


def keep_old_data_fleet_vehicle_tag(cr):
    openupgrade.logged_query(
        cr, """
            DELETE FROM ir_model_data
            WHERE module = 'fleet'
                  AND model = 'fleet.vehicle.tag'
                  AND name in (
                     'vehicle_tag_break',
                     'vehicle_tag_compact',
                     'vehicle_tag_convertible',
                     'vehicle_tag_junior',
                     'vehicle_tag_leasing',
                     'vehicle_tag_purchased',
                     'vehicle_tag_sedan',
                     'vehicle_tag_senior'
            )
        """
    )


@openupgrade.migrate()
def migrate(env, _):
    cr = env.cr
    keep_old_data_fleet_vehicle_model(cr)
    keep_old_data_fleet_service_type(cr)
    keep_old_data_fleet_vehicle_tag(cr)
    openupgrade.set_xml_ids_noupdate_value(
        env, 'fleet', ['ir_cron_contract_costs_generator'], True)
