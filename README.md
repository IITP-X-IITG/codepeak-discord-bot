
# Codepeak Discord Bot

This bot is used to the automation of the scoring process in the codepeak event.

## Deployment

To deploy this you need to have a virtual machine on cloud.

The steps to deploy this bot are as follow:  
    1. Create a Azure virtual machine.  
    2. Create discord bot through Discord Developer Portal  
    3. Get the github token.  
    4. Enable Google Sheet API from the google cloud console.  
    5. Invite the bot to the codepeak channel. 

### 1. Creating Azure Virtual machine

First you have to signup on microsoft azure to create an account. After successfully creating an account you will be given $200 credit.

Now you have to create a basic virtual machine in azure and get its ssh credentials. Make sure your VM can be accessed through the internet.

Either clone this repo there or you can use the `scp` command from your personal computer to send the files from the repo to the VM.

```bash
  scp -r folder_name name_of_vm@ip_of_vm:address_where_we_want_to_store
```

Now you need to setup the environment for it

```bash
pip install gspread oauth2client discord.py aiohttp python-dotenv requests
```

Now create a .env file in the same folder with the content

```bash
TOKEN=YOUR_DISCORD_BOT_TOKEN
GITHUB_TOKEN=YOUR_GITHUB_TOKEN
IMAGE_URL=YOUR_IMAGE_URL
```

### 2. Setting up the discord bot and getting the TOKEN

- First go to the [Discord Developer Portal](https://discord.com/developers/applications)

- Create a new application there and fill the necessary details like name of the bot, description of the bot and its profile picture.

- Click on the `reset token` button to get a new token and then click on the `copy token` button to copy the token. Paste this token to the .env file of the project.

- Now check the checkboxes under the `Privileged Gateway Intents` section.

### 3. Getting the Github TOKEN

- Go to your GitHub account settings and navigate to `Developer Settings`.
- Select `Personal access tokens` from the left sidebar.
- Click on `Generate new token`.
- Give your token a description and set the required permissions (repo, user, etc.) based on what your bot needs to do.
- Generate the token and copy it and paste it to the .env file. This token will be used for authentication in your bot code when interacting with GitHub's API.


### 4. Enable Google Sheet API from the google cloud console.

- Login to the [Google cloud console](https://console.cloud.google.com/)
- Create a new project
- In your selected project, navigate to the API Library.
- Find and enable the "Google Sheets API" for your project.
- In the Google Cloud Console, go to the `IAM & Admin` -> `Service Accounts` section.
- Click on `Create Service Account` at the top.
- Fill in the details for your service account, like name and role (e.g., Editor for testing purposes).
- After creating the service account, click on it in the Service Accounts list.
- Go to the `Keys` tab and click on `Add Key` -> `Create new key`.
- Choose JSON as the key type and click `Create`. This will download a JSON file containing your credentials.
- Place the downloaded JSON file in your project directory and rename it to `client_key.json`.
- After creating the service account you will get a different email id there copy it and add this email with the editor access to the sheet you want to make the score sheet.

In the line 43 of the discord_bot.py change the name of the sheet
```python
sheet = client_gs.open('NAME_OF_THE_SHEET').sheet1
```

### 5. Invite your bot to a server

Go to the Discord Developer Portal, select your application, navigate to the `OAuth2` tab, and generate an invite link to invite the bot to your server.




## Usage/Examples

```javascript
.test
```
This will check that the bot is running and listing to the commands

```javascript
.award github_id_of_participant point_awarded link_of_pr_or_issue
```
Make sure you have the mentor role before using this commands
