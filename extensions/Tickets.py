import discord
from discord.ext import commands
from discord import app_commands

GUILD_ID = YOUR_GUILD_ID  # Replace with your server ID
TICKET_CATEGORY_ID = YOUR_TICKET_CATEGORY_ID  # Replace with the ID of the category where tickets should be created


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="ticket-viewer", description="Command to view the ticket button.")
    async def ticket_viewer(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="Support Ticket",
                description="Please click the button below to create a ticket.",
                color=discord.Color.blurple(),
            )
            await interaction.response.send_message(embed=embed, view=MainTicketView())
        else:
            await interaction.response.send_message("Forbidden!", ephemeral=True)


class MainTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Support Ticket", style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Support Ticket",
            description="Please select the type of ticket you would like to create.",
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed, view=OptionsView(), ephemeral=True)


class OptionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Request Conference", style=discord.ButtonStyle.primary)
    async def callback_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RequestConferenceModal())

    @discord.ui.button(label="Need Help", style=discord.ButtonStyle.primary)
    async def callback_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NeedHelpModal())

    @discord.ui.button(label="Any Questions", style=discord.ButtonStyle.primary)
    async def callback_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AnyQuestionsModal())

    @discord.ui.button(label="Live Ban", style=discord.ButtonStyle.primary)
    async def callback_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LiveBanModal())


class CloseTicketView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            view = ConfirmCloseView(self.channel)
            await interaction.response.send_message(
                "Are you sure you want to close this ticket?", view=view, ephemeral=True
            )
        else:
            await interaction.response.send_message("You do not have permission to close this ticket!", ephemeral=True)


class ConfirmCloseView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    @discord.ui.button(label="Yes, Close Ticket", style=discord.ButtonStyle.danger)
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket will be closed.", ephemeral=True)
        await self.channel.delete()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket closure cancelled.", ephemeral=True)


async def create_ticket_channel(interaction: discord.Interaction, ticket_title, ticket_description):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

    # Create channel with permissions
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    }
    admin_role = discord.utils.get(guild.roles, name="Admin")  # Change to your admin role name
    if admin_role:
        overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

    channel = await guild.create_text_channel(
        name=f"ticket-{interaction.user.name}",
        category=category,
        overwrites=overwrites
    )

    embed = discord.Embed(title=ticket_title, description=ticket_description, color=discord.Color.green())
    embed.set_footer(text=f"Ticket opened by {interaction.user}")

    await channel.send(embed=embed, view=CloseTicketView(channel))
    await interaction.response.send_message(f"Your ticket has been created: {channel.mention}", ephemeral=True)


class NeedHelpModal(discord.ui.Modal, title="Need Help Ticket"):
    tiktok_username = discord.ui.TextInput(label="TikTok Username", required=True)
    urgency = discord.ui.TextInput(label="Is this urgent? (Urgent/Normal)", required=True)
    problem = discord.ui.TextInput(label="What seems to be the problem?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(
            interaction,
            "Need Help Ticket",
            f"📌 **TikTok Username:** {self.tiktok_username.value}\n⚡ **Urgency:** {self.urgency.value}\n❓ **Problem:** {self.problem.value}"
        )


class AnyQuestionsModal(discord.ui.Modal, title="Any Questions Ticket"):
    tiktok_username = discord.ui.TextInput(label="TikTok Username", required=True)
    urgency = discord.ui.TextInput(label="Is this urgent? (Urgent/Normal)", required=True)
    question = discord.ui.TextInput(label="What’s your question?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(
            interaction,
            "Question Ticket",
            f"📌 **TikTok Username:** {self.tiktok_username.value}\n⚡ **Urgency:** {self.urgency.value}\n❓ **Question:** {self.question.value}"
        )


class RequestConferenceModal(discord.ui.Modal, title="Request a Conference"):
    tiktok_username = discord.ui.TextInput(label="TikTok Username", required=True)
    urgency = discord.ui.TextInput(label="Is this urgent? (Urgent/Normal)", required=True)
    availability = discord.ui.TextInput(label="When are you available?", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(
            interaction,
            "Conference Request Ticket",
            f"📌 **TikTok Username:** {self.tiktok_username.value}\n⚡ **Urgency:** {self.urgency.value}\n📅 **Availability:** {self.availability.value}\n\n⚠️ *Please allow at least 24 hours after opening the ticket for us to schedule a conference.*"
        )


class LiveBanModal(discord.ui.Modal, title="Live Ban Ticket"):
    tiktok_username = discord.ui.TextInput(label="TikTok Username", required=True)
    reason_for_ban = discord.ui.TextInput(label="Reason for Live Ban", style=discord.TextStyle.paragraph, required=True)
    appealed = discord.ui.TextInput(label="Appealed? (Yes/No)", required=True)
    restore_date = discord.ui.TextInput(label="Live Access Restore Date", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket_channel(
            interaction,
            "Live Ban Ticket",
            f"📌 **TikTok Username:** {self.tiktok_username.value}\n🚫 **Reason for Ban:** {self.reason_for_ban.value}\n📢 **Appealed?:** {self.appealed.value}\n⏳ **Restoration Date:** {self.restore_date.value}"
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))