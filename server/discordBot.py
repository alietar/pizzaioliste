import discord
from discord.ext import commands
from discord.ext import tasks, commands

def generate_embed(_sos):
    embed = discord.Embed(
        title = _sos[5],
        description = f"Pour : {_sos[1]} {_sos[2]}\nAu : {_sos[7]}{str(_sos[8])}\nA : {_sos[6]}",
        color = discord.Colour.blurple()
    )

    #embed.set_author("Leonardo@insa-lyon.fr")

    return embed




@commands.command()
async def test(ctx, arg):
    await ctx.send(arg)


class Bot(commands.Bot):
    def __init__(self, send_queue, modify_queue, channels_id):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

        self.send_queue = send_queue
        self.modify_queue = modify_queue
        self.channels_id = channels_id

        self.add_command(test)


    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

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
        print(message.content)

        if message.author.id == self.user.id:
            return

        if not message.content.startswith('$'):
            return

        try:
            args = message.content.split(" ")

            if len(args) != 2:
                raise Exception("Il n'y a pas d'argument à la commande")


            command = args[0][1:]
            sos_id = args[1]

            if not sos_id.isdecimal():
                raise Exception("La turne n'est pas un numéro")

            dm_channel = message.author.dm_channel

            if dm_channel == None:
                dm_channel = await message.author.create_dm()

            # Check if it's a dm or on a server
            if message.channel.id == dm_channel.id:
                match command:
                    case "fini" | "finir":
                        print(f"Sos n°{sos_id} fini")

                    case "annule" | "annul" | "annulé" | "annuler" | "anule" | "anul" | "anulé" | "anuler":
                        print(f"Sos n°{sos_id} annulé")

                    case _:
                        raise Exception("La commande n'est pas reconnue\nLes commandes possibles sont 'annuler' et 'finir'")

            else:
                match command:
                    case "prendre":
                        print(f"Sos n°{sos_id} fini")

                    case "supprimer":
                        print(f"Sos n°{sos_id} annulé")

                    case _:
                        raise Exception("La commande n'est pas reconnue\nLes commandes possibles sont 'prendre' et 'supprimer'")



            await message.add_reaction("🤌")

        except Exception as e:
            # Sending the error message to the client to let him know
            await message.channel.send(str(e))



    async def send_sos(self, _sos):
        print(_sos[7])
        print(self.channels_id[_sos[7]])
        channel = self.get_channel(int(self.channels_id[_sos[7]]))


        embed = discord.Embed(
            title = _sos[5],
            description = f"Pour : {_sos[1]} {_sos[2]}\nAu : {_sos[7]}{str(_sos[8])}\nA : {_sos[6]}",
            color = discord.Colour.blurple()
        )

        await channel.send('Nouvelle commande de SOS', view=SOSView(_sos, self.modify_queue), embed=embed)



class SOSView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, _sos, _modify_queue):
        super().__init__(timeout=None)
        self.sos = _sos
        self.sos_id = self.sos[10]
        self.modify_queue = _modify_queue


    @discord.ui.button(label="Je m'en charge", style=discord.ButtonStyle.primary)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'SOS n°{str(self.sos_id)} pris par ${interaction.user.display_name}')

        dm_channel = interaction.user.dm_channel

        if dm_channel == None:
            dm_channel = await interaction.user.create_dm()

        embed = discord.Embed(
            title = self.sos[5],
            description = f"Pour : {self.sos[1]} {self.sos[2]}\nAu : {self.sos[7]}{str(self.sos[8])}\nA : {self.sos[6]}",
            color = discord.Colour.blurple()
        )

        await dm_channel.send(f"Tu t'occupes du SOS n°{str(self.sos_id)}", view=DoneView(self.sos_id, self.modify_queue), embed=embed)
        await interaction.message.delete()

        self.stop()


    @discord.ui.button(label="Supprimer le SOS", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"SOS n°{str(self.sos_id)} annulé par ${interaction.user.display_name}")

        self.modify_queue.put_nowait({"id": self.sos_id, "command": "removed"})

        await interaction.message.delete()

        self.stop()



class DoneView(discord.ui.View):
    def __init__(self, _sos_id, _modify_queue):
        super().__init__(timeout=None)
        self.sos_id = _sos_id
        self.modify_queue = _modify_queue


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
