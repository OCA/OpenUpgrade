import argparse
import os
import re
from pathlib import Path

from github import Auth, Github
from github.PullRequestReview import PullRequestReview

import tools

parser = argparse.ArgumentParser()
parser.add_argument('--version', nargs='+')
parser.add_argument('--repo', default='OCA/OpenUpgrade')
parser.add_argument('--github-login', default='ocabot')
args = parser.parse_args()

auth = None
if os.environ.get('GITHUB_TOKEN'):
    auth = Auth.Token(os.environ.get('GITHUB_TOKEN'))

g = Github(auth=auth)
repo = g.get_repo(args.repo)

# #######################
# Custom Function
# #######################
def module_ok(module_name):
    return module_coverage[module_name] in ["nothing_to_do", "done"] or opened_prs.get(module_name) == pr_number

def _extract_migration_comment(migration_message):
    if not migration_message:
        return "", "", ""
    text_reg = (
        r"(?P<before>(\r|\n|.)*)"
        r"<dependency>"
        "(?P<current_text>(\n|.)*)"
        r"<\/dependency>"
        r"(?P<after>(\r|\n|.)*)"
    )
    res = re.match(text_reg, migration_message.body)
    if not res:
        return "", "", ""
    groups = res.groupdict()
    return groups["before"], groups["current_text"], groups["after"]


def _get_comment_or_review(pr, content):
    comments = [x for x in pr.get_issue_comments() if content in x.body]
    if comments:
        return comments[0]
    reviews = [x for x in pr.get_reviews() if content in x.body]
    return reviews and reviews[0] or False


# ####################################
# Main Script
# ####################################

for current_version in map(float, args.version):
    tools._logger.info(f"*************************************************")
    tools._logger.info(f"Update Dependencies for Version {current_version}")
    tools._logger.info(f"*************************************************")

    # Get Opened PRs
    done_prs, opened_prs = tools._get_prs(repo, current_version)

    # Get Done modules
    module_coverage = tools._get_module_coverage(repo, current_version)


    for module_name, pr_number in opened_prs.items():
        tools._logger.info(f"Handle PR #{pr_number} for module '{module_name}'")
        manifest = tools._get_manifest_module(repo, current_version, module_name)
        if not manifest:
            tools._logger.info(f"the module {module_name} disappeared in the new version.")
            continue

        depends = manifest.get("depends")
        pr = repo.get_pull(pr_number)

        migration_message = _get_comment_or_review(pr, "ocabot migration")
        current_labels = [x.name for x in pr.labels]
        new_labels = current_labels.copy()

        log_message = f"PR #{pr_number} for {module_name}:"
        if all([module_ok(x) for x in depends]):
            # all dependencies are OK, mark the PR as OK.
            label_to_remove = "Blocked by dependency"
            label_to_add = "Dependency OK"
        else:
            # mark the PR as blocked
            label_to_remove = "Dependency OK"
            label_to_add = "Blocked by dependency"

        if label_to_remove in new_labels:
            log_message += f" Remove '{label_to_remove}'"
            new_labels.remove(label_to_remove)

        if label_to_add not in new_labels:
            log_message += f" Set '{label_to_add}'"
            new_labels.append(label_to_add)

        if new_labels != current_labels:
            tools._logger.info(log_message)
            pr.set_labels(*new_labels)

        if not migration_message:
            tools._logger.warning(f"Migration message not found in {pr.number}")
            continue

        before_text, current_text, after_text = _extract_migration_comment(
            migration_message
        )

        dep_modules_ok = [x for x in depends if x in done_prs]
        dep_modules_pending = [x for x in depends if x in opened_prs]
        dep_modules_ko = [
            x for x in depends if x not in dep_modules_ok + dep_modules_pending
        ]
        new_text = ""
        for dep_module in dep_modules_ok:
            new_text += f"\n- {dep_module} : #{done_prs[dep_module]}"
        for dep_module in dep_modules_pending:
            new_text += f"\n- {dep_module} : #{opened_prs[dep_module]}"
        for dep_module in dep_modules_ko:
            new_text += f"\n- {dep_module} : TODO"
            if module_ok(dep_module):
                tools._logger.error(f"{dep_module} not found in the issue 'Migration to version {current_version}'")


        if new_text:
            new_text = "Depends on : \n" + new_text

        new_body = ""
        if not current_text and new_text:
            tools._logger.info(
                f"PR#{pr.number} - {pr.title}: ADDING Text in migration message."
            )
            if migration_message.user.login != args.github_login:
                tools._logger.warning(
                    f"The message has been written by @{migration_message.user.login}"
                )
            new_body = (
                migration_message.body + "\n\n<dependency>" + new_text + "</dependency>"
            )
        elif new_text != current_text:
            tools._logger.info(
                f"PR#{pr.number} - {pr.title}: Replacing text in migration message."
            )
            if migration_message.user.login != args.github_login:
                tools._logger.warning(
                    f"The message has been written by @{migration_message.user.login}"
                )
            new_body = (
                before_text + "<dependency>" + new_text + "</dependency>" + after_text
            )

        if new_body:
            if type(migration_message) is PullRequestReview:
                tools._logger.warning("Unable to edit the PR due to PyGithub limitation.")
                continue
            migration_message.edit(new_body)
