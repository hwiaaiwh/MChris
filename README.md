# MChris
A simple Discord bot that allows a server or servers to check the status and player list of a Minecraft Java Edition server.

## Features
- Check to see if a Minecraft Java server is online.
- List the players of said server if online.
- Has a multi-server (hopefully) daemon that checks the server status and who joins/leaves the server every second.

## Installation
### Manual Install
1) Visit https://discord.com/developers/applications and copy the token from your application/bot. You can find the specific steps in the following: https://gist.github.com/guarzo/a4d238b932b6a168ad1c5f0375c4a561
2) In .env, delete where it says `[insert token here]` and replace it with your token.
3) If you haven't already, install Python (this was developed on 3.13.7, but I think any will do) and the required dependencies located in the `requirements.txt` file. If you have Python installed, you can do this with the following command: 
`python -m pip install -r requirements.txt`
4) Run `botcmds.py`, and the bot will automatically set itself up.

### Docker Install
If you have Docker on the machine hosting the bot, you can use the Dockerfile and the provided `build.bat` or `build.sh` scripts to automatically set up your bot. (from step 3 onwards from Manual Install)

## Commands
`status` 
Display the configured Minecraft server status

`status [ip address]`
Display Minecraft server status for a specific IP address

`setup [mc server address]`
Configure the Minecraft server for this Discord server

`beginquery`
Start monitoring player join/leave events on the Minecraft server

`stopquery`
Stop the player monitoring task

`help`
Display the help message

## Disclaimer
This is probably my first big Python project. There will be bugs. My source code has some of my grievances with this code. It will be janky, but its worked on my personal server so far. Please let me know if any bugs pop up, and I will fix them when I get the time in my college student schedule to.

## Acknowledgements
https://github.com/Iphex/DPMBot for the framework. If it weren't for them, I wouldn't know where to start.

mcstatus - Made by Dinnerbone (Mojang dev), this really simplified a lot of the processes behind this bot.

My friend Chris - The inspiration behind the bot's name.

## License
This project is licensed under MIT; see `LICENSE` for details.
