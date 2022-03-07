import discord
from discord.ext import commands
import os
import random
import json
import requests
import praw
import giphy_client
from requests import get

client = commands.Bot(command_prefix='?')


@client.event
async def on_guild_join(ctx, guild):
    await ctx.send('Hi!')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the permission to do that.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have the permission to do that.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("That command doesn't exist.")


mainshop = [{
    "name": "Watch",
    "price": 100,
    "description": ":watch:"
}, {
    "name": "Laptop",
    "price": 1000,
    "description": ":computer:"
}, {
    "name": "PC",
    "price": 10000,
    "description": ":desktop:"
}, {
    "name": "Ferrari",
    "price": 99999,
    "description": ":race_car:"
}]


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return (quote)


raggy = 767758282705731654


@client.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching,
                                name="?help")
    await client.change_presence(activity=activity, status=discord.Status.idle)
    print('UwU')


@client.command()
async def nickchange(ctx, member: discord.Member, nick):
  if not member:
    member = ctx.author
    return
  await member.edit(nick=nick)
  await ctx.send('Changed.')

@client.command()
async def userinfo(ctx, member: discord.Member = None):
    if not member:
        member = ctx.message.author

    roles = [role for role in member.roles]

    embed = discord.Embed(colour=member.color,
                          timestamp=ctx.message.created_at)

    embed.set_author(name=f"User Info - {member}")
    embed.set_thumbnail(url=member.avatar_url)
    embed.set_footer(text=f"Requested by {ctx.author}",
                     icon_url=ctx.author.avatar_url)

    embed.add_field(name='ID:', value=member.id)
    embed.add_field(
        name='Created at:',
        value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(
        name='Joined at:',
        value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name=f"Roles: {len(roles)}",
                    value=" ".join([role.mention for role in roles]))
    embed.add_field(name="Highest Role:", value=member.top_role.mention)

    embed.add_field(name="Bot?", value=member.bot)

    await ctx.send(embed=embed)

@client.command()
async def achievement (ctx, *, acheive_what:str):
  acheive=acheive_what.replace(" ","+")
  embed=discord.Embed(title=f"{ctx.author.display_name} unlocked a new achievement!")
  embed.set_image(url=f"https://minecraftskinstealer.com/achievement/2/New+achievement%21/{acheive}")
  await ctx.send(embed=embed)

@client.command()
async def pfp(ctx, member: discord.Member = None):
    await ctx.send(f"{member.avatar_url}")

@client.command()
async def serverpfp(ctx):
  await ctx.send(str(ctx.guild.icon_url))

@client.command()
async def serverinfo(ctx):
  name = str(ctx.guild.name)
  description = str(ctx.guild.description)

  owner = str(ctx.guild.owner)
  id = str(ctx.guild.id)
  region = str(ctx.guild.region)
  memberCount = str(ctx.guild.member_count)

  icon = str(ctx.guild.icon_url)
   
  embed = discord.Embed(
      title=name + " Server Information",
      description=description,
      color=discord.Color.blue()
    )
  embed.set_thumbnail(url=icon)
  embed.add_field(name="Owner", value=owner, inline=True)
  embed.add_field(name="Server ID", value=id, inline=True)
  embed.add_field(name="Region", value=region, inline=True)
  embed.add_field(name="Member Count", value=memberCount, inline=True)

  await ctx.send(embed=embed)

@client.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int):
    await ctx.channel.purge(limit=limit)
    await ctx.send('Purged.', delete_after=3.0)
    await ctx.message.delete()


@client.command(pass_context=True, aliases=['addrole', 'giveroles'])
async def giverole(ctx, user: discord.Member, role: discord.Role):
    await user.add_roles(role)
    await ctx.send(f"Added **{role.mention}** to **{user.mention}.**")


@client.command(pass_context=True)
async def removerole(ctx, role: discord.Role, user: discord.Member):
    await user.remove_roles(role)
    await ctx.send(f"Removed **{role.mention}** from **{user.mention}.**")


@client.command(pass_context=True)
async def changenick(ctx, member: discord.Member, *, nick):
    if not member:
      member = ctx.author
    await member.edit(nick=nick)
    await ctx.send(f'Nickname was changed for {member.mention}')


@client.command(aliases=['8b', 'eightball', '8ball'])
async def _8ball(ctx, *, question):
    answers = [
        "Nope.", "I don't know", "I'm to lazy to predict.", "My reply is no.",
        "Better not tell you now.", "Concentrate and ask again.",
        "My sources say no.", "Yes.", "Search on Google.", "Hell yeah.",
        "I don't think I want to answer that.", "I'm too busy to answer that."
    ]
    embed = discord.Embed(color=0x000000,
                          title=f'{question}',
                          description=f'{random.choice(answers)}')
    await ctx.send(embed=embed)


@client.command()
async def invite(ctx):
    await ctx.send(
        'https://discord.com/oauth2/authorize?client_id=905837727747039294&scope=identify%20bot%20applications.commands&permissions=2146958591'
    )


@client.command()
async def quote(ctx):
    quote = get_quote()
    await ctx.send(quote)


@client.command()
async def myip(ctx):
    ip = get('https://api.ipify.org').text
    await ctx.send('Your IP is: {}'.format(ip))


async def update_bank(user, change=0, mode='wallet'):
    users = await get_bank_data()

    users[str(user.id)][mode] += change
    with open('mainbank.json', 'w') as f:
        json.dump(users, f)
        bal = [users[str(user.id)]['wallet'], users[str(user.id)]['bank']]
        return bal


async def open_account(user):
    users = await get_bank_data()

    with open('mainbank.json', 'r') as f:
        users = json.load(f)
    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]['wallet'] = 0
        users[str(user.id)]['bank'] = 0

    with open('mainbank.json', 'w') as f:
        json.dump(users, f)
        return True


async def get_bank_data():
    with open('mainbank.json', 'r') as f:
        users = json.load(f)

        return users


@client.command(aliases=['bal', 'money', 'cash'])
async def balance(ctx):
    await open_account(ctx.author)

    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]['wallet']
    bank_amt = users[str(user.id)]['bank']

    em = discord.Embed(title=f"{ctx.author.name}'s balance:")
    em.add_field(name="Wallet", value=wallet_amt)
    em.add_field(name="Bank", value=bank_amt)
    await ctx.send(embed=em)

@client.command(description="Mutes the specified user.")
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="Muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=False)
    embed = discord.Embed(title="Mute", description=f"{member.mention} was muted ", colour=discord.Colour.light_gray())
    embed.add_field(name="Reason:", value=reason, inline=False)
    await ctx.send(embed=embed)
    await member.add_roles(mutedRole, reason=reason)
    await member.send(f" You have been muted from: {guild.name} reason: {reason}")

@client.command()
@commands.has_permissions(manage_messages=True)
async def unmute(ctx, member: discord.Member):
   mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")

   await member.remove_roles(mutedRole)
   await member.send(f" You are unmuted in: - {ctx.guild.name}")
   embed = discord.Embed(title="Unmute", description=f" Unmuted-{member.mention}",colour=discord.Colour.light_gray())
   await ctx.send(embed=embed)

@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(101)

    await ctx.send(f"Someone gave you {earnings}:dollar:!")

    users[str(user.id)]['wallet'] += earnings

    with open('mainbank.json', 'w') as f:
        json.dump(users, f)


@client.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def work(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    earnings = random.randrange(1000)

    await ctx.send(f"You earned {earnings} :dollar:!")

    users[str(user.id)]['wallet'] += earnings

    with open('mainbank.json', 'w') as f:
        json.dump(users, f)


@client.command(aliases=['wd'])
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[1]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1 * amount, 'bank')
    await ctx.send(f'{ctx.author.mention} You withdrew {amount}:dollar:!')


@client.command(aliases=['dp'])
async def deposit(ctx, amount=None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    await update_bank(ctx.author, -1 * amount)
    await update_bank(ctx.author, amount, 'bank')
    await ctx.send(f'{ctx.author.mention} You deposited {amount}:dollar:!')


@client.command(aliases=['sm'])
async def send(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member)
    if amount == None:
        await ctx.send("Please enter the amount")
        return

    bal = await update_bank(ctx.author)
    if amount == 'all':
        amount = bal[0]

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance!')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return

    if member == ctx.author:
        await ctx.send('You cannot send money to yourself!')
        return

    await update_bank(ctx.author, -1 * amount, 'bank')
    await update_bank(member, amount, 'bank')
    await ctx.send(f'{ctx.author.mention} You gave {member} {amount}:dollar:!')


@client.command(aliases=["lb"])
async def leaderboard(ctx, x=1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        total_amount = users[int(user)]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = int(user)
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(
        title=f"Top {x} Richest People",
        description=
        "This is decided on the basis of raw money in the bank and wallet",
        color=discord.Color(0xfa43ee))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name=f"{index}. {name}", value=f"{amt}", inline=False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed=em)


@client.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []

    em = discord.Embed(title="Bag")
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name=name, value=amount)

    await ctx.send(embed=em)


@client.command(aliases=['steal'])
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)
    bal = await update_bank(member)

    if bal[0] < 100:
        await ctx.send('It is useless to rob him :(')
        return

    earning = random.randrange(0, bal[0])

    await update_bank(ctx.author, earning)
    await update_bank(member, -1 * earning)
    await ctx.send(
        f'{ctx.author.mention} You robbed {member} and got {earning}:dollar:!')


@client.command()
async def slots(ctx, amount=None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please enter the amount!")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)

    if amount > bal[0]:
        await ctx.send('You do not have sufficient balance')
        return
    if amount < 0:
        await ctx.send('Amount must be positive!')
        return
    final = []
    for i in range(3):
        a = random.choice([':x:', ':o:'])

        final.append(a)

    await ctx.send(str(final))

    if final[0] == final[1] or final[1] == final[2] or final[0] == final[2]:
        await update_bank(ctx.author, 2 * amount)
        await ctx.send(f'You won :) {ctx.author.mention}')
    else:
        await update_bank(ctx.author, -1 * amount)
        await ctx.send(f'You lose :( {ctx.author.mention}')


@client.command()
async def shop(ctx):
    em = discord.Embed(title="Shop")

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name=name, value=f"${price} | {desc}")

    await ctx.send(embed=em)


@beg.error
async def beg_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(
            title=f"Slow it down bro!",
            description=f"Try again in {error.retry_after:.2f}s.")
        await ctx.send(embed=em)


@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(
            title=f"Slow it down bro!",
            description=f"Try again in {error.retry_after:.2f}s.")
        await ctx.send(embed=em)


@client.command()
async def buy(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(
                f"You don't have enough money in your wallet to buy {amount} {item}"
            )
            return

    await ctx.send(f"You just bought {amount} {item}")


async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False, 1]

    cost = price * amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0] < cost:
        return [False, 2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {"item": item_name, "amount": amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item": item_name, "amount": amount}
        users[str(user.id)]["bag"] = [obj]

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost * -1, "wallet")

    return [True, "Worked"]


@client.command()
async def sell(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(f"You don't have {amount} {item} in your bag.")
            return
        if res[1] == 3:
            await ctx.send(f"You don't have {item} in your bag.")
            return

    await ctx.send(f"You just sold {amount} {item}!")


async def sell_this(user, item_name, amount, price=None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price == None:
                price = 0.7 * item["price"]
            break

    if name_ == None:
        return [False, 1]

    cost = price * amount

    users = await get_bank_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False, 2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            return [False, 3]
    except:
        return [False, 3]

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, cost, "wallet")

    return [True, "Worked"]


@client.command()
async def gif(ctx, *, q='gif'):

    api_key = os.getenv('gifkey')
    api_instance = giphy_client.DefaultApi()

    api_response = api_instance.gifs_search_get(api_key,
                                                q,
                                                limit=5,
                                                rating='g')
    lst = list(api_response.data)
    gif = random.choice(lst)

    await ctx.send(gif.embed_url)


@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! **{round(client.latency * 1000)}ms.**")


@client.command()
async def say(ctx, *, args):
    await ctx.message.delete()
    await ctx.send(args)


reddit = praw.Reddit(client_id='7NNN5flP56QIF9mIuvYW5A',
                     client_secret='9-LrHQXIby53cVjhaql8gMLR26B43Q',
                     user_agent='test')


@client.command()
async def meme(ctx):
    memes_submissions = reddit.subreddit('memes').hot()
    post_to_pick = random.randint(1, 10)
    for i in range(0, post_to_pick):
        submission = next(x for x in memes_submissions if not x.stickied)

    await ctx.send(submission.url)


@client.command()
async def membersay(ctx, member: discord.Member, *, args):
    await ctx.message.delete()
    try:
        await member.send(args)
    except:
        await ctx.send('Member has their DMs closed.')


@client.command()
async def countservers(ctx):
    await ctx.send(f"I'm in {len(client.guilds)} servers!")


@client.command()
async def findowner(ctx):
    await ctx.send(f'The owner of this server is: {ctx.guild.owner}')


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):

    await member.kick(reason=reason)
    try:
        await member.send(f'You are kicked from **{ctx.guild.name}.**')
    except:
        await ctx.send('Member has their DMs closed.', delete_after=3.0)
    await ctx.send('Kicked.', delete_after=3.0)


@client.command()
async def poll(ctx, *, args):
    embed = discord.Embed(title='Poll', description=f'{args}')
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')


@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    try:
        await member.send(f'You are banned from **{ctx.guild.name}.**')
    except:
        await ctx.send('Member has their DMs closed.', delete_after=3.0)
    await ctx.send('Banned.', delete_after=3.0)


@client.command()
async def guild(ctx):
    await ctx.send(f'{ctx.guild.name}')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't use that.", delete_after=3.0)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all fields.', delete_after=3.0)
    print(error)



client.run(os.getenv('token'))
