import logging
import re
import sys
import urllib

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stdout)],
)

_logger = logging.getLogger()


def _get_prs(repo, version):
    opened_prs = {}
    done_prs = {}

    line_reg = (
        r"- \[(?P<done> |x)\] (\(del\) )?(\(new\) )?"
        r"(?P<module_name>\w+).*(pull\/|#)(?P<pr_number>\d+)"
    )
    issue_title = f"Migration to version {version:.1f}"

    _logger.info(f"Get PRs referenced in '{issue_title}' ...")
    # Get main issue to have PRs numbers
    for issue in repo.get_issues():
        if issue.title == issue_title:
            for line in issue.body.split("\n"):
                if not line.startswith("- ["):
                    continue
                res = re.match(line_reg, line)
                if not res:
                    _logger.debug(f"Unable to parse correctly '{line}'")
                    continue
                groups = res.groupdict()
                pr_number = int(groups["pr_number"])
                if groups["done"] == "x":
                    done_prs[groups["module_name"]] = pr_number
                else:
                    opened_prs[groups["module_name"]] = pr_number
    _logger.info(
        f">> found {len(done_prs)} done PRs" f" and {len(opened_prs)} Opened PRs"
    )
    return done_prs, opened_prs


def _get_module_coverage(repo, version):
    file_name = f"modules{(version - 1) * 10:.0f}-{(version) * 10:.0f}.rst"
    url = (
        f"https://raw.githubusercontent.com/OCA/OpenUpgrade"
        f"/{version:.1f}/docsource/"
        f"{file_name}"
    )
    module_coverage = {}
    _logger.info(f"Get and parse {file_name} to know coverage state ...")
    page = urllib.request.urlopen(url).read().decode()
    for line in page.split("\n"):
        line = line.replace("|del|", "").replace("|new|", "")
        if not line.startswith("|"):
            continue
        res = line.split("|")
        module_name = res[1].strip()
        status = res[2].strip()
        if module_name == "Module":
            continue
        if status == "":
            module_coverage[module_name] = "to_do"
        elif status == "Nothing to do":
            module_coverage[module_name] = "nothing_to_do"
        elif status.startswith("Done"):
            module_coverage[module_name] = "done"
        else:
            continue
            # TODO:fix me
            raise Exception("Status '%s' has not been analyzed." % (status))
    _logger.info(f">> found {len(module_coverage)} modules.")
    return module_coverage


def _get_manifest_module(repo, version, module_name):
    url = (
        f"https://raw.githubusercontent.com/odoo/"
        f"odoo/{version:.1f}/addons/{module_name}/__manifest__.py"
    )
    try:
        page = urllib.request.urlopen(url).read().decode()
    except urllib.error.HTTPError:
        return
    return eval(page)
