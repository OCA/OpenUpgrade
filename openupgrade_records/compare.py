# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2015-2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# flake8: noqa: C901
#####################################################################
#   library providing a function to analyse two progressive database
#   layouts from the OpenUpgrade server.
#####################################################################

import collections
import copy

from . import apriori


def module_map(module):
    return apriori.renamed_modules.get(
        module, apriori.merged_modules.get(module, module)
    )


def model_rename_map(model):
    return apriori.renamed_models.get(model, model)


def model_map(model):
    return apriori.renamed_models.get(model, apriori.merged_models.get(model, model))


def inv_model_map(model):
    inv_model_map_dict = {v: k for k, v in apriori.renamed_models.items()}
    return inv_model_map_dict.get(model, model)


IGNORE_FIELDS = [
    "create_date",
    "create_uid",
    "id",
    "write_date",
    "write_uid",
]


def compare_records(dict_old, dict_new, fields):
    """
    Check equivalence of two OpenUpgrade field representations
    with respect to the keys in the 'fields' arguments.
    Take apriori knowledge into account for mapped modules or
    model names.
    Return True of False.
    """
    for field in fields:
        if field == "module":
            if module_map(dict_old["module"]) != dict_new["module"]:
                return False
        elif field == "model":
            if model_rename_map(dict_old["model"]) != dict_new["model"]:
                return False
        elif field == "other_prefix":
            if (
                dict_old["module"] != dict_old["prefix"]
                or dict_new["module"] != dict_new["prefix"]
            ):
                return False
            if dict_old["model"] == "ir.ui.view":
                # basically, to avoid the assets_backend case
                return False
        elif dict_old[field] != dict_new[field]:
            return False
    return True


def search(item, item_list, fields):
    """
    Find a match of a dictionary in a list of similar dictionaries
    with respect to the keys in the 'fields' arguments.
    Return the item if found or None.
    """
    for other in item_list:
        if not compare_records(item, other, fields):
            continue
        return other
    # search for renamed fields
    if "field" in fields:
        for other in item_list:
            if not item["field"] or item["field"] is not None or item["isproperty"]:
                continue
            if compare_records(dict(item, field=other["field"]), other, fields):
                return other
    return None


def fieldprint(old, new, field, text, reprs):
    fieldrepr = "{} ({})".format(old["field"], old["type"])
    fullrepr = "{:<12} / {:<24} / {:<30}".format(old["module"], old["model"], fieldrepr)
    if not text:
        text = "{} is now '{}' ('{}')".format(field, new[field], old[field])
        if field == "relation":
            text += " [nothing to do]"
    reprs[module_map(old["module"])].append("{}: {}".format(fullrepr, text))
    if field == "module":
        text = "previously in module %s" % old[field]
        fullrepr = "{:<12} / {:<24} / {:<30}".format(
            new["module"], old["model"], fieldrepr
        )
        reprs[module_map(new["module"])].append("{}: {}".format(fullrepr, text))


def report_generic(new, old, attrs, reprs):
    for attr in attrs:
        if attr == "required":
            if old[attr] != new["required"] and new["required"]:
                text = "now required"
                if new["req_default"]:
                    text += ", req_default: %s" % new["req_default"]
                fieldprint(old, new, "", text, reprs)
        elif attr == "stored":
            if old[attr] != new[attr]:
                if new["stored"]:
                    text = "is now stored"
                else:
                    text = "not stored anymore"
                fieldprint(old, new, "", text, reprs)
        elif attr == "isfunction":
            if old[attr] != new[attr]:
                if new["isfunction"]:
                    text = "now a function"
                else:
                    text = "not a function anymore"
                fieldprint(old, new, "", text, reprs)
        elif attr == "isproperty":
            if old[attr] != new[attr]:
                if new[attr]:
                    text = "now a property"
                else:
                    text = "not a property anymore"
                fieldprint(old, new, "", text, reprs)
        elif attr == "isrelated":
            if old[attr] != new[attr]:
                if new[attr]:
                    text = "now related"
                else:
                    text = "not related anymore"
                fieldprint(old, new, "", text, reprs)
        elif old[attr] != new[attr]:
            fieldprint(old, new, attr, "", reprs)


def compare_sets(old_records, new_records):
    """
    Compare a set of OpenUpgrade field representations.
    Try to match the equivalent fields in both sets.
    Return a textual representation of changes in a dictionary with
    module names as keys. Special case is the 'general' key
    which contains overall remarks and matching statistics.
    """
    reprs = collections.defaultdict(list)

    def clean_records(records):
        result = []
        for record in records:
            if record["field"] not in IGNORE_FIELDS:
                result.append(record)
        return result

    old_records = clean_records(old_records)
    new_records = clean_records(new_records)

    origlen = len(old_records)
    new_models = {column["model"] for column in new_records}
    old_models = {column["model"] for column in old_records}

    matched_direct = 0
    matched_other_module = 0
    matched_other_type = 0
    in_obsolete_models = 0

    obsolete_models = []
    for model in old_models:
        if model not in new_models:
            if model_map(model) not in new_models:
                obsolete_models.append(model)

    non_obsolete_old_records = []
    for column in copy.copy(old_records):
        if column["model"] in obsolete_models:
            in_obsolete_models += 1
        else:
            non_obsolete_old_records.append(column)

    def match(match_fields, report_fields, warn=False):
        count = 0
        for column in copy.copy(non_obsolete_old_records):
            found = search(column, new_records, match_fields)
            if found:
                if warn:
                    pass
                    # print "Tentatively"
                report_generic(found, column, report_fields, reprs)
                old_records.remove(column)
                non_obsolete_old_records.remove(column)
                new_records.remove(found)
                count += 1
        return count

    matched_direct = match(
        ["module", "mode", "model", "field"],
        [
            "relation",
            "type",
            "selection_keys",
            "inherits",
            "stored",
            "isfunction",
            "isrelated",
            "required",
            "table",
        ],
    )

    # other module, same type and operation
    matched_other_module = match(
        ["mode", "model", "field", "type"],
        [
            "module",
            "relation",
            "selection_keys",
            "inherits",
            "stored",
            "isfunction",
            "isrelated",
            "required",
            "table",
        ],
    )

    # other module, same operation, other type
    matched_other_type = match(
        ["mode", "model", "field"],
        [
            "relation",
            "type",
            "selection_keys",
            "inherits",
            "stored",
            "isfunction",
            "isrelated",
            "required",
            "table",
        ],
    )

    printkeys = [
        "relation",
        "required",
        "selection_keys",
        "req_default",
        "inherits",
        "mode",
        "attachment",
    ]
    for column in old_records:
        # we do not care about removed non stored function fields
        if not column["stored"] and (column["isfunction"] or column["isrelated"]):
            continue
        if column["mode"] == "create":
            column["mode"] = ""
        extra_message = ", ".join(
            [
                k + ": " + str(column[k]) if k != str(column[k]) else k
                for k in printkeys
                if column[k]
            ]
        )
        if extra_message:
            extra_message = " " + extra_message
        fieldprint(column, "", "", "DEL" + extra_message, reprs)

    printkeys.extend(
        [
            "hasdefault",
        ]
    )
    for column in new_records:
        # we do not care about newly added non stored function fields
        if not column["stored"] and (column["isfunction"] or column["isrelated"]):
            continue
        if column["mode"] == "create":
            column["mode"] = ""
        printkeys_plus = printkeys.copy()
        if column["isfunction"] or column["isrelated"]:
            printkeys_plus.extend(["isfunction", "isrelated", "stored"])
        extra_message = ", ".join(
            [
                k + ": " + str(column[k]) if k != str(column[k]) else k
                for k in printkeys_plus
                if column[k]
            ]
        )
        if extra_message:
            extra_message = " " + extra_message
        fieldprint(column, "", "", "NEW" + extra_message, reprs)

    for line in [
        "# %d fields matched," % (origlen - len(old_records)),
        "# Direct match: %d" % matched_direct,
        "# Found in other module: %d" % matched_other_module,
        "# Found with different type: %d" % matched_other_type,
        "# In obsolete models: %d" % in_obsolete_models,
        "# Not matched: %d" % len(old_records),
        "# New columns: %d" % len(new_records),
    ]:
        reprs["general"].append(line)
    return reprs


def compare_xml_sets(old_records, new_records):
    reprs = collections.defaultdict(list)

    def match(match_fields, match_type="direct"):
        matched_records = []
        for column in copy.copy(old_records):
            found = search(column, new_records, match_fields)
            if found:
                old_records.remove(column)
                new_records.remove(found)
                if match_type != "direct":
                    column["old"] = True
                    found["new"] = True
                    column[match_type] = found["module"]
                    found[match_type] = column["module"]
                found["domain"] = (
                    column["domain"] != found["domain"]
                    and column["domain"] != "[]"
                    and found["domain"] is False
                )
                column["domain"] = False
                column["noupdate_switched"] = False
                found["noupdate_switched"] = column["noupdate"] != found["noupdate"]
                if match_type != "direct":
                    matched_records.append(column)
                    matched_records.append(found)
                elif (match_type == "direct" and found["domain"]) or found[
                    "noupdate_switched"
                ]:
                    matched_records.append(found)
        return matched_records

    # direct match
    modified_records = match(["module", "model", "name"])

    # other module, same full xmlid
    moved_records = match(["model", "name"], "moved")

    # other module, same suffix, other prefix
    renamed_records = match(["model", "suffix", "other_prefix"], "renamed")

    for record in old_records:
        record["old"] = True
        record["domain"] = False
        record["noupdate_switched"] = False
    for record in new_records:
        record["new"] = True
        record["domain"] = False
        record["noupdate_switched"] = False

    sorted_records = sorted(
        old_records + new_records + moved_records + renamed_records + modified_records,
        key=lambda k: (k["model"], "old" in k, k["name"]),
    )
    for entry in sorted_records:
        content = ""
        if "old" in entry:
            content = "DEL %(model)s: %(name)s" % entry
            if "moved" in entry:
                content += " [potentially moved to %(moved)s module]" % entry
            elif "renamed" in entry:
                content += " [renamed to %(renamed)s module]" % entry
        elif "new" in entry:
            content = "NEW %(model)s: %(name)s" % entry
            if "moved" in entry:
                content += " [potentially moved from %(moved)s module]" % entry
            elif "renamed" in entry:
                content += " [renamed from %(renamed)s module]" % entry
        if "old" not in entry and "new" not in entry:
            content = "%(model)s: %(name)s" % entry
        if entry["domain"]:
            content += " (deleted domain)"
        if entry["noupdate"]:
            content += " (noupdate)"
        if entry["noupdate_switched"]:
            content += " (noupdate switched)"
        reprs[module_map(entry["module"])].append(content)
    return reprs


def compare_model_sets(old_records, new_records):
    """
    Compare a set of OpenUpgrade model representations.
    """
    reprs = collections.defaultdict(list)

    new_models = {column["model"]: column["module"] for column in new_records}
    old_models = {column["model"]: column["module"] for column in old_records}

    obsolete_models = []
    for column in copy.copy(old_records):
        model = column["model"]
        if model in old_models:
            if model not in new_models:
                if model_map(model) not in new_models:
                    obsolete_models.append(model)
                    text = "obsolete model %s" % model
                    if column["model_type"]:
                        text += " [%s]" % column["model_type"]
                    reprs[module_map(column["module"])].append(text)
                    reprs["general"].append(
                        "obsolete model %s [module %s]"
                        % (model, module_map(column["module"]))
                    )
                else:
                    moved_module = ""
                    if module_map(column["module"]) != new_models[model_map(model)]:
                        moved_module = " in module %s" % new_models[model_map(model)]
                    text = "obsolete model {} (renamed to {}{})".format(
                        model,
                        model_map(model),
                        moved_module,
                    )
                    if column["model_type"]:
                        text += " [%s]" % column["model_type"]
                    reprs[module_map(column["module"])].append(text)
                    reprs["general"].append(
                        "obsolete model %s (renamed to %s) [module %s]"
                        % (model, model_map(model), module_map(column["module"]))
                    )
            else:
                if module_map(column["module"]) != new_models[model]:
                    text = "model {} (moved to {})".format(model, new_models[model])
                    if column["model_type"]:
                        text += " [%s]" % column["model_type"]
                    reprs[module_map(column["module"])].append(text)
                    text = "model {} (moved from {})".format(model, old_models[model])
                    if column["model_type"]:
                        text += " [%s]" % column["model_type"]

    for column in copy.copy(new_records):
        model = column["model"]
        if model in new_models:
            if model not in old_models:
                if inv_model_map(model) not in old_models:
                    text = "new model %s" % model
                    if column["model_type"]:
                        text += " [%s]" % column["model_type"]
                    reprs[column["module"]].append(text)
                    reprs["general"].append(
                        "new model {} [module {}]".format(model, column["module"])
                    )
                else:
                    moved_module = ""
                    if column["module"] != module_map(old_models[inv_model_map(model)]):
                        moved_module = (
                            " in module %s" % old_models[inv_model_map(model)]
                        )
                    text = "new model {} (renamed from {}{})".format(
                        model,
                        inv_model_map(model),
                        moved_module,
                    )
                    if column["model_type"]:
                        text += " [%s]" % column["model_type"]
                    reprs[column["module"]].append(text)
                    reprs["general"].append(
                        "new model %s (renamed from %s) [module %s]"
                        % (model, inv_model_map(model), column["module"])
                    )
            else:
                if column["module"] != module_map(old_models[model]):
                    text = "model {} (moved from {})".format(model, old_models[model])
                    if column["model_type"]:
                        text += " [%s]" % column["model_type"]
                    reprs[column["module"]].append(text)
    return reprs
