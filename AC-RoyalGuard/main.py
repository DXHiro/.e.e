import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import asyncio
import motor.motor_asyncio
from utils.mongo import Document
from menus import PromotionRequest
import base64
from easy_pil import Editor, load_image_async, Font
import roblox
import typing
from pkgutil import iter_modules
from utils.utils import get_admin_level, update_member, TRELLO_API_KEY, TRELLO_API_TOKEN
import math
from decouple import config
import requests

"""
UPDATE COOLDOWN CODE TO ADD BACK:
@commands.cooldown(1, 30, commands.BucketType.user)

BGCHECK COOLDOWN CODE TO ADD BACK:
@commands.cooldown(1, 60, commands.BucketType.user)
"""

level = [1135283267801718855, 1135283254732259419, 1135283252236669090, 1135283243420241980, 1135283250273734858, 1135283256640688350, 1135283261107609630, 1135283258049953895]
level_num = [1, 10, 20, 40, 60, 90, 120, 160]

class Bot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def is_owner(self, user: discord.User) -> bool:
		if user.id in [
			857732940788269076, # Hiro
		]:
			return True

		return await super().is_owner(user)

bot = Bot(command_prefix='!', case_insensitive=True, intents=discord.Intents.all(), help_command=None)
bot.is_synced = False

grenadierBot = commands.Bot(command_prefix='!', case_insensitive=True, intents=discord.Intents.all(), help_command=None)
grenadierBot.is_synced = False

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

	mongo_url = config('MONGO_URL')
	bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(mongo_url))
	bot.db = bot.mongo['royalguard']
	bot.admins = Document(bot.db, "admins")
	bot.actions = Document(bot.db, "actions")
	bot.roblox = Document(bot.db, "verifiedusers")
	bot.rankbinds = Document(bot.db, "rankbinds")
	bot.levels = Document(bot.db, "levels")
	bot.moderations = Document(bot.db, "moderations")
	bot.audit = Document(bot.db, "audit")
	bot.shifts = Document(bot.db, "shifts")
	bot.emails = Document(bot.db, "emails")
	bot.errors = Document(bot.db, "errors")

	Extensions = [m.name for m in iter_modules(["cogs"], prefix="cogs.")]
	Events = [m.name for m in iter_modules(["events"], prefix="events.")]

	for extension in Events:
		try:
			await bot.load_extension(extension)
			print(f"Loaded {extension}")
		except Exception as e:
			print(f"Failed to load extension {extension}.", exc_info=e)

	for extension in Extensions:
		try:
			await bot.load_extension(extension)
			print(f"Loaded {extension}")
		except Exception as e:
			print(f"Failed to load extension {extension}.", exc_info=e)

	member_report.start()
	check_promotions.start()
	robloxLogin.start()
	checkModerations.start()
	checkAuditLog.start()

	if not bot.is_synced:
		await bot.tree.sync()
		bot.is_synced = True

	async def send_or_edit_message(channel, embed, view, messageID):
		message = await channel.fetch_message(messageID)
		if message is not None:
			await message.edit(embed=embed, view=view)
		else:
			message = await channel.send(embed=embed, view=view)

	supportChannel = bot.get_channel(1091095337214689310)
	rulesChannel = bot.get_channel(1069666288852537557)
	RMPChannel = bot.get_channel(1145697665875710002)
	AABChannel = bot.get_channel(1073704480664723566)
	IFDChannel = bot.get_channel(1151598509313765466)
	ETSChannel = bot.get_channel(1120757245702062100)
	FCOChannel = bot.get_channel(1002323630652395580)
	RGGChannel = bot.get_channel(1114513081947672657)
	UKSFChannel = bot.get_channel(1111941114614796290)
	"""
	await supportChannel.purge()

	botUser = bot.get_user(int(1142151020928041130))

	def is_user_message(message):
		return message.author == botUser
	
	deleted = await rulesChannel.purge(check=is_user_message)
	"""

	verificationTickets = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="Press the **Verify / Reverify** button to verify or reverify your ROBLOX account.", color=discord.Color.dark_blue())
	verificationTickets.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)

	reportTickets = discord.Embed(title="REPORT TICKETS", description="Press the **🚨 Create Ticket** button for tickets to report an incident or other users.", color=discord.Color.dark_blue())
	reportTickets.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)

	otherTickets = discord.Embed(title="OTHER TICKETS", description="Press the **🚨 Create Ticket** button for tickets regarding other matters.", color=discord.Color.dark_blue())
	otherTickets.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)

	"""
	await supportChannel.send(embed=reportTickets, view=CreateTicket(2))
	await supportChannel.send(embed=otherTickets, view=CreateTicket(3))

	await rulesChannel.send(embed=verificationTickets, view=VerifyReverify())
	"""

	await send_or_edit_message(supportChannel, reportTickets, CreateTicket(2), 1145697199385231421)
	await send_or_edit_message(supportChannel, otherTickets, CreateTicket(3), 1145697206041575484)
	await send_or_edit_message(rulesChannel, verificationTickets, VerifyReverify(), 1145696997786005525)
	await send_or_edit_message(RMPChannel, verificationTickets, VerifyReverify(), 1145697762369880205)
	await send_or_edit_message(AABChannel, verificationTickets, VerifyReverify(), 1142153208521822358)
	await send_or_edit_message(IFDChannel, verificationTickets, VerifyReverify(), 1152638260196159558)
	await send_or_edit_message(ETSChannel, verificationTickets, VerifyReverify(), 1142153323588374558)
	await send_or_edit_message(FCOChannel, verificationTickets, VerifyReverify(), 1142153370212245604)
	await send_or_edit_message(RGGChannel, verificationTickets, VerifyReverify(), 1142153437753135205)
	await send_or_edit_message(UKSFChannel, verificationTickets, VerifyReverify(), 1142153473811566643)

	bmtTickets = discord.Embed(title="**ALFIE'S BASIC MILITARY TRAINING SYSTEM V1**", description="Press the **Start BMT** button to start your BMT.", color=0xf07c3e)
	bmtTickets.set_author(name=bot.user.name, icon_url=bot.user.avatar.url)
	channel = bot.get_channel(1138958292928954368)
	await send_or_edit_message(channel, bmtTickets, BasicMilitaryTraining(), 1145697812902846484)
	"""
	await channel.purge()
	await channel.send(embed=bmtTickets, view=BasicMilitaryTraining())
	"""

@bot.before_invoke
async def AutoDefer(ctx: commands.Context):
	if ctx.command:
		if ctx.command.extras.get("ephemeral") is True:
			if ctx.interaction:
				await ctx.defer(ephemeral=True)
		elif ctx.command.extras.get("ignoreDefer") is True:
			pass
		else:
			await ctx.defer()

	if ctx.command.enabled == False:
		raise discord.ext.commands.errors.DisabledCommand
	elif not await get_admin_level(bot, ctx.guild, ctx.author.id) >= ctx.command.extras['levelPermissionNeeded']:
		insufficientPermissions = discord.Embed(title = "Warning - Insufficient Permissions", description=f"This command is limited to the admin level **{'Infinity' if math.isinf(ctx.command.extras['levelPermissionNeeded']) else ctx.command.extras['levelPermissionNeeded']}**!", color = discord.Color.dark_gold())
		insufficientPermissions.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
		await ctx.send(embed=insufficientPermissions)
		raise discord.ext.commands.errors.CommandNotFound

@bot.event
async def on_member_join(member):
	await update_member(bot, member, member.guild)

@grenadierBot.event
async def on_ready():
	await grenadierBot.change_presence(activity=discord.Game(name='discord.gg/alfieba'))

	if not grenadierBot.is_synced:
		await grenadierBot.tree.sync()
		grenadierBot.is_synced = True

	print("--- Grenadier Bot Ready ---")

auditDict = {
	"ba": {
		"group": 15356653,
		"channel": 1146507460962697287
	},
	"ets": {
		"group": 15549981,
		"channel": 1145816367854014564
	},
	"otc": {
		"group": 16185446,
		"channel": 1145816131622420603
	},
	"rmp": {
		"group": 16195172,
		"channel": 1145816160043016212
	},
	"rgg": {
		"group": 32590701,
		"channel": 1145816185405984838
	},
	"uksf": {
		"group": 15964855,
		"channel": 1145816239499915314
	},
	"ifd": {
		"group": 15960178,
		"channel": 1145816287059116122
	},
	"aab": {
		"group": 15964799,
		"channel": 1145816410656866445
	},
}

@tasks.loop(minutes=1)
async def checkAuditLog():
	for group in auditDict:
		api_url = f'http://aba-ranking-services-fad267650515.herokuapp.com/auditlookup?key=psxap8ikeyhasawnwfs2ua3ynoiuqwanyeuo1ang7oisuhqw&group={auditDict.get(group)["group"]}'
		response = requests.get(api_url)
		audit_data = response.json()

		api_url = f'https://groups.roblox.com/v1/groups/{auditDict.get(group)["group"]}/roles'
		response = requests.get(api_url)
		groups_data = response.json()

		auditChannel = bot.get_channel(auditDict.get(group)["channel"])

		for item in audit_data:
			event_identifier = f"{auditDict.get(group)['group']}:{item['actionType']}:{item['created']}"

			default_audit_item = {
					'_id': event_identifier,
				}
			
			dataset = await bot.audit.find_by_id(event_identifier)
			if dataset:
				continue
			else:
				await bot.audit.insert(default_audit_item)

			if item['actionType'] == "Change Rank":
				oldRankId = 0
				newRankId = 0
				promotion = False
				actionTaken = "Demoted"

				for role in groups_data['roles']:
					if role['id'] == item['description']['OldRoleSetId']:
						oldRankId = role['rank']
					elif role['id'] == item['description']['NewRoleSetId']:
						newRankId = role['rank']

				if newRankId > oldRankId:
					promotion = True
					actionTaken = "Promoted"

				auditEmbed = discord.Embed(
					description=f"**Action Type:** {item['actionType']}\n**Target:** {item['description']['TargetName']} | {item['description']['TargetId']}\n**{actionTaken} by:** {item['actor']['user']['username']} | {item['actor']['user']['userId']} | {item['actor']['role']['name']}\n**Old Rank:** {item['description']['OldRoleSetName']}\n**New Rank:** {item['description']['NewRoleSetName']}\n**Time:** {item['created']}"
				)
				if promotion == True:
					auditEmbed.title="Promotion"
					auditEmbed.color=discord.Color.green()
				else:
					auditEmbed.title="Demotion"
					auditEmbed.color=discord.Color.red()
				await auditChannel.send(embed=auditEmbed)
			elif item['actionType'] == "Remove Member" or item['actionType'] == "Accept Join Request" or item['actionType'] == "Decline Join Request":
				if item['actionType'] == "Remove Member":
					actionTaken = "Exiled"
				elif item['actionType'] == "Accept Join Request":
					actionTaken = "Accepted"
				else:
					actionTaken = "Declined"
				auditEmbed = discord.Embed(
					description=f"**Action Type:** {item['actionType']}\n**Target:** {item['description']['TargetName']} | {item['description']['TargetId']}\n**{actionTaken} by:** {item['actor']['user']['username']} | {item['actor']['user']['userId']} | {item['actor']['role']['name']}\n**Time:** {item['created']}"
				)
				if item['actionType'] == "Remove Member":
					auditEmbed.title="Exile"
					auditEmbed.color=discord.Color.red()
				elif item['actionType'] == "Accept Join Request":
					auditEmbed.title="Join Request Accepted"
					auditEmbed.color=discord.Color.green()
				else:
					auditEmbed.title="Join Request Declined"
					auditEmbed.color=discord.Color.red()
				await auditChannel.send(embed=auditEmbed)
			elif item['actionType'] == "Post Status":
				actionTaken = "Posted"
				auditEmbed = discord.Embed(
					description=f"**Action Type:** {item['actionType']}\n**Text:** {item['description']['Text']}\n**{actionTaken} by:** {item['actor']['user']['username']} | {item['actor']['user']['userId']} | {item['actor']['role']['name']}\n**Time:** {item['created']}"
				)
				auditEmbed.title="Group Shout Updated"
				auditEmbed.color=discord.Color.yellow()
				await auditChannel.send(embed=auditEmbed)
			elif item['actionType'] == "Save Place" or item['actionType'] == "Publish Place":
				if item['actionType'] == "Save Place":
					actionTaken = "Saved"
				else:
					actionTaken = "Published"
				auditEmbed = discord.Embed(
					description=f"**Action Type:** {item['actionType']}\n**Game Information:** {item['description']['AssetName']} | {item['description']['AssetId']} | Version Number: {item['description']['VersionNumber']}\n**{actionTaken} by:** {item['actor']['user']['username']} | {item['actor']['user']['userId']} | {item['actor']['role']['name']}\n**Time:** {item['created']}"
				)
				if item['actionType'] == "Save Place":
					auditEmbed.title="Game Saved"
					auditEmbed.color=discord.Color.gold()
				else:
					auditEmbed.title="Game Published"
					auditEmbed.color=discord.Color.green()
				await auditChannel.send(embed=auditEmbed)
			elif item['actionType'] == "Spend Group Funds":
				actionTaken = "Spent"
				auditEmbed = discord.Embed(
					description=f"**Action Type:** {item['actionType']}\n**Information:** Amount: {item['description']['Amount']} | {item['description']['ItemDescription']}\n**{actionTaken} by:** {item['actor']['user']['username']} | {item['actor']['user']['userId']} | {item['actor']['role']['name']}\n**Time:** {item['created']}"
				)
				auditEmbed.title="Group Funds Spent"
				auditEmbed.color=discord.Color.gold()
				await auditChannel.send(embed=auditEmbed)
			elif item['actionType'] == "Create Group Asset" or item['actionType'] == "Update Group Asset"  or item['actionType'] == "Configure Group Asset":
				if item['actionType'] == "Create Group Asset":
					actionTaken = "Created"
				elif item['actionType'] == "Update Group Asset":
					actionTaken = "Updated"
				else:
					actionTaken = "Configured"
				auditEmbed = discord.Embed(
					description=f"**Action Type:** {item['actionType']}\n**Asset Information:** {item['description']['AssetName']} | {item['description']['AssetId']}\n**{actionTaken} by:** {item['actor']['user']['username']} | {item['actor']['user']['userId']} | {item['actor']['role']['name']}\n**Time:** {item['created']}"
				)
				if item['actionType'] == "Create Group Asset":
					auditEmbed.title="Asset Created"
					auditEmbed.color=discord.Color.green()
				elif item['actionType'] == "Update Group Asset":
					auditEmbed.title="Asset Updated"
					auditEmbed.color=discord.Color.yellow()
				else:
					auditEmbed.title="Asset Configured"
					auditEmbed.color=discord.Color.yellow()
				await auditChannel.send(embed=auditEmbed)
			else:
				print(item['actionType'])

class EnterRobloxUsername(discord.ui.Modal, title="BRITISH ARMY VERIFICATION SYSTEM V5"):
	username = discord.ui.TextInput(label='Please enter your ROBLOX username', placeholder="Only enter your ROBLOX username, e.g: AlfieDespair", max_length=None,
								style=discord.TextStyle.short, required=True)

	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer()
		self.stop()

class BeginVerification(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.modal: typing.Union[None, EnterRobloxUsername] = None

	@discord.ui.button(label='Begin Verification', style=discord.ButtonStyle.green)
	async def beginVerificationButton(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.modal = EnterRobloxUsername()
		await interaction.response.send_modal(self.modal)
		await self.modal.wait()
		await retrieveRobloxDetails(interaction, self.modal.username.value)

async def retrieveRobloxDetails(interaction, username):
	retrievingDetails = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="Retrieving details from ROBLOX", color=discord.Color.dark_blue())
	retrievingDetails.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
	await interaction.edit_original_response(embed=retrievingDetails, view=None)
	try:
		user = await client.get_user_by_username(username, expand=True)
		confirmationOfAccount = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description=f"Is this your ROBLOX account?\n\nUsername : [{user.name}](https://www.roblox.com/users/{user.id}/profile)\nROBLOX Profile : https://www.roblox.com/users/{user.id}/profile", color=discord.Color.dark_blue())
		confirmationOfAccount.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		return await interaction.edit_original_response(embed=confirmationOfAccount, view=AccountConfirmation(user))
	except roblox.UserNotFound:
		usernameNotFound = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="The ROBLOX account username you have entered does not exist.\n\nPlease try again by clicking the button below.", color=discord.Color.dark_blue())
		usernameNotFound.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		return await interaction.edit_original_response(embed=usernameNotFound, view=ReInputUsername())

class ReInputUsername(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.modal: typing.Union[None, EnterRobloxUsername] = None

	@discord.ui.button(label='Input ROBLOX Username', style=discord.ButtonStyle.blurple)
	async def beginVerificationButton(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.modal = EnterRobloxUsername()
		await interaction.response.send_modal(self.modal)
		await self.modal.wait()
		await retrieveRobloxDetails(interaction, self.modal.username.value)

class UpdateRoles(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label='Update Roles', style=discord.ButtonStyle.green)
	async def update(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer(ephemeral=True, thinking=True)
		updateEmbed = bot.get_cog("Verification").update(interaction, None, None)
		await interaction.edit_original_response(embed=updateEmbed)

class JoinedGame(discord.ui.View):
	def __init__(self, robloxID):
		super().__init__(timeout=None)
		self.robloxID = robloxID

	@discord.ui.button(label='Done', style=discord.ButtonStyle.green)
	async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer(ephemeral=True, thinking=True)
		verifyingUser = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="Verifying user..", color=discord.Color.dark_blue())
		verifyingUser.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		await interaction.edit_original_response(embed=verifyingUser, view=None)
		TRELLO_LIST_ID = "644569fed76bf48e8c67269f"
		url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
		response = requests.get(url)
		data = response.json()
		notVerified = False
		for user in data:
			if int(user['name'].split(":")[0]) == interaction.user.id:
				notVerified = True
				break
		if notVerified == False:
			notVerifiedEmbed = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="Successfully verified your ROBLOX account.", color=discord.Color.dark_blue())
			notVerifiedEmbed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
			await interaction.edit_original_response(embed=notVerifiedEmbed, view=None)

			verificationLog = discord.Embed(title="Alfie Verification Log", color=discord.Color.dark_blue())
			verificationLogs = bot.get_channel(1127284180062056488)

			robloxUser = await client.get_user(self.robloxID)
			discordUser = interaction.user

			verificationLog.description = f"Method: Roblox Game\nDiscord Account : {discordUser.mention} | {discordUser.display_name} | {discordUser.name}#{discordUser.discriminator}\nRoblox Account : {robloxUser.name}"
			verificationLog.set_author(name=discordUser.name, icon_url=discordUser.avatar)
			await verificationLogs.send(embed=verificationLog)

			default_roblox_item = {
				'_id': discordUser.id,
				'roblox': robloxUser.id,
				'banned': False,
				'suspended': False,
			}
			
			dataset = await bot.roblox.find_by_roblox(robloxUser.id)
			if len(dataset) >= 1:
				banned = any(item['banned'] for item in dataset)
				suspended = any(item['suspended'] for item in dataset)
				default_roblox_item = {
					'_id': discordUser.id,
					'roblox': robloxUser.id,
					'banned': banned,
					'suspended': suspended,
				}
				await bot.roblox.delete_by_id(discordUser.id)

			await bot.roblox.insert(default_roblox_item)
			for guild in bot.guilds:
				await update_member(bot, discordUser, guild)
		else:
			notVerifiedEmbed = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="Please join the ROBLOX game to verify, you have not verified yourself on the game yet.\n\nROBLOX Game: https://www.roblox.com/games/11722765504/Verification\n\nClick on the button below once you have successfully verified in the game.", color=discord.Color.dark_gold())
			notVerifiedEmbed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
			return await interaction.edit_original_response(embed=notVerifiedEmbed, view=JoinedGame(self.robloxID))

class AccountConfirmation(discord.ui.View):
	def __init__(self, username, firstTime=False):
		super().__init__(timeout=None)
		self.username = username
		self.firstTime = firstTime

	@discord.ui.button(label='Yes', style=discord.ButtonStyle.green)
	async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer(ephemeral=True, thinking=True)
		if self.firstTime == True:
			alreadyVerified = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="You are already verified. If you wish to retrieve new roles or update yourself, please use the button below.", color=discord.Color.dark_gold())
			alreadyVerified.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
			return await interaction.edit_original_response(embed=alreadyVerified, view=UpdateRoles())
		else:
			TRELLO_LIST_ID = "644569fed76bf48e8c67269f"
			url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
			response = requests.get(url)
			data = response.json()
			for user in data:
				if int(user['name'].split(":")[0]) == interaction.user.id:
					url = f"https://api.trello.com/1/cards/{user['id']}?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
					response = requests.delete(url)
			card_name = f"{interaction.user.id}:{self.username.id}:{interaction.user.name}:{interaction.user.discriminator}"
			url = f'https://api.trello.com/1/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}&idList={TRELLO_LIST_ID}&name={card_name}'
			requests.post(url)
			confirmationOfAccount = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="Please join this game to complete verification.\n\nhttps://www.roblox.com/games/11722765504/Verification\n\nClick on the button below once you have successfully verified in the game.", color=discord.Color.dark_blue())
			confirmationOfAccount.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
			return await interaction.edit_original_response(embed=confirmationOfAccount, view=JoinedGame(self.username.id))

	@discord.ui.button(label='No', style=discord.ButtonStyle.red)
	async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
		self.modal = EnterRobloxUsername()
		await interaction.response.send_modal(self.modal)
		await self.modal.wait()
		await retrieveRobloxDetails(interaction, self.modal.username.value)

async def gameVerification(interaction: discord.Interaction):	
	dataset = await bot.roblox.find_by_id(interaction.user.id)
	if dataset:
		user = await client.get_user(dataset['roblox'])
		confirmationOfAccount = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description=f"Is this your ROBLOX account?\n\nUsername : [{user.name}](https://www.roblox.com/users/{user.id}/profile)\nROBLOX Profile : https://www.roblox.com/users/{user.id}/profile", color=discord.Color.dark_blue())
		confirmationOfAccount.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		return await interaction.edit_original_response(embed=confirmationOfAccount, view=AccountConfirmation(user, firstTime=True))
	else:
		beginVerification = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="Please click the button below to begin verification.", color=discord.Color.dark_blue())
		beginVerification.set_author(name=interaction.user.name, icon_url=interaction.user.display_avatar)
		await interaction.edit_original_response(embed=beginVerification, view=BeginVerification())

class BasicMilitaryTraining(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label='Start BMT', style=discord.ButtonStyle.green)
	async def bmt(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer()
		dataset = await bot.roblox.find_by_id(interaction.user.id)
		if dataset is None:
			notVerified = discord.Embed(title="Not Verified", description="You need to verify your ROBLOX account in order to complete your BMT.", color=0xf07c3e)
			notVerified.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
			return await interaction.followup.send(embed=notVerified, ephemeral=True)
		else:
			robloxID = dataset['roblox']
			api_url = f'https://groups.roblox.com/v2/users/{robloxID}/groups/roles'
			response = requests.get(api_url)
			groups_data = response.json()['data']

			group_id = 15356653
			userBARank = 0

			for group in groups_data:
				if group['group']['id'] == group_id:
					userBARank = group['role']['rank']
					break
			
			if userBARank != 1:
				notBMT = discord.Embed(title="Not OR-1", description="You need to be ranked OR-1 in https://www.roblox.com/groups/15356653/ABA-British-Army#!/about in order to complete your BMT.", color=0xf07c3e)
				notBMT.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
				return await interaction.followup.send(embed=notBMT, ephemeral=True)
		
		await bmtTicket(interaction, robloxID)

class CustomBMT(discord.ui.Select):
	def __init__(self, user_id, options: list):
		self.user_id = user_id
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		# The placeholder is what will be shown when no option is chosen
		# The min and max values indicate we can only pick one of the three options
		# The options parameter defines the dropdown options. We defined this above
		super().__init__(placeholder='Select an Answer', min_values=1, max_values=1, options=optionList)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.defer()
		if len(self.values) == 1:
			self.view.value = self.values[0]
			self.placeholder = self.view.value.title()
		else:
			self.view.value = self.values

		self.disabled = True
		self.view.stop()

class CustomBMTMenu(discord.ui.View):
	def __init__(self, user_id, options: list):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id

		self.add_item(CustomBMT(self.user_id, options))

questionsDict = {
	1: {
		"question": "Who is the Chief of Defence Staff?",
		"answer": "AlfieDespair",
		"options": [
			"VoidDespair",
			"CrillioDespair",
			"MatDespair",
			"AlfieDespair"
		]
	},
	2: {
		"question": "Who is the Vice Chief of Defence Staff?",
		"answer": "MatDespair",
		"options": [
				"EpicDespair",
				"RickDespair",
				"MatDespair",
				"AlfieDespair"
			]
	},
	3: {
		"question": "Who is the Chief of General Staff?",
		"answer": "EpicDespair",
		"options": [
					"zapalangdzz3",
					"greenbirth666",
					"EpicDespair",
					"MexicanDespair"
				]
	},
	4: {
		"question": "What does BMT stand for?",
		"answer": "Basic Military Training",
		"options": [
			"British Military Conduct",
			"British Military Codex",
			"Basic Military Training"
		]
	},
	5: {
		"question": "Is Alfie the best coder?",
		"answer": "Yes",
		"options": [
				"Yes",
				"No"
			]
	},
}

async def bmtTicket(ctx, robloxID):
	category = discord.utils.get(ctx.guild.categories, id=1138958811105865739)
	ticketType = "bmt"
	ticketCreator = ctx.user

	ticketTypes = []

	for channel in category.channels:
		if isinstance(channel, discord.TextChannel):
			if str(ticketCreator.id) in channel.topic:
				ticketTypes.append(channel.name.split('-')[0])
	if ticketType in ticketTypes:
		openTicket = discord.Embed(title="BMT Ticket", description=f"There is already an open ticket at {channel.mention}", color=0xf07c3e)
		openTicket.set_author(name=ticketCreator.name, icon_url=ticketCreator.avatar)
		return await ctx.followup.send(embed=openTicket, ephemeral=True)

	ticket_number = 1

	for channel in category.channels:
		if isinstance(channel, discord.TextChannel):
			if channel.name.split('-')[0] == ticketType:
				ticket_number += 1
	
	name = f"{ticketType}-{ticket_number}"

	overwrites = {
				ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
				ctx.user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
			}
	channel = await ctx.guild.create_text_channel(name = name, topic=ctx.user.id, overwrites = overwrites, category=category)

	bmtCreated = discord.Embed(title="BMT Ticket", description=f"Your BMT ticket has been created. The ticket number is {channel.mention}", color=0xf07c3e)
	bmtCreated.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
	await ctx.followup.send(embed=bmtCreated, ephemeral=True)
	
	welcomeEmbed = discord.Embed(title=f"**{channel.name.split('-')[0].upper()} TICKET**", color=0xf07c3e)

	welcomeEmbed.description="Hello! This is your ticket to complete your BMT. We will be asking you several questions. If you manage to achieve above 60% then you will be automatically ranked and you will have passed your BMT."
	
	welcomeEmbed.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
	await channel.send(ctx.user.mention, embed=welcomeEmbed)

	def authorCheck(m):
		return m.author == ctx.user and m.channel == channel

	percent = 0

	for index, (question, description) in enumerate(questionsDict.items(), start=1):
		options = []
		question_info = questionsDict.get(question)
		optionCount = 0
		for answer in question_info["options"]:
			optionCount += 1
			option = discord.SelectOption(label=answer, value=answer)
			options.append(option)

		view = CustomBMTMenu(ctx.user.id, options)

		questionInput = discord.Embed(title="Alfie's Basic Military Training 1.0", description=question_info["question"], color=0xd177f7)
		questionInput.set_footer(text=f"Respond with cancel to end this prompt.", icon_url=bot.user.avatar.url)
		await channel.send(f"Hello {ctx.user.mention}", embed=questionInput, view=view)

		timeout = await view.wait()
		if timeout:
			return

		if view.value == question_info["answer"]:
			percent += 20

	passed = False
	if percent >= 60:
		passed = True
		successfullyPassed = discord.Embed(title="Alfie's Basic Military Training 1.0", description=f"Successfully passed your Basic Military Training.\n\nPercentage: {percent}%\n\nThis ticket will be closed momentarily.", color=0x7efc00)
		await channel.send(f"Hello {ctx.user.mention}", embed=successfullyPassed)
		api_url = f'https://aba-ranking-services-fad267650515.herokuapp.com/promote?key=psxap8ikeyhasawnwfs2ua3ynoiuqwanyeuo1ang7oisuhqw&userid={robloxID}'
		response = requests.get(api_url)
		await asyncio.sleep(3)
		await channel.delete()
	else:
		failed = discord.Embed(title="Alfie's Basic Military Training 1.0", description=f"You failed your Basic Military Training\n\nPercentage: {percent}%\n\nThis ticket will be closed momentarily.", color=0xd30013)
		await channel.send(f"Hello {ctx.user.mention}", embed=failed)
		await asyncio.sleep(3)
		await channel.delete()

	await update_member(bot, ctx.user, ctx.user.guild)

	robloxUser = await client.get_user(robloxID)

	bmtLogs = bot.get_channel(1138957939563049070)
	BMTLog = discord.Embed(title="Basic Military Training Log", description=f"Username: {robloxUser.name}\nPercentage: {percent}%\nPassed: {passed}", color=0xf07c3e)
	BMTLog.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
	return await bmtLogs.send(embed=BMTLog)

@grenadierBot.event
async def on_message(message):
	if message.author.bot:
		return
	
	if message.channel.id == 1069662277600563273:
		if not message.content.startswith("!"):
			if not message.author.bot:
				dataset = await bot.levels.find_by_id(message.author.id)
				if dataset:
					xp = dataset['xp']
					lvl = dataset['level']

					increased_xp = xp+25
					new_level = int(increased_xp/100)

					dataset['xp']=increased_xp

					await bot.levels.upsert(dataset)

					if new_level > lvl:
						levelChannel = grenadierBot.get_channel(1069665315044216902)
						await levelChannel.send(f"Congratulations {message.author.mention}! you just advanced to level {new_level}!\nKeep it up!")

						dataset = await bot.levels.find_by_id(message.author.id)
						dataset['level']=new_level
						dataset['xp']=0

						await bot.levels.upsert(dataset)
				
						for i in range(len(level)):
							if new_level == level_num[i]:
								role = message.author.guild.get_role(level[i])
								if role:
									await message.author.add_roles(role)
				else:
					default_level_item = {
						'_id': message.author.id,
						'xp': 0,
						'level': 0,
					}
					await bot.levels.insert(default_level_item)

import discord.ext.commands.errors

from roblox import Client
client = Client()

@grenadierBot.event
async def on_member_join(member):
	joinLogs = grenadierBot.get_channel(1069671230086586439)

	background = Editor("pic1.jpg")
	profile_image = await load_image_async(str(member.display_avatar.url))

	profile = Editor(profile_image).resize((175, 175)).circle_image()
	poppins = Font.poppins(size=30)

	poppins_small = Font.poppins(size=20)

	background.paste(profile, (315, 90))
	background.ellipse((315, 90), 175, 175, outline="#df6b6a", stroke_width=5)

	ima = Editor("JOIN_BACKGROUND_DARK.png")
	background.blend(image=ima, alpha=0.5, on_top=False)

	background.text((400, 310), f"{member.name} just joined the server", color="#df6b6a", font=poppins, align="center")
	background.text((400, 360), f"Member #{len(member.guild.members)}", color="#df6b6a", font=poppins_small, align="center")
	
	file = discord.File(fp=background.image_bytes, filename="pic1.jpg")
	await joinLogs.send(f"{member.mention}, has joined the discord server!", file=file)

@grenadierBot.event
async def on_member_remove(member):
	leaveLogs = grenadierBot.get_channel(1112118699655176232)

	await leaveLogs.send(f"**{member.mention} just left the server 🙁**")

last_run = None
	
@tasks.loop(seconds=5)
async def member_report():
	global last_run
	now = datetime.datetime.now()
	target_time = datetime.time(hour=22, minute=00, second=0)
	time = now.time().replace(microsecond=0)
	time = time.replace(second=0)
	if time == target_time and last_run != now.date():
		last_run = now.date()

		memberReportChannel = bot.get_channel(1069671463302475827)
		
		memberReport = discord.Embed(title="Member Report", color=0x6fff3e, timestamp=datetime.datetime.now())

		api_url = 'https://groups.roblox.com/v1/groups/15356653'
		response = requests.get(api_url)
		groups_data = response.json()

		memberReport.description = f"**{groups_data['name']}**\nMember Count : {groups_data['memberCount']}\n\n"

		api_url = f'https://groups.roblox.com/v1/groups/{15356653}/roles'
		response = requests.get(api_url)
		groups_data = response.json()
		for role in groups_data['roles']:
			if role['name'] == "Guest":
				continue
			memberReport.description += f"**{role['name']}** : {role['memberCount']}\n"

		await memberReportChannel.send(embed=memberReport)

@tasks.loop(seconds=5)
async def check_promotions():
	TRELLO_LIST_ID = "6446baf6199a70adf2ccfca8"

	url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
	response = requests.get(url)
	data = response.json()
	for user in data:
		userID = int(user['name'].split(":")[0])
		rank = int(user['name'].split(":")[1])
		promoter = int(user['name'].split(":")[2])
		event = str(user['name'].split(":")[3])
		promotionRequest = discord.Embed(title="Alfie Promotion Request", color=0x498baf)
		rankRequests = bot.get_channel(1069671290685886534)

		url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
		response = requests.get(url)
		data = response.json()
		for user in data:
			if str(user['name']) == f"{userID}:{rank}:{promoter}:{event}":
				url = f"https://api.trello.com/1/cards/{user['id']}?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
				response = requests.delete(url)
				break

		user = await client.get_user(userID)
		api_url = f'https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user.id}&size=48x48&format=Png&isCircular=true'
		response = requests.get(api_url)
		avatar_data = response.json()['data']
		for avatar in avatar_data:
			avatarURL = avatar['imageUrl']
		promotionRequest.set_author(name=user.name, icon_url=avatarURL)

		promoter = await client.get_user(promoter)

		api_url = f'https://groups.roblox.com/v2/users/{user.id}/groups/roles'
		response = requests.get(api_url)
		groups_data = response.json()['data']

		for group in groups_data:
			if group['group']['id'] == 15356653:
				originalRank = group['role']['name']
				break

		api_url = f'https://groups.roblox.com/v1/groups/{15356653}/roles'
		response = requests.get(api_url)
		groups_data = response.json()

		for role in groups_data['roles']:
			if role['rank'] == rank:
				nextRank = role['name']

		promotionRequest.description = f"USER PROMOTED FROM **{originalRank}** TO **{nextRank}**\n PROMOTER: **{promoter.name}**\n EVENT TYPE: **{event}**"
		promotionRequest.set_footer(text="Debugging info : N/A")
		await rankRequests.send(embed=promotionRequest, view=PromotionRequest(bot, user, originalRank, nextRank, promoter))

@tasks.loop(seconds=5)
async def robloxLogin():
	TRELLO_LIST_ID = "64b28b818d171d218078961e"

	url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
	response = requests.get(url)
	data = response.json()
	for user in data:
		userID = int(user['name'].split(":")[0])
		discordIDEncoded = user['name'].split(":")[1]
		discordID = int(base64.b64decode(discordIDEncoded))
		verificationLog = discord.Embed(title="Alfie Verification Log", color=discord.Color.dark_blue())
		verificationLogs = bot.get_channel(1127284180062056488)

		url = f"https://api.trello.com/1/lists/{TRELLO_LIST_ID}/cards?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
		response = requests.get(url)
		data = response.json()
		for user in data:
			if str(user['name']) == f"{userID}:{discordIDEncoded}":
				url = f"https://api.trello.com/1/cards/{user['id']}?key={TRELLO_API_KEY}&token={TRELLO_API_TOKEN}"
				response = requests.delete(url)
				break

		robloxUser = await client.get_user(userID)
		discordUser = bot.get_user(discordID)

		verificationLog.description = f"Method: Roblox Login\nDiscord Account : {discordUser.mention} | {discordUser.display_name} | {discordUser.name}#{discordUser.discriminator}\nRoblox Account : {robloxUser.name}"
		verificationLog.set_author(name=discordUser.name, icon_url=discordUser.avatar)
		await verificationLogs.send(embed=verificationLog)

		default_roblox_item = {
			'_id': discordUser.id,
			'roblox': robloxUser.id,
			'banned': False,
			'suspended': False,
		}
		
		dataset = await bot.roblox.find_by_roblox(robloxUser.id)
		if len(dataset) >= 1:
			banned = any(item['banned'] for item in dataset)
			suspended = any(item['suspended'] for item in dataset)
			default_roblox_item = {
				'_id': discordUser.id,
				'roblox': robloxUser.id,
				'banned': banned,
				'suspended': suspended,
			}
			await bot.roblox.delete_by_id(discordUser.id)

		await bot.roblox.insert(default_roblox_item)
		for guild in bot.guilds:
			await update_member(bot, discordUser, guild)

@tasks.loop(seconds=5)
async def checkModerations():
	currentTime = datetime.datetime.now()
	dataset = await bot.moderations.get_all()
	for member in dataset:
		for moderation in member['moderations']:
			id = moderation['Id']
			type = moderation['Type']
			duration = moderation['Duration']
			time = moderation['Time']
			server = moderation['Server']

		if len(member['moderations']) == 0:
			await bot.moderations.delete_by_id(member['_id'])
			continue

		duration = datetime.timedelta(hours=duration)

		if currentTime - time >= duration:
			pass
		else:
			continue

		guild = bot.get_guild(server)

		if type == "Watchlist":
			if guild is not None:
				member = guild.get_member(member['_id'])
				if member is not None:
					watchlistRole = guild.get_role(1133116078243971092)
					if watchlistRole and watchlistRole in member.roles:
						await member.remove_roles(watchlistRole)
		elif type == "Suspension":
			dataset = await bot.roblox.find_by_id(member['_id'])
			ID = member['_id']
			if dataset:
				default_action_item = {
					'_id': member['_id'],
					'roblox': dataset['roblox'],
					'banned': dataset['banned'],
					'suspended': False
				}

				await bot.roblox.update(default_action_item)

				for guild in bot.guilds:
					await update_member(bot, member, guild)
		elif type == "Ban":
			member = bot.get_user(member['_id'])
			dataset = await bot.roblox.find_by_id(member.id)

			if dataset:
				default_action_item = {
					'_id': member.id,
					'roblox': dataset['roblox'],
					'banned': False,
					'suspended': dataset['suspended']
				}

				await bot.roblox.update(default_action_item)

			for guild in bot.guilds:
				try:
					await guild.unban(member)
				except:
					pass

		selected_item = None
		selected_items = []
		item_index = 0

		async for item in bot.moderations.db.find({'moderations': {'$elemMatch': {'Id': id}}}):
			for index, _item in enumerate(item['moderations']):
				if _item['Id'] == id:
					selected_item = _item
					selected_items.append(_item)
					parent_item = item
					item_index = index
					break

		if selected_item is None:
			return

		if len(selected_items) > 1:
				return

		parent_item['moderations'].remove(selected_item)
		await bot.moderations.update_by_id(parent_item)

@grenadierBot.hybrid_command(description="Get a link to the leaderboard")
async def levels(ctx):
	range_num = 5

	dataset = await bot.levels.get_all()

	l = {}
	total_xp = []

	for userid in dataset:
		xp = userid['xp']+(userid['level']*100)

		l[xp] = f"{userid['_id']};{userid['level']};{userid['xp']}"
		total_xp.append(xp)

	total_xp = sorted(total_xp, reverse=True)
	index=1

	mbed = discord.Embed(
	  title="Leaderboard Command Results",
	  color=discord.Color.dark_blue()
	)

	for amt in total_xp:
		id_ = int(str(l[amt]).split(";")[0])
		level = int(str(l[amt]).split(";")[1])
		xp = int(str(l[amt]).split(";")[2])

		member = await bot.fetch_user(id_)

		if member is not None:
			name = member.name
			mbed.add_field(name=f"{index}. {name}",
			value=f"**Level: {level} | XP: {xp}**", 
			inline=False)

			if index == range_num:
				break
			else:
				index += 1

	await ctx.send(embed = mbed, ephemeral=True)
	
@grenadierBot.hybrid_command(description="Get your rank or another member's rank")
@app_commands.describe(member="Target @member")
async def rank(ctx, member: discord.Member=None):
	userr = member or ctx.author

	dataset = await bot.levels.find_by_id(userr.id)

	xp = dataset['xp']
	lvl = dataset['level']

	next_level_xp = (lvl+1) * 100
	xp_need = next_level_xp
	xp_have = dataset['xp']

	percentage = int(((xp_have * 100)/ xp_need))

	if percentage < 1:
		percentage = 0
	
	background = Editor(f"zIMAGE.png")
	profile = await load_image_async(str(userr.avatar))

	profile = Editor(profile).resize((150, 150)).circle_image()
	
	poppins = Font.poppins(size=40)
	poppins_small = Font.poppins(size=30)

	ima = Editor("zBLACK.png")
	background.blend(image=ima, alpha=.5, on_top=False)

	background.paste(profile.image, (30, 30))

	background.rectangle((30, 220), width=650, height=40, fill="#fff", radius=20)
	background.bar(
		(30, 220),
		max_width=650,
		height=40,
		percentage=percentage,
		fill="#ff9933",
		radius=20,
	)
	background.text((200, 40), str(userr.name), font=poppins, color="#ff9933")

	background.rectangle((200, 100), width=350, height=2, fill="#ff9933")
	background.text(
		(200, 130),
		f"Level : {lvl}   "
		+ f" XP : {xp} / {(lvl+1) * 100}",
		font=poppins_small,
		color="#ff9933",
	)

	card = discord.File(fp=background.image_bytes, filename="zCARD.png")
	await ctx.send(file=card, ephemeral=True)

@grenadierBot.hybrid_command(name="give-xp", description="Give XP to a member")
@app_commands.describe(member="Target @member")
@app_commands.describe(amount="Amount of XP to give")
async def give_xp(ctx, member: discord.Member, amount: int):
	dataset = await bot.levels.find_by_id(member.id)
	if dataset:
		dataset['xp'] += amount
		await bot.levels.upsert(dataset)
	else:
		default_level_item = {
			'_id': member.id,
			'xp': amount,
			'level': 0,
		}
		await bot.levels.insert(default_level_item)
	
	givenXP = discord.Embed(description=f"✅ {amount} XP has been given to {member.mention}", color=0x2B2D31)
	await ctx.send(embed=givenXP)

@grenadierBot.hybrid_command(name="remove-xp", description="Remove XP from a member")
@app_commands.describe(member="Target @member")
@app_commands.describe(amount="Amount of XP to remove")
async def remove_xp(ctx, member: discord.Member, amount: int):
	dataset = await bot.levels.find_by_id(member.id)
	if dataset:
		if dataset['xp'] <= amount:
			dataset['xp'] = 0
		else:
			dataset['xp'] -= amount
		await bot.levels.upsert(dataset)

	givenXP = discord.Embed(description=f"✅ {amount} XP has been removed from {member.mention}", color=0x2B2D31)
	await ctx.send(embed=givenXP)
	
from discord.ext import commands

async def createTicket(ctx, type, message=None):
	type = int(type)
	category = discord.utils.get(ctx.guild.categories, id=1091254812819066891)

	if type == 8:
		ticketType = "dstransfer"
	elif type == 2 or type == 3 or type == 7 or type == 9 or type == 10 or type == 11 or type == 12 or type == 14:
		ticketType = "report"
	elif type == 1 or type == 4 or type == 5 or type == 6 or type == 13:
		if type == 1:
			ticketType = "bug"
		elif type == 4:
			ticketType = "exploit"
		elif type == 5:
			ticketType = "devapp"
		elif type == 6:
			ticketType = "alliance"
		elif type == 13:
			ticketType = "veteran"

	if type != 12 and type != 13 and type != 14:
		ticketCreator = ctx.user

		ticketTypes = []

		for channel in category.channels:
			if isinstance(channel, discord.TextChannel):
				if channel.topic and str(ticketCreator.id) in channel.topic:
					ticketTypes.append(channel.name.split('-')[0])
		if ticketType in ticketTypes:
			openTicket = discord.Embed(title="Report Ticket", description=f"There is already an open ticket at {channel.mention}", color=discord.Color.dark_blue())
			openTicket.set_author(name=ticketCreator.name, icon_url=ticketCreator.avatar)
			return await ctx.followup.send(embed=openTicket, ephemeral=True)
	elif type == 12 or type == 14:
		if type == 12:
			ticketCreator = ctx.author
			reportedMessage = await ctx.fetch_message(ctx.message.reference.message_id)
		else:
			ticketCreator = ctx.user
			reportedMessage = message
		contentReported = reportedMessage.content
		if reportedMessage.author.nick == None:
			reportedMessageAuthorNickname = reportedMessage.author.name
		else:
			reportedMessageAuthorNickname = reportedMessage.author.nick
		contentSentBy = f"{reportedMessage.author.mention} | {reportedMessageAuthorNickname} | {reportedMessage.author.id}"
		jumpToMessage = reportedMessage.jump_url
	elif type == 13:
		ticketCreator = ctx.author

	ticket_number = 1

	for channel in category.channels:
		if isinstance(channel, discord.TextChannel):
			if channel.name.split('-')[0] == ticketType:
				ticket_number += 1
	
	name = f"{ticketType}-{ticket_number}"

	supportTeam = ctx.guild.get_role(1069672694175506463)

	if type != 12 and type != 13 and type != 14:
		overwrites = {
					ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
					ctx.user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					supportTeam: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
				}
		channel = await ctx.guild.create_text_channel(name = name, topic=f"otherReport:{ctx.user.id}", overwrites = overwrites, category=category)

		ticketCreated = discord.Embed(title="Report Ticket", description=f"Your report ticket has been created. The ticket number is {channel.mention}", color=discord.Color.dark_blue())
		ticketCreated.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
		await ctx.followup.send(embed=ticketCreated, ephemeral=True)
	elif type == 12 or type == 14:
		overwrites = {
					ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
					ticketCreator: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					reportedMessage.author: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					supportTeam: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
				}
		channel = await ctx.guild.create_text_channel(name = name, topic=f"contentReport:{ticketCreator.id}", overwrites = overwrites, category=category)
		if type == 14:
			ticketCreated = discord.Embed(title="Report Ticket", description=f"Your report ticket has been created. The ticket number is {channel.mention}", color=discord.Color.dark_blue())
			ticketCreated.set_author(name=ctx.user.name, icon_url=ctx.user.avatar)
			await ctx.response.send_message(embed=ticketCreated, ephemeral=True)
		elif type == 12:
			ticketCreated = discord.Embed(title="Report Ticket", description=f"Your report ticket has been created. The ticket number is {channel.mention}", color=discord.Color.dark_blue())
			ticketCreated.set_author(name=ticketCreator.name, icon_url=ticketCreator.avatar)
			await ctx.send(embed=ticketCreated)
	elif type == 13:
		overwrites = {
					ctx.guild.default_role: discord.PermissionOverwrite(view_channel = False),
					ctx.author: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
					supportTeam: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True, use_application_commands = True),
				}
		channel = await ctx.guild.create_text_channel(name = name, topic=f"otherReport:{ctx.author.id}", overwrites = overwrites, category=category)
	
	welcomeEmbed = discord.Embed(title=f"**{channel.name.split('-')[0].upper()} TICKET**", color=discord.Color.dark_blue())

	if type == 1:
		welcomeEmbed.description="Hello! This is your Report ticket to report a glitch or bug. Please send us the following information.\n```Username:\nProfile Link:\nGlitch/Bug:\nDescribe it:\nImage/Videos:\nSteps to Replicate:```"
	elif type == 2:
		welcomeEmbed.description="Hello! This is your Report ticket to report a High rank. Please send us the following information about that officer.\n```Username:\nRank:\nExplain their behaviour:\nImage/Videos:```"
	elif type == 3:
		welcomeEmbed.description="Hello! This is your Report ticket to report an exploiter. Please send us the following information.\n```Exploiter:\nExplain:\nImage/Videos:```"
	elif type == 4:
		welcomeEmbed.description="Hello! This is your report ticket to report a script that works to exploit our game. Please send us the following information about the script.\n```Exploit name:\nWhat it does:\nHow to do it:\nHow did you get this:\nImage/Videos:```"
	elif type == 5:
		welcomeEmbed.description="Hello! This is your ticket to apply as a developer in Alfie's Dev Team. Please send us the following information.\n```Username:\nProfile Link:\nType of Developer:\nDevForum Portfolio:\nGroups Work History:\nImage/Videos:```"
	elif type == 6:
		welcomeEmbed.description="Hello! This is your ticket to request an alliance with Roblox |ABA| British Army group. Please send us the following information.\n```Roblox Username:\nYour rank there:\nGroup Name:\nOwned By:\nGroup link:\nMain Game link:\nReason for alliance:```"
	elif type == 7:
		welcomeEmbed.description="Hello! This is your Report ticket to report corruption. Please send us the following information about the corrupt individual\n```Username:\nRank:\nRegiment:\nExplain:\nImage/Videos:```"
	elif type == 8:
		welcomeEmbed.description="Hello! This is your ticket to request a transfer from your old discord to a new discord.Please send us the following information about you.\n```Username:\nRank:\nDivision:\nDivision Rank:\nOld Discord:\nExplain:\nImage/Videos:```"
	elif type == 9:
		welcomeEmbed.description="Hello! This is your Report ticket to report an abuser. Please send us the following information about the abuser.\n```Username:\nRegiment:\nRank:\nExplain:\nImage/Videos:```"
	elif type == 10:
		welcomeEmbed.description="Hello! This is your Report ticket to report a rule breaker in DMs or BA chat. Please send us the following information about the individual.\n```Username:\nRank:\nExplain their actions:\nImage/Videos:```"
	elif type == 11:
		welcomeEmbed.description="**Unfair Mute Report Ticket**\n\nAll mods, please do not intervene into this ticket and escalate it to an administrator immediately, failure to do so would result in a removal.\n\nModerator Reported: {ctx.author.nick}\nMute Duration: {duration}\nMute Reason: {reason}"
	elif type == 12 or type == 14:
		welcomeEmbed.description=f"Content Reported : {contentReported}\n\nContent Sent By : {contentSentBy}\n\nJump To Message : {jumpToMessage}"
	elif type == 13:
		welcomeEmbed.description="Hello! This is your ticket to gain your rank in the Veteran Association group. Please send us the following information about you.\n```Username:\nRank:\nRegiment:\nYear Joined:\nImage/Videos:```"
	
	if type != 12 and type != 13 and type != 14:
		welcomeEmbed.set_author(name=f"{ctx.user.name}", icon_url=ctx.user.avatar)
		message = await channel.send(f"{ctx.user.mention}, {supportTeam.mention}", embed=welcomeEmbed)
	elif type == 12 or type == 14:
		welcomeEmbed.set_author(name=f"{ticketCreator.name}", icon_url=ticketCreator.avatar)
		message = await channel.send(f"{ticketCreator.mention}, {reportedMessage.author.mention}, {supportTeam.mention}", embed=welcomeEmbed)
	elif type == 13:
		welcomeEmbed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar)
		message = await channel.send(f"{ctx.author.mention}, {supportTeam.mention}", embed=welcomeEmbed)

	def check(m):
		if m.author.bot:
			return False
		return supportTeam in m.author.roles and m.channel == channel
	
	response = await bot.wait_for("message", check=check)
	
	supportArrived = discord.Embed(
		title="**Support has arrived!**",
		description=f"{response.author.mention} will now be assisting with your report.",
		color=discord.Color.dark_blue(),
	)
	supportArrived.set_author(name=response.author.name, icon_url=response.author.avatar)
	await channel.send(ticketCreator.mention, embed=supportArrived)

	claimedMod = response.author
	await channel.edit(topic=f"{channel.topic}-{claimedMod.id}")

class RobloxVerify(discord.ui.View):
	def __init__(self, encoded_discord_user_id):
		super().__init__(timeout=None)
		button = discord.ui.Button(label='Begin Verification', style=discord.ButtonStyle.url, url=f'https://authorize.roblox.com/?response_type=code&client_id=8711244147193460036&redirect_uri=https%3A%2F%2Faba-ranking-services-fad267650515.herokuapp.com%2Fverify&scope=profile+openid&prompt=login+consent+select_account&state={encoded_discord_user_id}')
		self.add_item(button)

class VerifyReverify(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label='Verify via ROBLOX Login', style=discord.ButtonStyle.green)
	async def roblox(self, interaction: discord.Interaction, button: discord.ui.Button):
		discord_user_id = str(interaction.user.id)
		encoded_discord_user_id = base64.b64encode(discord_user_id.encode()).decode()
		verifyAccount = discord.Embed(title="BRITISH ARMY VERIFICATION SYSTEM V5", description="Click on the button below to begin verification process\n\n**Please DO NOT share this link with anyone**\n\nThis link expires in **2 minutes** or once the verification process begins.", color=discord.Color.dark_blue())
		verifyAccount.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		await interaction.response.send_message(embed=verifyAccount, view=RobloxVerify(encoded_discord_user_id), ephemeral=True)

	@discord.ui.button(label='Verify via ROBLOX Game', style=discord.ButtonStyle.green)
	async def game(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer(ephemeral=True, thinking=True)
		await gameVerification(interaction)

	@discord.ui.button(label='Update Roles', style=discord.ButtonStyle.green)
	async def update(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.defer(ephemeral=True, thinking=True)
		updateEmbed = await bot.get_cog("Verification").update(interaction, None, None)
		await interaction.edit_original_response(embed=updateEmbed)

class CreateTicket(discord.ui.View):
	def __init__(self, ticketTypes):
		super().__init__(timeout=None)
		self.value = None
		self.ticketTypes = ticketTypes

	# When the confirm button is pressed, set the inner value to `True` and
	# stop the View from listening to more input.
	# We also send the user an ephemeral message that we're confirming their choice.
	@discord.ui.button(label='Create Ticket', style=discord.ButtonStyle.red)
	async def createTicket(self, interaction: discord.Interaction, button: discord.ui.Button):
		if self.ticketTypes == 1:
			view = CustomTicketMenu(interaction.user.id, [
				discord.SelectOption(label="Verify / Reverify", description="Verify / reverify your ROBLOX account via this ticket",value="13"),
				discord.SelectOption(label="Discord Transfer", description="Open a transfer ticket",value="8"),
			])
		elif self.ticketTypes == 2:
			view = CustomTicketMenu(interaction.user.id, [
				discord.SelectOption(label="Report High Rank", description="Report a high ranking officer.",value="2"),
				discord.SelectOption(label="Report Exploiter", description="Report an exploiter in game to our moderation team",value="3"),
				discord.SelectOption(label="Report Corruption", description="Report a corrupted user",value="7"),
				discord.SelectOption(label="Report Abuser", description="Report an abuser",value="9"),
				discord.SelectOption(label="Report Rule Breaker", description="Report a rule breaker",value="10"),
			])
		elif self.ticketTypes == 3:
			view = CustomTicketMenu(interaction.user.id, [
				discord.SelectOption(label="Report Bug / Glitch", description="Report an in game / discord glitch or bug to our developers",value="1"),
				discord.SelectOption(label="Report Exploit Script", description="Report an exploit script or vulnerability to our developers",value="4"),
				discord.SelectOption(label="Developer Application", description="Apply to become a developer for British Army",value="5"),
				discord.SelectOption(label="Alliance Application", description="Apply to become an ally with the British Army",value="6"),
			])

		if self.ticketTypes == 2 or self.ticketTypes == 3:
			dataset = await bot.roblox.find_by_id(interaction.user.id)
			if dataset is None:
				notVerified = discord.Embed(title="Not Verified", description="You need to verify your ROBLOX account in order to create report or other tickets.", color=discord.Color.dark_gold())
				notVerified.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
				return await interaction.response.send_message(embed=notVerified, ephemeral=True)
		selectTicketType = discord.Embed(title="Create Ticket", description="Please select what ticket you wish to create.", color=discord.Color.dark_blue())
		selectTicketType.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
		await interaction.response.send_message(embed=selectTicketType, view=view, ephemeral=True)

class CustomTicket(discord.ui.Select):
	def __init__(self, user_id, options: list):
		self.user_id = user_id
		optionList = []

		for option in options:
			if isinstance(option, str):
				optionList.append(
					discord.SelectOption(
						label=option.replace('_', ' ').title(),
						value=option
					)
				)
			elif isinstance(option, discord.SelectOption):
				optionList.append(option)

		# The placeholder is what will be shown when no option is chosen
		# The min and max values indicate we can only pick one of the three options
		# The options parameter defines the dropdown options. We defined this above
		super().__init__(placeholder='Select Ticket Type', min_values=1, max_values=1, options=optionList)

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.defer()
		if len(self.values) == 1:
			self.view.value = self.values[0]
			self.placeholder = self.view.value.title()
		else:
			self.view.value = self.values

		if self.view.value != "13":
			await createTicket(interaction, type=self.view.value)
		elif self.view.value == "13":
			dataset = await bot.roblox.find_by_id(interaction.user.id)
			if dataset:
				await bot.get_cog("Verification").reverify(interaction)
			else:
				await bot.get_cog("Verification").verify(interaction)

class CustomTicketMenu(discord.ui.View):
	def __init__(self, user_id, options: list):
		super().__init__(timeout=None)
		self.value = None
		self.user_id = user_id

		self.add_item(CustomTicket(self.user_id, options))

@bot.tree.context_menu(name="Report Message")
async def report(interaction: discord.Interaction, message: discord.Message):
	await createTicket(interaction, 14, message)

from discord.abc import User
from utils.predicates import owner_predicate

class CustomBot(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def is_owner(self, user: User) -> bool:
		return owner_predicate(user)

xyron = CustomBot(command_prefix='!', case_insensitive=True, intents=discord.Intents.all())
xyron.allowed_commands = ["commands"]

@xyron.event
async def on_ready():
	extensions = [m.name for m in iter_modules(["xyron_cogs"], prefix="xyron_cogs.")]
	for i in extensions:
		print(f"Loading {i}")
		await xyron.load_extension(i)
		print(f'Loaded {i}')

	await xyron.load_extension('jishaku')
	await xyron.tree.sync()

loop = asyncio.get_event_loop()
loop.create_task(bot.start(config('BOT_TOKEN')))
loop.create_task(grenadierBot.start("MTEzNTI2NDMxMjk4Njk3NjMxNw.GzN7bl.I55VAbPfTcBiReZuc69Lhu6Nw3uGBFX55vkGAo"))
loop.create_task(xyron.start("MTE2MjEwMTgzNDExOTM5MzM5MA.GQCyfW.Xbvx-RoyofYc4ul9odcUMFz-4nL8_XNEc5-YdQ"))
loop.run_forever()
