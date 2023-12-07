import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import urllib
import io
import aiohttp

# These are the PRs we have taken care
prs_taken_care = []
prs_ids_file = open('pr_ids.txt', 'r')
prs_taken_care = prs_ids_file.read().split("\n")
prs_ids_file.close()

# Repos list
repos_list = []
repos_file = open('repos.txt', 'r')
repos_list = repos_file.read().split("\n")
repos_list = [x.lower() for x in repos_list]
repos_file.close()

# Bot's announcement channel
discord_channel_id = 1050055499485286450
temp_channel = 1049971925792870470

# Role to mention, when a PR with no points label or badly formatted points label is found
organizing_team_role_id = "<@&900360254624239666>"

# Stuff for google spreadsheets
scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets'
]

file_name = 'client_key.json'
creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
client_gs = gspread.authorize(creds)
sheet = client_gs.open('CODEPEAK 23 SCORING').sheet1

load_dotenv()

# Discord bot
client = commands.Bot(command_prefix=".", intents=discord.Intents.all())
token = os.getenv('TOKEN')
github_token = os.getenv('GITHUB_TOKEN')
image_url = os.getenv('IMAGE_URL')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="codepeak.tech"))
    await check.start()
    print("Logged in as a bot {0.user}".format(client))

# Command to test if the bot is up
@client.command()
async def test(ctx):
    await ctx.reply("Up")

@client.command()
async def award(ctx, username, points, link):

    my_roles = ctx.author.roles
    found_mentor = False
    
    for role in my_roles:
        if role.name == 'Mentor':
            found_mentor = True
            break
    
    if not found_mentor:
        return

    try:
        points = int(points)
    except Exception:
        await ctx.reply("Invalid points")
        return

    column = sheet.col_values(1)
    column = [x.lower() for x in column]

    if (username.lower() in column):
        i = column.index(username.lower())+1
        row = sheet.row_values(i)
        currentPoints = int(row[1])
        l = len(row)
        sheet.update_cell(i, l+1, points)
        sheet.update_cell(i, l+2, link)
        currentPoints += points
        sheet.update_cell(i, 2, currentPoints)
        await ctx.reply(username + " has been awarded " + str(points) + " points! Making their total: " + str(currentPoints))
    else:
        i = len(column) + 1
        sheet.update_cell(i, 1, username)
        sheet.update_cell(i, 2, points)
        sheet.update_cell(i, 3, points)
        sheet.update_cell(i, 4, link)
        await ctx.reply(username + " has been awarded " + str(points) + " points! Making their total: " + str(points))

@tasks.loop(seconds=3*60)
async def check():
     await findNewContributions()

# To announce that we have got a badly formatted points label
async def announce_badly_formatted_points_label(pr_link):
    global client
    global temp_channel
    global organizing_team_role_id
    message = organizing_team_role_id + ", found a PR with `CodePeak 22` label, but with a badly formatted points label.\n"+pr_link
    await client.get_channel(temp_channel).send(message)

# To announce that we have got a PR with CodePeak 22 label but no points label
async def announce_no_points_label(pr_link):
    global client
    global temp_channel
    global organizing_team_role_id
    message = organizing_team_role_id + ", found a PR with `CodePeak 22` label, but with no points label.\n"+pr_link
    await client.get_channel(temp_channel).send(message)

async def new_announce_points_awarded(handle, points, total, link, avatar_link):
    global client
    global discord_channel_id
    global temp_channel
    global image_url
    await client.get_channel(temp_channel).send("4")
    repo = link.split('/')[-3]
    prnumber = link.split('/')[-1]
    change_url = image_url + "points/?username="
    change_url += urllib.parse.quote(handle, safe='()*!\'')
    change_url += "&points="
    change_url += urllib.parse.quote(points, safe='()*!\'')
    change_url += "&totalpoints="
    change_url += urllib.parse.quote(total, safe='()*!\'')
    change_url += "&repo="
    change_url += urllib.parse.quote(repo, safe='()*!\'')
    change_url += "&prnumber="
    change_url += urllib.parse.quote(prnumber, safe='()*!\'')
    change_url += "&url="
    change_url += urllib.parse.quote(avatar_link, safe='()*!\'')

    async with aiohttp.ClientSession() as session:
        await client.get_channel(temp_channel).send("5")
        async with session.get(change_url) as resp:
            await client.get_channel(temp_channel).send("6")
            img = await resp.read()
            with io.BytesIO(img) as file:
                await client.get_channel(temp_channel).send("7")
                await client.get_channel(discord_channel_id).send(file=discord.File(file, "points.png"))
    await client.get_channel(temp_channel).send("8")

# To awards points, i.e., update points in google spreadsheet
async def award_points(handle, points, link, id, avatar_url):
    global client
    global temp_channel
    await client.get_channel(temp_channel).send("1")
    try:
        column = sheet.col_values(1)
        column = [x.lower() for x in column]

        if (handle.lower() in column):
            i = column.index(handle.lower())+1
            row = sheet.row_values(i)
            currentPoints = int(row[1])
            l = len(row)
            sheet.update_cell(i, l+1, points)
            sheet.update_cell(i, l+2, link)
            currentPoints += points
            sheet.update_cell(i, 2, currentPoints)
            await new_announce_points_awarded(handle, str(points), str(currentPoints), link, avatar_url)
        else:
            i = len(column) + 1
            sheet.update_cell(i, 1, handle)
            sheet.update_cell(i, 2, points)
            sheet.update_cell(i, 3, points)
            sheet.update_cell(i, 4, link)
            await new_announce_points_awarded(handle, str(points), str(points), link, avatar_url)

            await client.get_channel(temp_channel).send("2")

        prs_taken_care.append(id)
        set_pr_ids()
        await client.get_channel(temp_channel).send("3")

    except Exception as e:
        print(e)
        print("Rated limited ig")

def set_pr_ids():
    global prs_taken_care
    prs_ids_file = open('pr_ids.txt', 'w')
    prs_ids_file.write("\n".join(prs_taken_care))
    prs_ids_file.close()

# To find new contributions
async def findNewContributions():
    global prs_taken_care
    global repos_list
    global github_token
    print("Attempting to find some.")
    headers = {'Authorization': 'Bearer ' + github_token}

    url = 'https://api.github.com/search/issues?q=label%3Aissue%3A1'
    req = requests.get(url, headers=headers)
    data = json.loads(req.text)

    for i in data['items']:
        repo_name = i['repository_url'].split("/")[-1]
        if not repo_name.lower() in repos_list:
            continue

        if not str(i['id']) in prs_taken_care:
            handle = i['user']['login']
            link = i['html_url']
            points = 1
            await award_points(handle, points, link, str(i['id']), i['user']['avatar_url'])

    url = 'https://api.github.com/search/issues?q=label%3Aissue%3A3'
    req = requests.get(url, headers=headers)
    data = json.loads(req.text)

    for i in data['items']:
        repo_name = i['repository_url'].split("/")[-1]
        if not repo_name.lower() in repos_list:
            continue

        if not str(i['id']) in prs_taken_care:
            handle = i['user']['login']
            link = i['html_url']
            points = 3
            await award_points(handle, points, link, str(i['id']), i['user']['avatar_url'])

    url = 'https://api.github.com/search/issues?q=is%3Apr+is%3Amerged+label%3A%22codepeak+22%22'
    req = requests.get(url, headers=headers)
    data = json.loads(req.text)

    for i in data['items']:
        repo_name = i['repository_url'].split("/")[-1]
        if not repo_name.lower() in repos_list:
            continue
        
        if not str(i['id']) in prs_taken_care:
            handle = i['user']['login']
            link = i['html_url']
            points = -1
            badly_formatted = False

            for label in i['labels']:
                name = label['name'].lower()
                if "points:" in name:
                    args = name.split('points:')

                    if len(args) != 2:
                        await announce_badly_formatted_points_label(link)
                        badly_formatted = True
                        break
                    
                    try:
                        points = int(args[1])
                    except Exception:
                        await announce_badly_formatted_points_label(link)
                        badly_formatted = True
                        break

            if badly_formatted:
                continue

            if points == -1:
                await announce_no_points_label(link)
                continue

            await award_points(handle, points, link, str(i['id']), i['user']['avatar_url'])

client.run(token)