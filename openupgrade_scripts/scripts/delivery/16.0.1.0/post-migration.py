# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import string
from inspect import cleandoc

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

ALPHANUM = string.digits + string.ascii_uppercase


def increment_alphanum(value):
    result = []
    carry = False
    first = True
    for digit in reversed(value):
        # Preserve spaces and hyphens
        if digit in [" ", "-"]:
            result.append(digit)
        elif digit == "Z" and (first or carry):
            result.append("0")
            carry = True
        elif carry or first:
            result.append(ALPHANUM[ALPHANUM.index(digit) + 1])
            carry = False
        else:
            result.append(digit)
        first = False
    if carry:
        result.append("1")
    return "".join(result[::-1])


def fill_prefix(prefix, length, item, spaces, dashes):
    result = prefix + (length * item)
    for index in spaces:
        result = result[:index] + " " + result[index + 1 :]
    for index in dashes:
        result = result[:index] + "-" + result[index + 1 :]
    return result


def prefix_works(prefix, start, end, spaces, dashes):
    # Get the highest and lowest values for the prefix, and compare them against
    # the two extremes.
    fill_length = len(start) - len(prefix)
    highest = fill_prefix(prefix, fill_length, "Z", spaces, dashes)
    lowest = fill_prefix(prefix, fill_length, "0", spaces, dashes)
    return lowest >= start and highest <= end


def next_alphanum(prefix, length, end, spaces, dashes):
    result = increment_alphanum(prefix)
    fill_length = length - len(prefix)
    if fill_length:
        result = fill_prefix(result, length - len(prefix), "0", spaces, dashes)
    if result > end:
        return None
    return result


def find_occurrences(item, iterable):
    return [i for i, val in enumerate(iterable) if val == item]


def range_to_prefixes(start, end):
    if len(start) != len(end):
        raise ValueError(f"{start!r} and {end!r} do not have an equal length")
    # Implementation detail: It is assumed that spaces and dashes occur in
    # identical places in start and end. If this is not true, the whole thing
    # doesn't work.
    spaces = find_occurrences(" ", start)
    dashes = find_occurrences("-", start)
    if find_occurrences(" ", end) != spaces or find_occurrences("-", end) != dashes:
        raise ValueError(
            f"{start!r} and {end!r} do not have spaces or dashes in identical"
            f" locations"
        )

    prefixes = set()
    not_prefixes = set()
    alphanum = start
    while alphanum:
        prefix = alphanum
        candidate = prefix
        while prefix:
            if prefix in not_prefixes:
                break
            if prefix_works(prefix, start, end, spaces, dashes):
                candidate = prefix
                prefix = prefix[:-1]
            else:
                not_prefixes.add(prefix)
                break
        prefixes.add(candidate)
        alphanum = next_alphanum(candidate, len(start), end, spaces, dashes)
    return prefixes


@openupgrade.migrate()
def migrate(env, version):
    delivery_methods = env["delivery.carrier"].search([])
    if not delivery_methods:
        return
    _logger.warning(
        cleandoc(
            """
            TODO: warn that this creates weird results that are technically
            correct.
            """
        )
    )
    for method in delivery_methods:
        try:
            prefixes = range_to_prefixes(method.zip_from, method.zip_to)
        except Exception as error:
            _logger.error(
                f"Failed to convert the zip range '{method.zip_from} --"
                f" {method.zip_to}'of delivery method {method!r} to a set of"
                f" prefixes. Got error:\n\n{error}"
            )
            continue

        for prefix in prefixes:
            try:
                prefix_record = env["delivery.zip.prefix"].create({"name": prefix})
            # TODO: which exception?
            except Exception:
                prefix_record = env["delivery.zip.prefix"].search(
                    [("name", "=", prefix)]
                )
            method.zip_prefix_ids |= prefix_record
