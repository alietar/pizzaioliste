import discord
from discord.ext import commands
from discord.ext import tasks, commands

channel_id = 1184475986419519591


class Bot(commands.Bot):
    def __init__(self, send_queue, modify_queue):
        intents = discord.Intents.default()
        intents.message_content = True
        self.send_queue = send_queue
        self.modify_queue = modify_queue

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)


    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        # await self.send_sos(1)
        self.loop.create_task(self.queue_loop())

    async def queue_loop(self):
        await self.wait_until_ready()

        while not self.is_closed():
            sos = await self.send_queue.get()
            print("Sending sos to the discord")

            await self.send_sos(sos)

            self.send_queue.task_done()

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.channel.name != "test-sos":
            return

        print(message.channel.id)


    async def send_sos(self, _sos):
        channel = self.get_channel(channel_id)

        embed = discord.Embed(
            title = _sos[5],
            description = f"Pour : {_sos[1]} {_sos[2]}\nAu : {_sos[7]}{str(_sos[8])}\nA : {_sos[6]}",
            color = discord.Colour.blurple()
        )

        #embed.set_author("Leonardo@insa-lyon.fr")

        await channel.send('Nouvelle commande de SOS', view=SOSView(_sos[10], self.modify_queue), embed=embed)



class SOSView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, sos_id, modify_queue):
        super().__init__()
        self.sos_id = sos_id
        self.modify_queue = modify_queue


    @discord.ui.button(label="Je m'en charge", style=discord.ButtonStyle.primary)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'SOS n°{str(self.sos_id)} pris par ${interaction.user.display_name}')

        dm_channel = interaction.user.dm_channel

        if dm_channel == None:
            dm_channel = await interaction.user.create_dm()

        await dm_channel.send(f"Suivi du SOS n°{str(self.sos_id)}", view=DoneView(self.sos_id, self.modify_queue))

        await interaction.message.delete()

        self.stop()


    @discord.ui.button(label="Supprimer le SOS", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"SOS n°{str(self.sos_id)} annulé par ${interaction.user.display_name}")

        self.modify_queue.put_nowait({"id": self.sos_id, "command": "removed"})

        await interaction.message.delete()

        self.stop()



class DoneView(discord.ui.View):
    def __init__(self, sos_id, modify_queue):
        super().__init__()
        self.sos_id = sos_id
        self.modify_queue = modify_queue


    @discord.ui.button(label="J'ai fais le SOS", style=discord.ButtonStyle.success)
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        #Prendre en compte dans la database
        self.modify_queue.put_nowait({"id": self.sos_id, "command": "done"})

        await interaction.response.send_message("Réponse prise en compte")

        self.stop()


    @discord.ui.button(label="J'ai pas pu faire le SOS", style=discord.ButtonStyle.danger)
    async def not_done(self, interaction: discord.Interaction, button: discord.ui.Button):
        #Prendre en compte dans la database
        self.modify_queue.put_nowait({"id": self.sos_id, "command": "abandoned"})

        await interaction.response.send_message("Réponse prise en compte")

        self.stop()



#@bot.command()
#async def button(ctx):
#    view = MyView()
#
#    await ctx.send('Do you want to continue?', view=view)
#    await view.wait()
#    print(view.value)
