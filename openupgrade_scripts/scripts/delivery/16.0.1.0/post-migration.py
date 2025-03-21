# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
# SPDX-FileCopyrightText: 2024 Tecnativa - Pedro M. Baeza
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import string

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


def numerical_range_to_prefixes(min_, max_):
    """Adapted from https://github.com/voronind/range-regex."""

    def fill_by_nines(integer, nines_count):
        return int(str(integer)[:-nines_count] + "9" * nines_count)

    def fill_by_zeros(integer, zeros_count):
        return integer - integer % 10**zeros_count

    def split_to_ranges(min_, max_):
        stops = {max_}
        nines_count = 1
        stop = fill_by_nines(min_, nines_count)
        while min_ <= stop < max_:
            stops.add(stop)
            nines_count += 1
            stop = fill_by_nines(min_, nines_count)
        zeros_count = 1
        stop = fill_by_zeros(max_ + 1, zeros_count) - 1
        while min_ < stop <= max_:
            stops.add(stop)
            zeros_count += 1
            stop = fill_by_zeros(max_ + 1, zeros_count) - 1
        stops = list(stops)
        stops.sort()
        return stops

    subpatterns = []
    start = min_
    for stop in split_to_ranges(min_, max_):
        pattern = ""
        any_digit_count = 0
        for start_digit, stop_digit in zip(str(start), str(stop), strict=True):
            if start_digit == stop_digit:
                pattern += start_digit
            elif start_digit != "0" or stop_digit != "9":
                pattern += f"[{start_digit}-{stop_digit}]"
            else:
                any_digit_count += 1
        if any_digit_count:
            pattern += "[0-9]"
        if any_digit_count > 1:
            pattern += f"{{{any_digit_count}}}"
        pattern += "$"
        subpatterns.append(pattern)
        start = stop + 1
    return subpatterns


def _convert_carrier_zip_ranges(env):
    """Transform the previous zip_from and zip_to fields to the new prefixes system."""
    env.cr.execute(
        "SELECT id, zip_from, zip_to FROM delivery_carrier "
        "WHERE zip_from IS NOT NULL AND zip_to IS NOT NULL"
    )
    for carrier_id, zip_from, zip_to in env.cr.fetchall():
        if zip_from.isnumeric() and zip_to.isnumeric():
            prefixes = numerical_range_to_prefixes(int(zip_from), int(zip_to))
        else:
            try:
                prefixes = range_to_prefixes(zip_from, zip_to)
            except Exception as error:
                _logger.error(
                    f"Failed to convert the zip range '{zip_from} --"
                    f" {zip_to}'of delivery method {carrier_id} to a set of"
                    f" prefixes. Got error:\n\n{error}"
                )
                continue
        carrier = env["delivery.carrier"].browse(carrier_id)
        for prefix in prefixes:
            prefix_record = env["delivery.zip.prefix"].search([("name", "=", prefix)])
            if not prefix_record:
                prefix_record = env["delivery.zip.prefix"].create({"name": prefix})
            carrier.zip_prefix_ids |= prefix_record


@openupgrade.migrate()
def migrate(env, version):
    _convert_carrier_zip_ranges(env)
