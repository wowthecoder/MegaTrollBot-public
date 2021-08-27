import discord
from discord.ext import commands
from discord_components import Button, ButtonStyle, InteractionType
from asyncio import TimeoutError

class Games(commands.Cog):
    description = ""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="rps", brief="rps <@user>", description="Classic rock paper scissors game with your friend.")
    async def rps(self, ctx, *, user: discord.Member):
        if user == ctx.author:
            await ctx.send("You can't play with yourself, dummy.")
            return
        elif user.bot:
            await ctx.send("You can't play with a bot, they will never respond anyways.")
            return
        rps_intro = f"{ctx.author.mention} {user.mention}\n__**ROCKS PAPER SCISSORS**__, who will win? :trophy:\n**{ctx.author.name} vs {user.name}**"
        rps_author = f"{ctx.author.name} is choosing..."
        rps_user = f"{user.name} is choosing..."
        rps_str = rps_intro + "\n" + rps_author + "\n" + rps_user
        emojis = {"Rock": "🪨", "Paper": "🧻", "Scissor": "✂️"}
        msg = await ctx.send(rps_str, 
                            components=[[
                                Button(style=ButtonStyle.blue, label="Rock", emoji="🪨"),
                                Button(style=ButtonStyle.blue, label="Paper", emoji="🧻"),
                                Button(style=ButtonStyle.blue, label="Scissor", emoji="✂️")
                            ]])

        try:
            author_choice, user_choice = None, None
            while author_choice is None or user_choice is None:
                interaction = await self.bot.wait_for("button_click", timeout=15)
                if interaction.user.id == ctx.author.id:
                    #await interaction.respond(type=InteractionType.UpdateMessage)
                    author_choice = interaction.component.label
                    rps_author = f"{ctx.author.name} has chosen!"
                    rps_str = rps_intro + "\n" + rps_author + "\n" + rps_user
                    await msg.edit(rps_str,
                                    components=[[
                                        Button(style=ButtonStyle.blue, label="Rock", emoji="🪨"),
                                        Button(style=ButtonStyle.blue, label="Paper", emoji="🧻"),
                                        Button(style=ButtonStyle.blue, label="Scissor", emoji="✂️")
                                    ]])
                elif interaction.user.id == user.id:
                    #await interaction.respond(type=InteractionType.UpdateMessage)
                    user_choice = interaction.component.label
                    rps_user = f"{user.name} has chosen!"
                    rps_str = rps_intro + "\n" + rps_author + "\n" + rps_user
                    await msg.edit(rps_str, 
                                    components=[[
                                        Button(style=ButtonStyle.blue, label="Rock", emoji="🪨"),
                                        Button(style=ButtonStyle.blue, label="Paper", emoji="🧻"),
                                        Button(style=ButtonStyle.blue, label="Scissor", emoji="✂️")
                                    ]])
                else:
                    await interaction.respond(type=InteractionType.ChannelMessageWithSource, content="This is not your game, back off!")
            if author_choice == user_choice:
                rps_str = rps_intro + f"\nBoth chosed {emojis[author_choice]}! The game ended in a draw."
                await msg.edit(rps_str, 
                                components=[[
                                    Button(style=ButtonStyle.blue, label="Rock", emoji="🪨", disabled=True),
                                    Button(style=ButtonStyle.blue, label="Paper", emoji="🧻", disabled=True),
                                    Button(style=ButtonStyle.blue, label="Scissor", emoji="✂️", disabled=True)
                                ]])
            elif (author_choice == "Rock" and user_choice == "Scissor") or (author_choice == "Paper" and user_choice == "Rock") or (author_choice == "Scissor" and user_choice == "Paper"):
                #author wins
                rps_str = rps_intro + f"\n{ctx.author.name} chose {emojis[author_choice]} and {user.name} chose {emojis[user_choice]}!\n:tada: {ctx.author.name} won the game! :tada:"
                await msg.edit(rps_str, 
                                components=[[
                                    Button(style=ButtonStyle.blue, label="Rock", emoji="🪨", disabled=True),
                                    Button(style=ButtonStyle.blue, label="Paper", emoji="🧻", disabled=True),
                                    Button(style=ButtonStyle.blue, label="Scissor", emoji="✂️", disabled=True)
                                ]])
            else: #user wins
                rps_str = rps_intro + f"\n{ctx.author.name} chose {emojis[author_choice]} and {user.name} chose {emojis[user_choice]}!\n:tada: {user.name} won the game! :tada:"
                await msg.edit(rps_str, 
                                components=[[
                                    Button(style=ButtonStyle.blue, label="Rock", emoji="🪨", disabled=True),
                                    Button(style=ButtonStyle.blue, label="Paper", emoji="🧻", disabled=True),
                                    Button(style=ButtonStyle.blue, label="Scissor", emoji="✂️", disabled=True)
                                ]])
        except TimeoutError as e:
            await msg.edit(f"{ctx.author.mention} {user.mention}\n__**ROCKS PAPER SCISSORS**__, who will win? :trophy:\nLooks like nobody wants to play!",
                            components=[[
                                Button(style=ButtonStyle.blue, label="Rock", emoji="🪨", custom_id="rps1rock", disabled=True),
                                Button(style=ButtonStyle.blue, label="Paper", emoji="🧻", custom_id="rps2paper", disabled=True),
                                Button(style=ButtonStyle.blue, label="Scissor", emoji="✂️", custom_id="rps3scissor", disabled=True)
                            ]])

        
    '''                   
    @commands.Cog.listener()
    async def on_button_click(self, interaction):
    '''    
                                             
    @commands.command(name="guess", brief="guess [integer]", aliases=["gtn"], description="Try to guess my number in the range 1 to [your number](default is 50).\nDon't worry, I will make it easier with some hints and several attempts!\nBut bet you still can't guess my number HEHE")
    async def guess(self, ctx, *number):
        await ctx.send("Still in development.")
        
    @commands.command(name="fight", brief="fight <@user>", description="Challenge your friend to a fight!")
    async def fight(self, ctx, *, friend: discord.Member):
        if friend == ctx.author:
            await ctx.send("You can't play with yourself, dummy.")
            return
        elif friend.bot:
            await ctx.send("You can't play with a bot, they will never respond anyways.")
            return
        fightbox = discord.Embed(
            color=0xf11e8b,
        )
        battle_img = discord.File("Images/sword_battle.png")
        fightbox.set_thumbnail(url="attachment://sword_battle.png")
        await ctx.send(file=battle_img, embed=fightbox)
        
    @fight.error
    async def fight_error(self, ctx, error):
        print(error)
        
    @commands.Cog.listener()
    async def on_ready(self):
        my_cog = self.bot.get_cog("Games")
        Games.description = "Some mini-games to play when you are feeling bored!\n`{} total commands`".format(len(my_cog.get_commands()))
        
def setup(bot):
    bot.add_cog(Games(bot))
    