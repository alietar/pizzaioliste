import discord
from discord.ext import commands
from discord.ext import tasks, commands


def convert_timeslot(timeslot):
    dayName = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"][int(timeslot[0]) - 1];
    hourName = ["7h-8h", "12h-14h", "18h-21h"][int(timeslot[2]) - 1];

    return dayName + " " + hourName

class Bot(commands.Bot):
    def __init__(self, send_queue, modify_queue, channels_id, db):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

        self.send_queue = send_queue
        self.modify_queue = modify_queue
        self.channels_id = channels_id
        self.db = db


    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

        self.loop.create_task(self.queue_loop())


    async def queue_loop(self):
        await self.wait_until_ready()

        while not self.is_closed():
            sos = await self.send_queue.get()
            print("Sending sos to the discord")

            await self.annouce_sos(sos)

            self.send_queue.task_done()


    async def on_message(self, _message):
        print(f"New message from discord : {_message.content}")

        await self.handle_message(_message, False)


    async def handle_message(self, message, confirmed):
        # we do not want the bot to reply to itself

        confirmed = True

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
            status = await self.db.get_status(sos_id)

            if not sos_id.isdecimal():
                raise Exception("L'agument n'est pas un nombre")

            dm_channel = message.author.dm_channel

            if dm_channel == None:
                dm_channel = await message.author.create_dm()

            # Check if it's a dm or on a server
            if message.channel.id == dm_channel.id:
                match command:
                    case "fini" | "finir":
                        print(f"Sos n°{sos_id} fini")

                        match status:
                            case "done":
                                raise Exception("Le SOS est déjà fait")
                            case "abandonned":
                                raise Exception("Le SOS a été abandonné")
                            case "pending":
                                raise Exception("Le SOS n'a pas été pris")

                        if confirmed:
                            await self.db.set_status(sos_id, 'done')

                    case "annule" | "annul" | "annulé" | "annuler" | "anule" | "anul" | "anulé" | "anuler":
                        print(f"Sos n°{sos_id} annulé")

                        match status:
                            case "done":
                                raise Exception("Le SOS est déjà fait")
                            case "abandonned":
                                raise Exception("Le SOS est déjà abandonné")
                            case "pending":
                                raise Exception("Le SOS n'a pas été pris")

                        if confirmed:
                            await self.db.set_status(sos_id, 'abandonned')

                    case _:
                        raise Exception("La commande n'est pas reconnue\nLes commandes possibles sont 'annuler' et 'finir'")

            else:
                match command:
                    case "prendre":
                        print(f"Sos n°{sos_id} pris")

                        if status != "pending":
                            raise Exception("Le SOS est déjà pris")

                        if confirmed:
                            await self.db.set_status(sos_id, 'taken')

                            sos = await self.db.get_sos(sos_id)

                            await self.send_sos(sos, dm_channel)

                    case "supprimer":
                        print(f"Sos n°{sos_id} annulé")

                        if status != "pending":
                            raise Exception("Le SOS est déjà pris")

                        if confirmed:
                            await self.db.set_status(sos_id, 'cancelled')

                    case _:
                        raise Exception("La commande n'est pas reconnue\nLes commandes possibles sont 'prendre' et 'supprimer'")

            if confirmed:
                await message.add_reaction("🤌")
            else:
                await self.ask_confirmation(message)

        except Exception as e:
            # Sending the error message to the client to let him know
            await message.reply(str(e), silent=True, delete_after=10)


    async def on_reaction_add(self, _reaction, _user):
        print(_reaction.emoji)
        if _reaction.emoji == "🍕":
            await self.handle_message(_reaction.message, True)


    async def annouce_sos(self, _sos):
        channelName = _sos[7] + str(_sos[8])[0]
        print(channelName)

        channelId = int(self.channels_id["erreur"])
        try:
            channelId = int(self.channels_id[channelName])
        except:
            pass

        channel = self.get_channel(channelId)

        await self.send_sos(_sos, channel)


    async def ask_confirmation(self, _message):
        await _message.reply(f"Confirme l'action en réagissant avec 🍕 à ton propre message", silent=True, delete_after=10)


    async def send_sos(self, _sos, _channel):
        embed = discord.Embed(
            title = _sos[5],
            description = f"Pour : {_sos[1]} {_sos[2]}\nAu : {_sos[7]}{str(_sos[8])}\nLe : {convert_timeslot(_sos[6])}",
            color = discord.Colour.blurple()
        )

        await _channel.send(f"Nouvelle commande de SOS n°{str(_sos[10])}", embed=embed)
