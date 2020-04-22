"""
Syntax: .update
\nAll Credits goes to © @Three_Cube_TeKnoways
\nFor this awasome plugin.\nPorted from PpaperPlane Extended"""

import os
import sys
import git
import asyncio
import requests
from telethon import events
from uniborg.util import admin_cmd
from sql_helpers.global_variables_sql import  SYNTAX, MODULE_LIST

MODULE_LIST.append("update (update the BEASTBOT)")

# -- Constants -- #
IS_SELECTED_DIFFERENT_BRANCH = (
    "looks like a custom branch {branch_name} "
    "is being used:\n"
    "in this case, Updater is unable to identify the branch to be updated."
    "please check out to an official branch, and re-start the updater."
)
OFFICIAL_UPSTREAM_REPO = "https://github.com/rishabh-45/new"
BOT_IS_UP_TO_DATE = "`The BeastBot up-to-date.\nThank you for Using this Service.`"
NEW_BOT_UP_DATE_FOUND = (
    "new update found for {branch_name}\n"
    "changelog: \n\n{changelog}\n"
    "updating ..."
)
NEW_UP_DATE_FOUND = (
    "New update found for {branch_name}\n"
    "`updating ...`"
)
REPO_REMOTE_NAME = "temponame"
IFFUCI_ACTIVE_BRANCH_NAME = "master"
DIFF_MARKER = "HEAD..{remote_name}/{branch_name}"
NO_HEROKU_APP_CFGD = "no heroku application found, but a key given? 😕 "
HEROKU_GIT_REF_SPEC = "HEAD:refs/heads/master"
RESTARTING_APP = "re-starting heroku application"
# -- Constants End -- #


@borg.on(admin_cmd(pattern="update ?(.*)", allow_sudo=True))
async def updater(message):
    try:
        repo = git.Repo()
    except git.exc.InvalidGitRepositoryError as e:
        repo = git.Repo.init()
        origin = repo.create_remote(REPO_REMOTE_NAME, OFFICIAL_UPSTREAM_REPO)
        origin.fetch()
        repo.create_head(IFFUCI_ACTIVE_BRANCH_NAME, origin.refs.master)
        repo.heads.master.checkout(True)

    active_branch_name = repo.active_branch.name
    if active_branch_name != IFFUCI_ACTIVE_BRANCH_NAME:
        await message.edit(IS_SELECTED_DIFFERENT_BRANCH.format(
            branch_name=active_branch_name
        ))
        return False

    try:
        repo.create_remote(REPO_REMOTE_NAME, OFFICIAL_UPSTREAM_REPO)
    except Exception as e:
        print(e)
        pass

    temp_upstream_remote = repo.remote(REPO_REMOTE_NAME)
    temp_upstream_remote.fetch(active_branch_name)

    changelog = generate_change_log(
        repo,
        DIFF_MARKER.format(
            remote_name=REPO_REMOTE_NAME,
            branch_name=active_branch_name
        )
    )

    if not changelog:
        await message.edit("`Updating...`")
        await asyncio.sleep(3)

    message_one = NEW_BOT_UP_DATE_FOUND.format(
        branch_name=active_branch_name,
        changelog=changelog
    )
    message_two = NEW_UP_DATE_FOUND.format(
        branch_name=active_branch_name
    )

    if len(message_one) > 4095:
        with open("change.log", "w+", encoding="utf8") as out_file:
            out_file.write(str(message_one))
        await borg.send_message(
            message.chat_id,
            document="change.log",
            caption=message_two
        )
        os.remove("change.log")
    else:
        await borg.send_message(message.chat_id,"ChangeLog:\n"+message_one)
        # await message.edit(message_one)
        await asyncio.sleep(3)

    temp_upstream_remote.fetch(active_branch_name)
    repo.git.reset("--hard", "FETCH_HEAD")

    if Config.HEROKU_API_KEY is not None:
        import heroku3

        logger.info("heroku api key"+Config.HEROKU_API_KEY)

        heroku = heroku3.from_key(Config.HEROKU_API_KEY)
        heroku_applications = heroku.apps()
        if len(heroku_applications) >= 1:
            if Config.HEROKU_APP_NAME is not None:
                logger.info("heroku app name"+Config.HEROKU_APP_NAME)

                heroku_app = None
                for i in heroku_applications:
                    extr_name=""
                    if Config.HEROKU_LINK!=None:
                        extr_name=Config.HEROKU_LINK.split(".")[0][8:]
                    if i.name == Config.HEROKU_APP_NAME or i.name==extr_name:
                        heroku_app = i
                if heroku_app is None:
                    await message.edit("Invalid APP Name. Please set the name of your bot in heroku in the var `HEROKU_APP_NAME.`")
                    return
                heroku_git_url = heroku_app.git_url.replace(
                    "https://",
                    "https://api:" + Config.HEROKU_API_KEY + "@"
                )
                if "heroku" in repo.remotes:
                    remote = repo.remote("heroku")
                    remote.set_url(heroku_git_url)
                else:
                    remote = repo.create_remote("heroku", heroku_git_url)
                asyncio.get_event_loop().create_task(deploy_start(borg, message, HEROKU_GIT_REF_SPEC, remote))

            else:
                await message.edit("Please create the var `HEROKU_APP_NAME` as the key and the name of your bot in heroku as your value.")
                return
        else:
            await message.edit(NO_HEROKU_APP_CFGD)
    else:
        msg="""No `HEROKU_API_KEY` found in config
        \nGoto https://dashboard.heroku.com/account\nThere  after scrolling a bit you will see API key tab .. \nclick on **reveal** button you will see your **API key** \n**copy it**
        \nNow goto **Heroku>your app >Settings>Reveal Config vars**
        \nNow add `HEROKU_API_KEY` with copied API key"""
        await message.edit(msg)
        

def generate_change_log(git_repo, diff_marker):
    out_put_str = ""
    d_form = "%d/%m/%y"
    for repo_change in git_repo.iter_commits(diff_marker):
        out_put_str += f"•[{repo_change.committed_datetime.strftime(d_form)}]: {repo_change.summary} <{repo_change.author}>\n"
    return out_put_str

async def deploy_start(borg, message, refspec, remote):
    await message.edit(RESTARTING_APP)
    await message.edit("Updating and Deploying New Branch. Please wait for 5 minutes then use `.alive` to check if i'm working or not.")
    await remote.push(refspec=refspec)
    await borg.disconnect()
    os.execl(sys.executable, sys.executable, *sys.argv)

SYNTAX.update({"update":"""
\nUpdate your bot with the latest update on Official Repo.
\nBut first set HEROKU_API_KEY first .
\nIf you have more than one bot set HEROKU_APP_NAME too
"""})
