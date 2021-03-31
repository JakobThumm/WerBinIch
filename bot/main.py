# bot.py
import os
import random
from discord.ext import commands

token = os.getenv("DISCORD_BOT_TOKEN")
bot = commands.Bot(command_prefix='!')
player_list = []
# key: who is writing the word, value: for whom
player_connection = {}
# key: The player with word on head, value: the word
word_dict = {}
game_state = 0

def reset_game():
    global player_list
    global player_connection
    global word_dict
    global game_state
    player_list = []
    player_connection = {}
    word_dict = {}
    game_state = 0

reset_game()

@bot.command(name='go', help='Reset wer bin ich.')
async def go(ctx):
    player = ctx.author
    if player == bot.user:
        return
    global player_list
    global player_connection
    global word_dict
    global game_state
    if game_state != 3:
        await ctx.send("Not all players typed in a word yet.")
        return

    for this_player in player_list:
        await this_player.create_dm()
        await this_player.dm_channel.send(f'The words of all players are:')
        for other_player in word_dict:
            if other_player != this_player:
                await this_player.create_dm()
                await this_player.dm_channel.send("{}: {}".format(other_player.name, word_dict[other_player]))
    await ctx.send("Have fun. Type !reset to reset the game.") 

@bot.command(name='reset', help='Reset wer bin ich.')
async def reset(ctx):
    player = ctx.author
    if player == bot.user:
        return
    reset_game()
    await ctx.send("Wer bin ich reseted.")

@bot.command(name='start', help='Start a round of Wer bin ich.')
async def start(ctx):
    player = ctx.author
    if player == bot.user:
        return
    global game_state
    if game_state != 0:
        await ctx.send("Please reset the game")
        return
    await ctx.send("Started a game of Wer bin ich. Write !dtf in the chat to play along. Write !ready to start the word phase.")
    game_state=1

@bot.command(name='dtf', help='Indicate that you are down to fuck for a round of Wer bin ich.')
async def dtf(ctx):
    player = ctx.author
    if player == bot.user:
        return
    global player_list
    global game_state
    
    if game_state != 1:
        await player.create_dm()
        await player.dm_channel.send(f'Game not started yet.')
        return
    player_list.append(player)
    await player.create_dm()
    await player.dm_channel.send(
        f'Welcome to Wer bin ich, you are now an active player. Please wait until everyone is ready.'
    )

@bot.command(name='ready', help='All players wrote dtf.')
async def ready(ctx):
    global player_list
    global player_connection
    global word_dict
    global game_state
    player = ctx.author
    if player == bot.user:
        return
    if game_state != 1:
        await ctx.send("The game state is not resetted.")
        return
    all_players_string = ""
    for p in player_list:
        all_players_string += p.name + " "
    await ctx.send("Players in list: " + all_players_string)
    random.shuffle(player_list)
    for i, player in enumerate(player_list):
        if i<len(player_list)-1:
            player_connection[player] = player_list[i+1]
        else:
            player_connection[player] = player_list[0]
        word_dict[player] = ""
        
        await player.create_dm()
        await player.dm_channel.send(
            f'Welcome to Wer bin ich, {player.name}, choose a word for {player_connection[player].name} by entering !word __your_word__. Do not use spaces.'
        )
    await ctx.send("Please send your words in private chat.")
    game_state = 2

def check_all_words_there():
    global word_dict
    all_there = True
    for player in word_dict:
        if word_dict[player] == "":
            all_there = False
    return all_there

@bot.command(name='word', help='Insert your word.')
async def word(ctx, word: str):
    global player_list
    global player_connection
    global word_dict
    global game_state
    player = ctx.author
    if player == bot.user:
        return
    if game_state!=2:
        await player.create_dm()
        await player.dm_channel.send(
            f'Not all players are ready yet. Stop spamming.'
        )
        return
    word_dict[player_connection[player]] = word
    await player.create_dm()
    await player.dm_channel.send(
        f'You chose, {word}, for {player_connection[player].name}!'
    )
    if check_all_words_there():
        await ctx.send("All players are ready! Type !go to start the funs.")
        game_state = 3

bot.run(token)