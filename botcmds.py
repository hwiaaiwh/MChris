__version__ = '0.9.7'

from mcstatus import JavaServer
import discord
from discord.ext import commands, tasks
import socket # error handling in setup
import os, datetime # misc
from jsonstuff import DBObject # some json stuff
import logging, dotenv

# in come the discord.py stuff
# 3 years later and i still don't understand this
intents = discord.Intents.default()
intents.message_content = True
prefixes = 'Chris ', 'chris '
chris = commands.Bot(command_prefix=prefixes, intents=intents)
chris.remove_command('help')
tolkier = dotenv.load_dotenv()
up = False
filedir = os.path.dirname(os.path.abspath(__file__)) + '/files'

# a quick function i wrote to check server status
# shut up autocorrect stop reading my mind
async def check_server(server:JavaServer, ip):
    status = server.status()
    message = f'ping: {status.latency:.2f} ms\nip address: {ip}\njits online: {status.players.online}\n'
    if status.players.online > 0 and status.players.online < 10:
        message += f'- {"\n- ".join(list(i.name for i in status.players.sample))}\n'
    elif status.players.online > 10:
        message += f'- jit.'
    return message

# used to get the java server every time its needed
# useful for multi-server deployments
def getserverobj(guid):
    try:
        return JavaServer.lookup(db.data[str(guid)]['mc_server_ip'], db.data[str(guid)]['mc_server_port'])
    except (KeyError, TimeoutError):
        return None

# setup commands
class setupcmd(commands.Cog, name='setup commands'):
    def __init__(self) -> None:
        super().__init__()

    # in server setup
    # requires a valid minecraft server ip
    # successfully migrated from native function to discordpy
    # current soln is not fun to look at
    @commands.command(help='set me up')
    @commands.has_guild_permissions(administrator=True)
    async def setup(self, ctx: commands.Context, ip=None, port=25565):
        server = getserverobj(ctx.guild.id) # type: ignore
        try:
            if server is None:
                raise NameError      
            else:
                server.ping()  # type: ignore
        except NameError:
            try:
                if ip is None:
                    raise NotImplementedError # idk how else to do this
                server = JavaServer.lookup(ip, port)
                server.status()
            except TimeoutError:
                await ctx.send('guys the server is not on or this jit gave me the wrong address')
            except (ValueError, socket.gaierror):
                await ctx.send('this jit gave me the wrong address')
            except NotImplementedError:
                await ctx.send('this jit gave me no address')
            else:
                db.add_server(ctx.guild.name, ctx.guild.id, ctx.channel.id, ip, port) # type: ignore
                db.save_db()
                await ctx.send('guys the server is on')
        else:
            await ctx.send('server is already setup')

    # help
    @commands.command(help='reset setup')
    @commands.has_guild_permissions(administrator=True)
    async def resetsetup(self, ctx: commands.Context):
        if ctx.guild.id in db.ids: # type: ignore
            db.rm_server(ctx.guild.id) # type: ignore
            db.save_db()
            await ctx.send('bruh')
        else:
            await ctx.send('jit i don\'t even know you')
    
    @resetsetup.error # type: ignore
    async def resetsetup_handler(ctx:commands.Context,error: commands.errors.MissingPermissions):
        await ctx.send('hey you can\'t do that')

# query commands
class querycmd(commands.Cog, name='query commands'):
    def __init__(self) -> None:
        super().__init__()
        self.queries = {}
        self.tasks = ['buffer']
        self.ind = 0
        self.logs=False
        # switched from self vars to queries that use dicts
        # dicts are 
        # key: channel id
        # 0: [prev list]
        # 1: False if first query, True if not
        # 2: True if server online, False if not

    
    # checks if someone joins server
    # help
    @commands.command(aliases=['startquery'])
    @commands.has_guild_permissions(administrator=True)
    async def beginquery(self, ctx:commands.Context):
        ch = ctx.channel
        if not self.taskmanager.is_running():
            logger.log(20,'starting task manager')
            self.taskmanager.start()
        if ch.id in self.queries.keys():
            await ctx.send('jit its already running')
        else:
            logger.log(20, f'adding task: {ch.id}')
            await ctx.send('beginning query')
            self.queries[ch.id] = [[], False, False]
            self.tasks.append(str(ch.id))

    # ends query task
    # help2
    @commands.command(aliases=['endquery'])
    @commands.has_guild_permissions(administrator=True)
    async def stopquery(self, ctx):
        ch = ctx.channel
        if ch.id not in self.queries.keys(): 
            await ctx.send('The query is not running.')
        else:
            logger.log(20, f'removing task: {ch.id}')
            if len(self.queries.keys()) == 0:
                self.tasks.append('buffer')
            del self.queries[ch.id]
            self.tasks.remove(str(ch.id))
            await ctx.send('Stopping query.')
            if len(self.tasks) == 1:
                self.taskmanager.cancel()
    
    # command for me
    # and only me
    # so that it doesnt clutter the logger
    @commands.command(hidden=True)
    @commands.is_owner()
    async def listqueries(self, ctx):
        self.logs = True if self.logs == False else False
        await ctx.send(f'current queries: {self.queries}\ncurrent tasks: {self.tasks}')

    # task manager
    # by all the gods and heavens i want to throw this into the sun
    @tasks.loop(seconds=1.0)
    async def taskmanager(self):
        await chris.wait_until_ready()
        if self.logs:
            logger.log(20, f'current tasks: {self.tasks}')
        if self.tasks[0] == 'buffer':
            if len(self.tasks) != 1:
                self.tasks.append(self.tasks.pop(0))
            else:
                pass # loop again if no tasks
        else:
            ch = chris.get_channel(int(self.tasks[0]))
            id = ch.id
            server = getserverobj(ch.guild.id)
            try:
                queue = server.status() # type: ignore
            except (TimeoutError,ConnectionRefusedError):
                if self.queries[id][2]:
                    await ch.send('the server\'s down')
                    self.queries[id][2] = False
                else:
                    pass
            except IOError:
                pass
            else:
                if not self.queries[id][2]:
                    await ch.send('the server is up')
                    self.queries[id][2] = True
                curr = list(i.name for i in queue.players.sample) if queue.players.sample is not None else []
                if self.queries[id][1]:
                    for player in curr:
                        if player not in self.queries[id][0]:
                            await ch.send(f'guys {player} stopped joined the server.')
                    for player in self.queries[id][0]:
                        if player not in curr:
                            await ch.send(f'guys {player} has left the server.')
                    self.queries[id][0] = curr
                else:
                    self.queries[id][0] = curr
                    self.queries[id][1] = True
                    self.queries[id][2] = True
            self.tasks.append(self.tasks.pop(0))

    @taskmanager.before_loop
    async def before_query(self):
        await chris.wait_until_ready()

    @taskmanager.after_loop
    async def after_query(self):
        if self.taskmanager.is_being_cancelled():
            logger.log(20,'pausing task manager')

#misc
class misccmd(commands.Cog, name='misc. commands'):
    def __init__(self) -> None:
        super().__init__()

    # custom help command
    # stole this from https://github.com/Iphex/DPMBot/tree/master
    # almost stole the prefixes function too, but i think thats deprecated
    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="MChris",
            description="A simple Minecraft server status bot")

        embed.add_field(
            name="status",
            value="Display the configured Minecraft server status",
            inline=False)
        embed.add_field(
            name="status [ip address]",
            value="Display Minecraft server status for a specific IP address",
            inline=False)
        embed.add_field(
            name="setup [mc server address]",
            value="Configure the Minecraft server for this Discord server",
            inline=False)
        embed.add_field(
            name="beginquery",
            value="Start monitoring player join/leave events on the Minecraft server",
            inline=False)
        embed.add_field(
            name="stopquery",
            value="Stop the player monitoring task",
            inline=False)
        embed.add_field(
            name="help",
            value="Display this help message",
            inline=False)
        await ctx.send(embed=embed)

    # server check
    @commands.command(aliases=['status', 'server', 'check'], help='checks mc server status')
    async def servercheck(self, ctx: commands.Context, ip=None, port=25565, *args):
        server = getserverobj(ctx.guild.id) # type: ignore
        if server is None:
            try:
                if ip is None:
                    raise NotImplementedError # idk how else to do this
                server = JavaServer.lookup(ip, port)
                server.status()
            except TimeoutError:
                await ctx.send('Guys, either the server is currently offline or the address provided is incorrect.')
            except (ValueError, socket.gaierror):
                await ctx.send('Man, the address provided is invalid.')
            except NotImplementedError:
                await ctx.send('You didn\'t give me a server address.')
            else:
                await ctx.send(await check_server(server, ip)) # type: ignore
        else:
            await ctx.send(await check_server(server, db.data[str(ctx.guild.id)]['mc_server_ip'])) # type: ignore

# error handling
@chris.event
async def on_command_error(ctx:commands.Context, error:discord.DiscordException, *args, **kwargs):
    if isinstance(error, commands.errors.MissingPermissions) or isinstance(error, commands.errors.NotOwner):
        logger.log(20, f'permission error: {ctx.author} tried to use {ctx.command} in {ctx.guild.name}')
        await ctx.send("You can't do that.")
    elif isinstance(error, commands.errors.CommandInvokeError):
        logger.log(40, f'command invoke error: {ctx.author} tried to use {ctx.command} in {ctx.guild.name}\n{error}')
        await ctx.send('An error occurred while executing the command.')
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('What?')
    else:
        raise error

# yippee!
@chris.event
async def on_ready():
    global db, up, statch
    # add cogs
    # might automate this sometime
    await chris.add_cog(querycmd())
    await chris.add_cog(setupcmd())
    await chris.add_cog(misccmd())
    up = True
    db = DBObject()
    print(f'We have logged in as {chris.user}')

    logger.log(20, f'MChris is active on ({datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})') # type: ignore

# logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
os.makedirs('./logs', exist_ok=True)
handler = logging.FileHandler(filename='./logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# let chris run
chris.run(os.getenv('CHRIS_ENV'), reconnect=True) # type: ignore

# when the chris shut ddown
logger.log(20, 'stopping')
db.save_db()
