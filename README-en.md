# GenshinArtifacter_Discrord-BOT

# What is this?

This is a code to make "ArtifacterImageGen", which calculates scores of relics of the Genshin Impact and generates images, available as a BOT for Discord.

We decided to distribute the code under the MIT license so that anyone can easily use the DiscordBOT created based on "ArtifacterImageGen".

This is thanks to "ArtifacterImageGen" being distributed under MIT license on github.

Our sincere thanks to Mr. Hyugo.

This is almost my first time using github, so there may be mistakes, etc.

I would appreciate it if you could contact me if you find any mistakes.

# operating environment
Python 3.11.2

Discord.py 2.2.2

python-dotenv 1.0.0

Pillow 9.4.0

PyYAML 6.0

requests 2.28.2

# How to Setup

## Windows

Editing...

## Linux(Debian or Ubuntu)

### Create Disocrd BOT

Access the DiscordDeveloperPortal.

https://discord.com/developers/applications

Click on "New Application."

(If you have already created a dedicated BOT, skip to token generation.)

Decide on a name for the BOT and enter it in the "NAME" field.

Agree to the Terms of Use and Developer Policy and click "Create".

Select the "BOT" tab under "SETTING" and click "Add Bot.

Click "Yes, do it!" when the confirmation dialog appears.

(If 2FA is set, please authenticate.)

### Token Generation

Click on "Copy" under "TOKEN" to copy the BOT token.

Make a note (paste) of this token in a notepad, etc.

This token must not be seen by anyone.

### Setting BOT

Turn ON "PRESENCE INTENT", "SERVER MEMBERS INTENT", and "MESSAGE CONTENT INTENT" in "Privileged Gateway Intents".

Remember to click "Save Changes" to save your changes.

### Allow BOTs to join the server

Select "OAuth2" and "URL Generator" from the menu.

Check the "BOT" checkbox under "SCOPES" and set the "BOT PERMISSIONS" to the necessary permissions.

(If you own the server and trust the code of this BOT, you may check the "Administrator" checkbox.)

Copy the URL displayed in the "GENERATED URL" field and access the copied URL.

Select the server you want the BOT to join and click Yes.

Confirm that the authorization is correct and click authentication.

Clear the hCaptcha authorization and enlist the BOT.

This completes the preconfiguration of the Discord BOT.

### Download Source
Download this repository from github as a zip file or clone it with GithubCLI, etc.

https://github.com/tarou-software/GenshinArtifacter_Discrord-BOT

(If you downloaded the file as a zip file, please unzip it.)

Open the file ".env" in the directory and replace "token here!" with the BOT token copied in "Token Generation".

### Setup Python
Run the check version command to see if python is installed.

````
python3 --version
````

If the version is displayed, you are OK.

Install pip.

````
sudo apt update
sudo apt install python3-pip
```` 

Use PIP to install each library.

```
pip3 install discord.py
```

```
pip3 install python-dotenv
```

```
pip3 install Pillow
```

```
pip3 install pyyaml
```

```
pip3 install requests
```

Verify that everything was installed correctly.

### Make the BOT work

Launch a command prompt or similar.

Change the current directory to the source directory.

Execute the following command

```
python bot_start.py
```

(It is recommended to create a batch file.)

"Ready! Name:~~" and confirm that the BOT is working properly on Discord.

# Asset Update

Due to the specifications of ArtifacterImageGen, it is necessary to update assets to accommodate new elements that are added when Genshin Impact is upgraded.

We are currently working on the code for updating assets, so please be patient.

# Copylight

ArtifacterImageGen Copyright (c) Hyugo(FuroBath)

GenshinArtifacter_Discrord-BOT Copyright (c) mendoitarou_

# special thanks

[FuroBath/ArtifacterImageGen](https://github.com/FuroBath/ArtifacterImageGen)

# translation
This README-en.md has been translated from Japanese to English using the DeepL translation tool.

https://www.deepl.com/ja/translator

# Contact

It may take some time for us to reply.

Please understand that it may take some time to reply.

Twitter: [@mendoitarou_](https://twitter.com/mendoitarou_)

E-Mail: [contact@mendoitarou.com](mailto:contact@mendoitarou.com)
