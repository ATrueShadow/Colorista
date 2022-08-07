import os
import discord
from discord import option
from discord import Colour
from discord.utils import get
from contextlib import suppress
import logging
from pymongo import MongoClient
import bson
import dns.resolver

# set up logs

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# end of logs segment

# setting up dns resolver, connecting and getting collection from mongodb

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8"]
db = MongoClient(os.environ["MONGODB_URI"])["colorista"]
print(f"Successfully connected to MongoDB database. (DB collections: {db.list_collection_names()}")
roles = db["roles"]

# end of mongodb segment

# setting up discord bot with member intent

intents = discord.Intents.default()
intents.members = True

bot = discord.Bot(intents=intents)

# end of setup

# bot events

@bot.event
async def on_ready():
	print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.event
async def on_member_join(user: discord.Member):
	if (roles.get(user) != None):
		await user.add_roles(roles[user], reason=f"Colorista assigned role. Done automaticaly by bot on member join.")

# end of events

# bot commands

@bot.slash_command(name="ping")
async def global_command(ctx: discord.ApplicationContext):
	"""Pings the bot and checks if he's alive."""
	await ctx.respond(f'Pong! {ctx.author.mention}')

@bot.slash_command(name="roleassign")
@discord.default_permissions(
	administrator=True,
)
@option(
	"user",
	discord.Member,
	description="The member who is given the role.",
	required=True,
)
@option(
	"role",
	discord.Role,
	description="The role that is given.",
	required=True,
)
async def global_command(ctx: discord.ApplicationContext, user: discord.Member, role: discord.Role):
	"""Assigns editable role to a user. Admin only."""
	if (role.position == 0):
		await ctx.respond(f"Error: Assigning `@everyone` is forbidden.")
		return
#	if (roles.get(user) != None):
#		await ctx.respond(f"Error: This user already has an associated role.")
#		return
#	if (role in roles.values()):
#		await ctx.respond(f"Error: This role is already assigned to someone")
#		return
#	roles[user] = role

	# search for a user
	try:
		roles.find({"userId": user.id})[0]
	except:
		pass
	else: # if try is executed - we found someone
		await ctx.respond("Error: This user already has a Colorista assignable role.")
		return
	# search for a role
	try:
		roles.find({"roleId": role.id})[0]
	except:
		pass
	else: # if try is executed - we found a role
		await ctx.respond("Error: This role is already assigned to someone.")
		return
	if (role.is_bot_managed() or role.managed):
		await ctx.respond(f"Error: Assigning managed roles is forbidden.")
		return
	if (role not in user.roles):
		await user.add_roles(role, reason=f"Colorista assigned role. Done by {ctx.author}")
	roles.insert_one({
		"userId": user.id,
		"roleId": role.id
	})
	await ctx.respond(f'Done.')

@bot.slash_command(name="roletakeback")
@discord.default_permissions(
	administrator=True,
)
@option(
	"user",
	discord.Member,
	description="The member whose role is taken",
	required=True,
)
async def global_command(ctx: discord.ApplicationContext, user: discord.Member):
	"""Takes back a Colorista managed role from specified user. Admin only."""
#	roleToTake = roles.get(user)
#	if (roleToTake == None):
#		await ctx.respond(f"Error: This user has no assigned roles.")
#		return
#	roles.pop(user)
	try:
		roleToTake = get(ctx.guild.roles ,id=(roles.find_one({"userId": user.id})["roleId"]))
	except:
		await ctx.respond("Error: This user doesn't have a Colorista manageble role.")
		return
	roles.delete_one({"userId": user.id})
	await user.remove_roles(roleToTake, reason=f"Remove Colorista managed role. Done by {ctx.author}")
	await ctx.respond(f"Done.")

@bot.slash_command(name="rolecolor")
@option(
	"model",
	choices=["RGB", "RGB HEX", "Name"],
	description="Color model for your color. If you want to set color by name (e. g. 'red', 'blue') - choose Name.",
	required=True,
)
@option(
	"color",
	str,
	description="The color in which the role will be painted.",
	required=True,
)
async def global_command(ctx: discord.ApplicationContext, model: str, *, color: str):
	"""Change color of your role."""
	try:
		roleToChange = get(ctx.guild.roles, id=roles.find_one({"userId": ctx.author.id})["roleId"])#	if (roleToChange == None):
	except:
		await ctx.respond("Error: You don't have a Colorista manageble role.")
		return
	match model:
		case "RGB":
			rgb = color.split(", ", 2)
			await roleToChange.edit(colour=Colour.from_rgb(int(rgb[0]), int(rgb[1]), int(rgb[2])))
		case "RGB HEX":
			rgb = tuple(int((color.lstrip('#'))[i:i+2], 16) for i in (0, 2, 4))
			await roleToChange.edit(colour=Colour.from_rgb(rgb[0], rgb[1], rgb[2]))
		case "Name":
			match color.lower():
				case "red":
					await roleToChange.edit(colour=Colour.red())
				case "green":
					await roleToChange.edit(colour=Colour.green())
				case "blue":
					await roleToChange.edit(colour=Colour.blue())
				case "orange":
					await roleToChange.edit(colour=Colour.orange())
				case "purple":
					await roleToChange.edit(colour=Colour.purple())
				case "white":
					await roleToChange.edit(colour=Colour.from_rgb(255, 255, 255))
				case "black":
					await roleToChange.edit(colour=Colour.black())
				case "discord dark":
					await roleToChange.edit(colour=Colour.dark_theme())
				case "discord light":
					await roleToChange.edit(colour=Colour.embed_background(theme="light"))
				case "default":
					await roleToChange.edit(colour=Colour.default())
				case "magenta":
					await roleToChange.edit(colour=Colour.magenta())
				case "yellow":
					await roleToChange.edit(colour=Colour.yellow())
				case "teal":
					await roleToChange.edit(colour=Colour.teal())
				case "random":
					await roleToChange.edit(colour=Colour.random())
				case _:
					await ctx.respond("Error: Unknown color.")
					return
	await ctx.respond(f"Done.")

@bot.slash_command(name="roleinfo")
@option(
	"role",
	discord.Role,
	description="Role, whose info will be displayed.",
	required=True,
)
async def global_command(ctx: discord.ApplicationContext, role: discord.Role):
	"""Gets and displays given role's info"""
	response = f"Role: {role.name}\n\tID: {role.id}\n\tPosition: {role.position}"
#	with suppress(ValueError): response += f"\n\tAssigned to: {list(roles.keys())[list(roles.values()).index(role)]}"
	with suppress(TypeError): response += f"\n\tAssigned to: {get(ctx.guild.members, id=roles.find_one({'roleId': role.id})['userId']).name}"
	await ctx.respond(response)

# end of commands

bot.run(os.environ["DISCORD_TOKEN"])

# this is gross.
