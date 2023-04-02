# Main file

# Beat discord music bot v1.2.3
# Made by Knedme

from time import sleep
from youtubesearchpython.__future__ import VideosSearch
import discord
from discord.ext import commands

import asyncio
import requests
import random
from pytube import Playlist
from async_spotify import SpotifyApiClient
from async_spotify.authentification.authorization_flows import ClientCredentialsFlow
from async_spotify.spotify_errors import SpotifyBaseError
from ytmusicapi import YTMusic
from concurrent.futures import ThreadPoolExecutor

from pymongo import MongoClient
from datetime import datetime
import os
import json
from yt_dlp import YoutubeDL
import functools
import typing
import asyncio
import time




from misc import Config, YouTubeWrapper
#Mongodb Setup
'


def to_thread(func: typing.Callable) -> typing.Coroutine:
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


@to_thread
def blocking_func(a):
    time.sleep(a)
    return "some stuff"









ydl=YoutubeDL({
    'format': 'bestaudio/best',
    'ignoreerrors': True,
})


def extract_info(yt_url):
    return ydl.extract_info(yt_url, download=False)


clinet=MongoClient("mongodb",27017) #If Use Windows or WindowsServer Use this MongoClient("localhost",27017)

db =clinet["server"]  #Make Database Az Name Music 
Queuelist=db["Queuelist6"]

idchannel = 1070637151030607922


def selectPath(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)


if len(list(Queuelist.find())) == 0:
    temp = []
    with open(selectPath("Queuelist6.json"),"rb") as f:
        file_data = json.load(f)
    for x in file_data:
        x.pop('_id', None)
        temp.append(x)
    Queuelist.insert_many(temp)




spotify_client = SpotifyApiClient(authorization_flow=ClientCredentialsFlow(
    application_id=SPOTIFY_CLIENT_ID, application_secret=SPOTIFY_CLIENT_SECRET))




ytm_client = YTMusic()

loops = {}  # for /loop command
queues = {}  # for current queues
all_queues_info = {}  # all queues info, for /queue command
now_playing_pos = {}  # to display the current song in /queue command correctly
adding_to_queue_ids = []  # to add YouTube playlists or Spotify playlists/albums to the queue correctly
temp = "" # For Title of embed
text="""[Song List]\n Join a voice channel and queue songs by name or url in here. """   #For text channel 
embed_temp = "" # For Img and text of embed 
Queue = [] # Dont touch This For Database

# this function checks if YouTube link is valid
def is_valid_yt_url(url):
    checker_url = 'https://www.youtube.com/oembed?url=' + url
    request = requests.get(checker_url)
    return request.status_code == 200


# this function extracts all info from YouTube video url



# this function gets full name of the Spotify track with artists
def get_sp_track_full_name(sp_track_artist_list, sp_track_name):
    artist_names = sp_track_artist_list[0]['name']
    for i in range(len(sp_track_artist_list) - 1):
        artist_names += ', ' + sp_track_artist_list[i + 1]['name']
    return artist_names + ' - ' + sp_track_name


# this function returns the YouTube url of the specified full name of the Spotify track
async def get_sp_track_yt_url(sp_track_full_name):
    # finding track on YouTube Music or YouTube (if not found)
    try:
        event_loop = asyncio.get_event_loop()
        yt_url = 'https://www.youtube.com/watch?v='\
                 + (await event_loop.run_in_executor(ThreadPoolExecutor(),
                                                     ytm_client.search,
                                                     sp_track_full_name,
                                                     'songs'))[0]['videoId']
    except IndexError:
        search_obj = VideosSearch(sp_track_full_name, limit=1)
        try:
            yt_url = (await search_obj.next())['result'][0]['link']
        except IndexError:
            # if track not found even on YouTube, just assigning None
            yt_url = None
    return yt_url






async def changename_basic():
    try:
        giveaway_msg_channel = bot.get_channel(idchannel)
        list_ahangha = await giveaway_msg_channel.fetch_message(int(temp))
        embed_ahanga = await giveaway_msg_channel.fetch_message(int(embed_temp))
        await list_ahangha.edit(content=text)
        emb = discord.Embed(title="Vibing Alone 😎",description = f'Anything you type in this channel will be interpreted as a video title', colour =  discord.Color.from_rgb(000,000,000))
        emb.set_footer(text =f"Developer AmirKasra#0991",icon_url="https://cdn.discordapp.com/avatars/643137299701563418/37658535e0ab7b355fd4e6f1fd3313e0.png?size=1024")
        emb.set_image(url="https://i.pinimg.com/originals/8f/34/4c/8f344c0b417b86b687ba30ea13f7a341.gif")
        await embed_ahanga.edit(embed=emb)
    except:
        pass



async def changename(duration_string,title,thumbnail):

    giveaway_msg_channel = bot.get_channel(idchannel)

    
    embed_ahanga = await giveaway_msg_channel.fetch_message(int(embed_temp))

    emb = discord.Embed(title=f"[{duration_string}]-{title}", colour =  discord.Color.from_rgb(000,000,000))

    emb.set_footer(text =f"Developer AmirKasra#0991",icon_url="https://cdn.discordapp.com/avatars/643137299701563418/37658535e0ab7b355fd4e6f1fd3313e0.png?size=1024")
    emb.set_image(url=thumbnail)
            
    time.sleep(3)
    await embed_ahanga.edit(embed=emb)








# function, which 'loop' loops, checks the queue and plays the remaining links
def check_new_songs(vc, guild_id):
    global now_playing_pos

    # if the bot is not playing any songs, deleting the queue
    if not vc.is_connected():
        if guild_id in queues:
            del queues[guild_id]
        if guild_id in all_queues_info:
            del all_queues_info[guild_id]
        if guild_id in now_playing_pos:
            del now_playing_pos[guild_id]
        if guild_id in adding_to_queue_ids:
            adding_to_queue_ids.remove(guild_id)
        if guild_id in loops:
            del loops[guild_id]
        return

    # 'loop' track loops
    if guild_id in loops and loops[guild_id] == 'current track':
        try :
            src_url = queues[guild_id][0]['src_url']
            print(40)
            thumbnail=queues[guild_id][0]['thumbnail']
            duration_string=queues[guild_id][0]['duration_string']
            title = queues[guild_id][0]['title']
        except:
            pass
        


        bot.loop.create_task(changename(duration_string,title,thumbnail))
        # play music
        try:
            play_music(vc, src_url, guild_id)
        except discord.errors.ClientException:
            pass
        return

    if queues[guild_id]:
        queues[guild_id].pop(0)

        try:
            src_url = queues[guild_id][0]['src_url']
            
            now_playing_pos[guild_id] += 1
            thumbnail=queues[guild_id][0]['thumbnail']
            duration_string=queues[guild_id][0]['duration_string']
            title = queues[guild_id][0]['title']
            

            


            bot.loop.create_task(changename(duration_string,title,thumbnail))

            
            
            print(412)
        except IndexError:
            
            # if queue is empty and there are tracks adding to queue, then returning
            if guild_id in adding_to_queue_ids:
                return

            # if queue is empty and there is no queue loop, then deleting the variables and return
            if guild_id not in loops or loops[guild_id] != 'queue':
                print(4413)
                del queues[guild_id]
                del all_queues_info[guild_id]
                del now_playing_pos[guild_id]
                if guild_id in loops:
                    del loops[guild_id]

                bot.loop.create_task(changename_basic())
                
                delete= Queuelist.find()
                if delete is not None :
                    for data in delete :
                            Queuelist.delete_one(data)
                
                
                return
            # queue loop
            for track in all_queues_info[guild_id]:
                queues[guild_id].append({'title':track['title'],'url': track['url'], 'src_url': track['src_url'],'duration_string':track['duration_string'],'thumbnail':track['thumbnail']})
            
            now_playing_pos[guild_id] = 0
            src_url = queues[guild_id][0]['src_url']
            thumbnail=queues[guild_id][0]['thumbnail']
            duration_string=queues[guild_id][0]['duration_string']
            title = queues[guild_id][0]['title']
            

        

            bot.loop.create_task(changename(duration_string,title,thumbnail))
            
            print(10)
        # play music
        try:
            play_music(vc, src_url, guild_id)
        except discord.errors.ClientException:
            return


# this function plays music from source url and then calling check_new_songs function
def play_music(vc, src_url, guild_id):
    try:
        if src_url is not None:

        
            vc.play(discord.FFmpegPCMAudio(
                src_url,
                # executable=FFMPEG_PATH,    # If You Use Docker Comment This Line
                before_options=Config.FFMPEG_OPTIONS['before_options'],
                options=Config.FFMPEG_OPTIONS['options']
                # calling the check_new_songs function after playing the current music
            ), after=lambda _: check_new_songs(vc, guild_id))
        else:
            check_new_songs(vc, guild_id)
    except:
        pass




class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True  
        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')



        print('------')



bot = Bot()








class Confirm(discord.ui.View,):
    def __init__(self):
        super().__init__()
        self.value = None


    
    @discord.ui.button(label='', style=discord.ButtonStyle.primary,emoji="<:pause:1014645688417660999>")
    async def pasue(self, interaction: discord.Interaction, button: discord.ui.Button):
        try :
            self.timeout=None
            if interaction.guild.voice_client is None:
                return await interaction.response.send_message('I am not playing any songs for you.',ephemeral=True)

            if interaction.user.voice is None:
                return await interaction.response.send_message(f'{interaction.user.mention}, You have to be connected to a voice channel.',ephemeral=True)

            if interaction.user.voice.channel.id != interaction.guild.voice_client.channel.id:
                return await interaction.response.send_message('You are in the wrong channel.',ephemeral=True)
            if not interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.resume()
                return await interaction.response.send_message('▶️ Successfully resumed.',ephemeral=True)
            
            interaction.guild.voice_client.pause() # stopping a music
            await interaction.response.send_message('⏸️ Successfully paused.',ephemeral=True)

        except:
            self.timeout=None
            pass
    
    @discord.ui.button(label='', style=discord.ButtonStyle.primary,emoji="<:skip:1014645693102694470>")
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        try :
            self.timeout=None
            if interaction.guild.voice_client is None:
                return await interaction.response.send_message('I am not playing any songs for you.',ephemeral=True)

            if interaction.user.voice is None:
                return await interaction.response.send_message(f'{interaction.user.mention}, You have to be connected to a voice channel.',ephemeral=True)

            if interaction.user.voice.channel.id != interaction.guild.voice_client.channel.id:
                return await interaction.response.send_message('You are in the wrong channel.',ephemeral=True)

            interaction.guild.voice_client.stop()  # skipping current track
            await interaction.response.send_message('✅ Successfully skipped.',ephemeral=True)
        except:
            self.timeout=None
            pass
    @discord.ui.button(label='', style=discord.ButtonStyle.red,emoji="<:stop:1014645696718184478>")
    async def Leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        try :
            self.timeout=None
            if interaction.guild.voice_client  is None:
                return await interaction.response.send_message('I am not playing any songs for you.',ephemeral=True)

            if interaction.user.voice is None:
                return await interaction.response.send_message(f'{interaction.user.mention}, You have to be connected to a voice channel.',ephemeral=True)

            if interaction.user.voice.channel.id != interaction.guild.voice_client.channel.id:
                return await interaction.response.send_message('You are in the wrong channel.',ephemeral=True)

            await interaction.guild.voice_client.disconnect()  # leaving a voice channel
            await interaction.response.send_message('✅ Successfully disconnected.',ephemeral=True)
            await changename_basic()
            
            
            delete= Queuelist.find()
            if delete is not None :
                for data in delete :
                        Queuelist.delete_one(data)
            # clearing everything
            
            
            if interaction.guild.id in queues:
                del queues[interaction.guild.id]
            if interaction.guild.id in all_queues_info:
                del all_queues_info[interaction.guild.id]
            if interaction.guild.id in now_playing_pos:
                del now_playing_pos[interaction.guild.id]
            if interaction.guild.id in adding_to_queue_ids:
                adding_to_queue_ids.remove(interaction.guild.id)
            if interaction.guild.id in loops:
                del loops[interaction.guild.id]
        except:
            self.timeout=None
            pass
    
    @discord.ui.button(label='', style=discord.ButtonStyle.red,emoji="<:radio:1016674295126183967>")
    async def radiojavan(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
                self.timeout=None
                channel = interaction.user.voice.channel

                try:
                    await interaction.guild.voice_client.disconnect() # leaving a voice channel
                    delete= Queuelist.find()
                    if delete is not None :
                        for data in delete :
                                Queuelist.delete_one(data)
                    # clearing everything
                    
                    
                    if interaction.guild.id in queues:
                        del queues[interaction.guild.id]
                    if interaction.guild.id in all_queues_info:
                        del all_queues_info[interaction.guild.id]
                    if interaction.guild.id in now_playing_pos:
                        del now_playing_pos[interaction.guild.id]
                    if interaction.guild.id in adding_to_queue_ids:
                        adding_to_queue_ids.remove(interaction.guild.id)
                    if interaction.guild.id in loops:
                        del loops[interaction.guild.id] 
                except:
                    pass 
                
                await changename_basic()
                if interaction.guild.voice_client is None:  # if bot is not connected to a voice channel, connecting to it
                    play = await channel.connect()
                    src_url = "https://stream.rjtv.stream/live/smil:rjtv.smil/playlist.m3u8"
                    play.play(discord.FFmpegPCMAudio(source=src_url))
                           
                if interaction.user.voice.channel.id != interaction.guild.voice_client.channel.id and interaction.guild.voice_client.is_playing() :
                    await interaction.response.send_messag('You are in the wrong channel.',ephemeral=True)
                    await interaction.delete()
                    return
                
                await interaction.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
        except:
            self.timeout=None
            pass


    @discord.ui.button(label='', style=discord.ButtonStyle.primary,emoji="<:loop:1014645681329295411>")
    async def Loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        try :
            self.timeout=None
            global loops

            if interaction.guild.voice_client is None:
                return await interaction.response.send_message('I am not playing any songs for you.',ephemeral=True)

            if interaction.user.voice is None:
                return await interaction.response.send_message(f'{interaction.user.mention}, You have to be connected to a voice channel.',ephemeral=True)

            if interaction.user.voice.channel.id != interaction.guild.voice_client.channel.id:
                return await interaction.response.send_message('You are in the wrong channel.',ephemeral=True)

            # sending a message depending on whether is loop turned on or off
            if interaction.guild.id not in loops:
                loops[interaction.guild.id] = 'queue'
                await interaction.response.send_message('🔁 Queue loop enabled!',ephemeral=True)
            elif loops[interaction.guild.id] == 'queue':
                loops[interaction.guild.id] = 'current track'
                await interaction.response.send_message('🔁 Current track loop enabled!',ephemeral=True)
            else:
                del loops[interaction.guild.id]
                await interaction.response.send_message('❎ Loop disabled!',ephemeral=True)
        except:
            self.timeout=None
            pass







    @discord.ui.button(label='', style=discord.ButtonStyle.primary,emoji="<:shuffle:1014645684764422224>")
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        try :
            self.timeout=None
            global queues
            global all_queues_info

            if interaction.guild.voice_client is None:
                return await interaction.response.send_message('I am not playing any songs for you.',ephemeral=True)

            if interaction.user.voice is None:
                return await interaction.response.send_message(f'{interaction.user.mention}, You have to be connected to a voice channel.',ephemeral=True)

            if interaction.user.voice.channel.id != interaction.guild.voice_client.channel.id:
                return await interaction.response.send_message('You are in the wrong channel.',ephemeral=True)

            if interaction.guild.id not in all_queues_info or len(all_queues_info[interaction.guild.id]) == 0:
                return await interaction.response.send_message('Your queue is empty!',ephemeral=True)

            # getting next songs from the queue
            next_songs = all_queues_info[interaction.guild.id][now_playing_pos[interaction.guild.id] + 1:]
            # getting previous songs from the queue
            previous_songs = all_queues_info[interaction.guild.id][:now_playing_pos[interaction.guild.id] + 1]

            if len(next_songs) <= 1:
                return await interaction.response.send_message('Not enough songs to shuffle.',ephemeral=True)

            # shuffling next songs
            shuffled_next_songs = next_songs.copy()
            while shuffled_next_songs == next_songs:
                random.shuffle(shuffled_next_songs)

            # replacing the queue
            all_queues_info[interaction.guild.id] = previous_songs + shuffled_next_songs
            queues[interaction.guild.id] = []
            for song in all_queues_info[interaction.guild.id][now_playing_pos[interaction.guild.id]:]:
                queues[interaction.guild.id].append({'url': song['url'], 'src_url': song['src_url'],'thumbnail':song['thumbnail'] ,'duration_string':song['duration_string'],'title':song['title']})

            await interaction.response.send_message('✅ Next songs were successfully shuffled.',ephemeral=True)
        except:
            self.timeout=None
            pass






@bot.event
async def on_message(message):


    

    if message.author == bot.user:
        return   
    if message.channel.id == idchannel:  # Please Enter Id Of the channel where you want to setup music bot.
            global temp ,embed_temp , Queue , ydl
            if message.content == "!setup":   
                view = Confirm()
                view.timeout=None
                
                channel = bot.get_channel(idchannel)
                list_ahangha = await channel.send(text)
                emb = discord.Embed(title="Vibing Alone 😎",description = f'Anything you type in this channel will be interpreted as a video title', colour =  discord.Color.from_rgb(000,000,000))
                temp= + list_ahangha.id
                

                emb.set_footer(text =f"Developer AmirKasra#0991",icon_url="https://cdn.discordapp.com/avatars/643137299701563418/37658535e0ab7b355fd4e6f1fd3313e0.png?size=1024")
                emb.set_image(url="https://i.pinimg.com/originals/8f/34/4c/8f344c0b417b86b687ba30ea13f7a341.gif")
                embed_ahanga=await channel.send(embed=emb, view=view)
                embed_temp =+ embed_ahanga.id

            else:

                global queues, all_queues_info, now_playing_pos
                
                query = str(message.content)
                
                giveaway_msg_channel = bot.get_channel(idchannel)
                list_ahangha = await giveaway_msg_channel.fetch_message(int(temp))
                embed_ahanga = await giveaway_msg_channel.fetch_message(int(embed_temp))
                await spotify_client.get_auth_token_with_client_credentials()
                await spotify_client.create_new_client()

                if message.author.voice is None:
                    
                    await message.channel.send(f'{message.author.mention}, You have to be connected to a voice channel.',delete_after=5)
                    await message.delete()
                    return 

                channel = message.author.voice.channel
                
                if message.guild.voice_client is None:  # if bot is not connected to a voice channel, connecting to it
                    await channel.connect()
                if message.author.voice.channel.id != message.guild.voice_client.channel.id and message.guild.voice_client.is_playing() :
                    await message.channel.send('You are in the wrong channel.',delete_after=5)
                    await message.delete()
                    return
                else:
                    await message.guild.voice_client.move_to(channel)
                
                await message.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)  # self deaf

                  # saving source query
                
                url = ''
                spotify_link_info = None
                soundcloud_info = None
                link_music = None
                playlist_youtube = None
                
                if '.mp3' in query:
                    src_url=query
                    vc = message.guild.voice_client
                    

                    title="None"
                    duration_string="None"
                    thumbnail = "https://cdn.appleosophy.com/2021/08/e33e2e5aa6c4d1f9e889b22193f2b67ad94fda35.png"
                    
                    if message.guild.id in queues:
                            queues[message.guild.id].append({'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'})
                            all_queues_info[message.guild.id].append({'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'})

                    else:
                        queues[message.guild.id] = [{'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'}]
                        now_playing_pos[message.guild.id] = 0
                        all_queues_info[message.guild.id] = [{'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'}]


                if 'soundcloud.com/' in query :
                    if "/set" not in query:
                        
                        try :
                            urlb=query 

                            soundcloud_info = ydl.extract_info(urlb , download=False)
                            title=soundcloud_info['title']
                            src_url=soundcloud_info['formats'][2]['url']
                            thumbnail=soundcloud_info["thumbnail"]
                            duration_string="None"
                            
                            if message.guild.id in queues:
                                print(120)
                                queues[message.guild.id].append({'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'})
                                all_queues_info[message.guild.id].append({'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'})
                                await message.delete()

                            else:
                                queues[message.guild.id] = [{'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'}]
                                now_playing_pos[message.guild.id] = 0
                                all_queues_info[message.guild.id] = [{'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'}]
                                await message.delete()
                        except:
                            await message.delete()
                            return await message.channel.send('Unknown soundcloud url.',delete_after=5)
                    else:
                        await message.delete()
                        return await message.channel.send('playlist soundcloud support nemishe.',delete_after=5)

                        # try:
                        #         urlz=query 

                                
                        #         duration_string="None"
                        #         thumbnail="https://cdn.appleosophy.com/2021/08/e33e2e5aa6c4d1f9e889b22193f2b67ad94fda35.png"
                                                        
                                                         
                                
                        #         soundcloud_info = ydl.extract_info(urlz, download=False,process=False)

                        #         id_tracks=[]
                                
                        #         id_tracks.clear()
                        #         await message.channel.send(f'{message.author.mention} plz w8 to load playlist',delete_after=5)
                                
                        #         for i in soundcloud_info["entries"] :
                        #             id_tracks.append(i["id"])

                                    


                                

                        #         for id in id_tracks: 
                        #             url=f"https://api-v2.soundcloud.com/tracks/{id}?client_id=HSxMgfrLBAtUfKoMezWmzJLMra1YY5ZQ"
                        #             headers = {'content-type': 'application/json','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}
                        #             check=requests.get(url, headers=headers).json()
                        #             await bot.wait_until_ready()
                        #             await blocking_func(1)
                        #             try:
                        #                 linkx = check["media"]["transcodings"][1]["url"]+"?client_id=HSxMgfrLBAtUfKoMezWmzJLMra1YY5ZQ"
                        #                 title = "None"
                        #             except:
                        #                 try:
                        #                     linkx = check["media"]["transcodings"]["url"]+"?client_id=HSxMgfrLBAtUfKoMezWmzJLMra1YY5ZQ"
                        #                     title = "None"
                        #                 except:
                        #                     pass
                                                                
                        #             try:                            
                        #                 checks = requests.get(linkx, headers=headers).json()
                        #                 src_url = checks['url']
                        #             except:
                        #                 pass

                        #             if message.guild.id in queues:
                        #                 print(120)
                        #                 queues[message.guild.id].append({'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'})
                        #                 all_queues_info[message.guild.id].append({'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'})


                        #             else:
                        #                 queues[message.guild.id] = [{'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'}]
                        #                 now_playing_pos[message.guild.id] = 0
                        #                 all_queues_info[message.guild.id] = [{'url':'','title':title, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':'None'}]
                                
                        #         vc = message.guild.voice_client
                        #         await message.delete()
                        # except:

                        #     await message.delete()
                        #     return await message.channel.send('Unknown soundcloud url.',delete_after=5)

                        


                # if the query has a YouTube link, using this link
                
                if 'youtube.com/' in query and 'youtube.com/playlist'  not in query:
                    try :
                        urlz=query
                        


                        info = ydl.extract_info(urlz , download=False)
                        url = info["url"]

                        titlex = info["title"]
                    except :
                        await message.delete()
                        return await message.channel.send('Unknown YouTube url.',delete_after=5)
                
                       
                    
                elif 'youtube.com/playlist'   in query:
                    await message.delete()
                    return await message.channel.send('Unknown YouTube url.',delete_after=5)


                # else if the query has a Spotify link, extracting info from this link
                elif 'open.spotify.com/' in query:
                    for el in query.split():
                        if 'open.spotify.com/' in el:
                            query = el
                            break

                    _type = list(filter(None, query.split('/')))[-2]
                    _id = list(filter(None, query.split('/')))[-1].split('?')[0]

                    try:
                        if _type == 'track':
                            spotify_link_info = await spotify_client.track.get_one(_id)
                        elif _type == 'album':
                            spotify_link_info = await spotify_client.albums.get_one(_id)
                        elif _type == 'playlist':
                            spotify_link_info = await spotify_client.playlists.get_one(_id)
                        else:
                            raise TypeError
                    except SpotifyBaseError and TypeError:
                        
                        await message.channel.send(
                            f'Unknown Spotify url. Make sure you entered the link correctly and that your link leads to opened ' +
                            'Spotify track/album/playlist.',delete_after=5)
                        await message.delete()
                        return

                    if spotify_link_info['type'] == 'track':
                        print(4555)
                        # if it's single Spotify track, getting his YouTube url and playing as usual
                        spotify_link_info['full_name'] =\
                            get_sp_track_full_name(spotify_link_info['artists'], spotify_link_info['name'])
                        spotify_link_info['yt_url'] = await get_sp_track_yt_url(spotify_link_info['full_name'])
                        
                        if spotify_link_info['yt_url'] is None:  # error handling
                            return await message.channel.send(f'Your song was not found. Try another one.',delete_after=5)
                        url = spotify_link_info['yt_url']

                    else:
                        # if it's Spotify playlist or album, sorting through each track and getting YouTube url of the track

                        # getting all tracks
                        next_link = spotify_link_info['tracks']['next']
                        while next_link:
                            next_tracks = await spotify_client.next(next_link)
                            spotify_link_info['tracks']['items'] += next_tracks['items']
                            next_link = next_tracks['next']

                        # if it was Spotify playlist, removing all episodes from it and moving item['track'] to item
                        if spotify_link_info['type'] == 'playlist':
                            episode_indexes = []
                            print(0)
                            for i in range(len(spotify_link_info['tracks']['items'])):
                                if not spotify_link_info['tracks']['items'][i]['track']:
                                    episode_indexes.append(i)
                                else:
                                    spotify_link_info['tracks']['items'][i].update(spotify_link_info['tracks']['items'][i]['track'])
                                    del spotify_link_info['tracks']['items'][i]['track']

                            episode_indexes.reverse()
                            for episode_index in episode_indexes:
                                spotify_link_info['tracks']['items'].pop(episode_index)

                        if len(spotify_link_info['tracks']['items']) == 0:  # if there is no tracks, returning
                            await message.channel.send('There is no tracks in your Spotify playlist/album.',delete_after=5)
                            await message.delete()
                            return 
                            
                        # getting yt_url of the first track
                        spotify_link_info['tracks']['items'][0]['full_name'] =\
                            get_sp_track_full_name(spotify_link_info['tracks']['items'][0]['artists'],
                                                spotify_link_info['tracks']['items'][0]['name'])
                        spotify_link_info['tracks']['items'][0]['yt_url'] =\
                            await get_sp_track_yt_url(spotify_link_info['tracks']['items'][0]['full_name'])
                            
                        if spotify_link_info['tracks']['items'][0]['yt_url'] is None:
                            await message.channel.send(f'One of the songs in the album/playlist was not found, so this song will not play.',delete_after=5)
                            await message.delete()
                            print(54545455454545454545454545)

                # if the query consists of something else, searching it on YouTube
                elif soundcloud_info is None and link_music is None and playlist_youtube is None:
                    search_obj = VideosSearch(query, limit=1)
                    try:
                        url = (await search_obj.next())['result'][0]['link']
                        print(4545454)
                    except IndexError:
                        # if video not found, sending message
                        await message.channel.send(f'Video titled \'{search_obj.data["query"]}\' not found. Try another video title.',delete_after=5)
                        await message.delete()
                        return

                # extracting source video/track url and playing song as usual
                # if it's not a Spotify playlist/album or a YouTube playlist
                if (spotify_link_info is None or spotify_link_info['type'] == 'track') and 'list=' not in url and soundcloud_info is None and link_music is None and playlist_youtube is None:
                    print(url)
                    if "https://rr" in url :
                        src_url=url
                        title = titlex
                        duration_string = "None"
                        thumbnail = "https://cdn.appleosophy.com/2021/08/e33e2e5aa6c4d1f9e889b22193f2b67ad94fda35.png"

                    
                    else:


                        information_serch = await YouTubeWrapper.search(query)
                        information = ydl.extract_info(information_serch, download=False)
                        src_url = information['url']
                        title = information['title']
                        
                        duration_string =  "None"
                        thumbnail = "https://cdn.appleosophy.com/2021/08/e33e2e5aa6c4d1f9e889b22193f2b67ad94fda35.png"
                        


                    await message.delete()
                    if spotify_link_info is not None:  # changing title and link if it is Spotify track
                        title = spotify_link_info['full_name']
                        url = spotify_link_info['external_urls']['spotify']
                        print(53355554545)

                    # filling queues
                    if message.guild.id in queues:
                        queues[message.guild.id].append({'title':title,'url': url, 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':duration_string})
                        all_queues_info[message.guild.id].append({'title':title,'name': title, 'url': url, 'src_url': src_url,'thumbnail':thumbnail ,'duration_string':duration_string})
                        print(533555)
                    else:
                        queues[message.guild.id] = [{'title':title,'url': url, 'src_url': src_url,'thumbnail':thumbnail ,'duration_string':duration_string}]
                        now_playing_pos[message.guild.id] = 0
                        all_queues_info[message.guild.id] = [{'title':title,'name': title, 'url': url, 'src_url': src_url,'thumbnail':thumbnail ,'duration_string':duration_string}]
                        print(2525)

                elif spotify_link_info is not None\
                        and (spotify_link_info['type'] == 'album' or spotify_link_info['type'] == 'playlist'):
                    # if it's Spotify playlist/album, adding to queue first track
                    # and extracting its source url (if its YouTube url was found)
                    first_track_info = spotify_link_info['tracks']['items'][0]
                   
                    title = spotify_link_info['tracks']["items"][0]['full_name']
                   
                    url = spotify_link_info['external_urls']['spotify']

                    thumbnail= "https://cdn.appleosophy.com/2021/08/e33e2e5aa6c4d1f9e889b22193f2b67ad94fda35.png"
                    
                    millis=spotify_link_info['tracks']["items"][0]['duration_ms']
                    millis = int(millis)
                    seconds=(millis/1000)%60
                    seconds = int(seconds)
                    minutes=(millis/(1000*60))%60
                    minutes = int(minutes)
                    
                    duration_string="%d:%d" % (minutes, seconds)

                    if first_track_info['yt_url'] is not None:
                        print(59)
                        event_loop = asyncio.get_event_loop()
                        information =\
                            await event_loop.run_in_executor(ThreadPoolExecutor(), extract_info, first_track_info['yt_url'])
                        src_url = information['url']

                    else:
                        print(52)
                        src_url = None

                    if message.guild.id in queues:
                        print(56)
                        queues[message.guild.id].append({'url': first_track_info['external_urls']['spotify'], 'src_url': src_url,'thumbnail':thumbnail,'duration_string':duration_string,'title':title})
                        all_queues_info[message.guild.id].append(
                            {'name': first_track_info['full_name'],
                            'url': first_track_info['external_urls']['spotify'], 'src_url': src_url,'thumbnail':thumbnail,'duration_string':duration_string,'title':title})
                    else:
                        print(5)
                        queues[message.guild.id] = [{'url': first_track_info['external_urls']['spotify'], 'src_url': src_url,'thumbnail':thumbnail,'duration_string':duration_string,'title':title}]
                        now_playing_pos[message.guild.id] = 0
                        all_queues_info[message.guild.id] = [{
                            'name': first_track_info['full_name'],
                            'url': first_track_info['external_urls']['spotify'], 'src_url': src_url,'thumbnail':thumbnail,'duration_string':duration_string,'title':title}]
                    adding_to_queue_ids.append(message.guild.id)

                else:  # if it's YouTube playlist, adding to queue first video and extracting its source url
                    if soundcloud_info is None and link_music is None and playlist_youtube is None:
                        playlist = Playlist(url)
                        event_loop = asyncio.get_event_loop()
                        information = await event_loop.run_in_executor(ThreadPoolExecutor(), extract_info, playlist.video_urls[0])
                        src_url = information['url']
                        title = playlist.title
                        duration_string = information['duration_string']
                        thumbnail = information['thumbnail']
                        
                        # queuing first song
                        if message.guild.id in queues:
                            print(59)
                            queues[message.guild.id].append({'title':title,'url': playlist.video_urls[0], 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':duration_string})
                            all_queues_info[message.guild.id].append(
                                {'name': information['title'], 'url': playlist.video_urls[0], 'src_url': src_url,'thumbnail':thumbnail ,'duration_string':duration_string})
                        else:
                            print(54568)
                            queues[message.guild.id] = [{'title':title,'url': playlist.video_urls[0], 'src_url': src_url,'thumbnail':thumbnail ,'duration_string':duration_string}]
                            now_playing_pos[message.guild.id] = 0
                            all_queues_info[message.guild.id] = [
                                {'name': information['title'], 'url': playlist.video_urls[0], 'src_url': src_url ,'thumbnail':thumbnail ,'duration_string':duration_string}]
                        adding_to_queue_ids.append(message.guild.id)
                        await message.delete()

                vc = message.guild.voice_client

                # play music
                try:
                    play_music(vc, src_url, message.guild.id)
                except discord.errors.ClientException:
                    pass

                # sending embed, depending on the queue
                if len(queues[message.guild.id]) != 1:

                    dt = datetime.now()
                    ts = datetime.timestamp(dt)
                    dict1 = [{"ServerId":int(message.guild.id),"Queuelist":f"{title}","time":int(ts)}] 
                    Queuelist.insert_many(dict1)

                
                    for x in Queuelist.find({"ServerId":int(message.guild.id)}).sort("time",1):
                        Queue.append({'Queuelist':x['Queuelist']})    
                    tempQueue=""
                    

                    for idx,x in enumerate(Queue):
                            idx+=1
                            temptitle = x["Queuelist"]
                            tempQueue += f"{str(idx)}.{temptitle} \n"
                    await list_ahangha.edit(content=f"{tempQueue}")
                        
                    Queue.clear()


                
                else:
                    
                    checkdata=Queuelist.find({"ServerId":int(message.guild.id)})
                    if checkdata is not None:
                        delete= Queuelist.find()
                        for data in delete :
                            Queuelist.delete_one(data)

                    emb = discord.Embed(title=f"[{duration_string}]-{title}", colour =  discord.Color.from_rgb(000,000,000))

                    emb.set_footer(text =f"Developer AmirKasra#0991",icon_url="https://cdn.discordapp.com/avatars/643137299701563418/37658535e0ab7b355fd4e6f1fd3313e0.png?size=1024")
                    emb.set_image(url=thumbnail)
                    
                    

                    await embed_ahanga.edit(embed=emb)


                # adding to queue remaining tracks of Spotify playlist or album
                if spotify_link_info is not None\
                        and (spotify_link_info['type'] == 'album' or spotify_link_info['type'] == 'playlist'):
                    print(85)
                    for i in range(len(spotify_link_info['tracks']['items'])):
                        if i == 0:
                            continue

                        if message.guild.id not in adding_to_queue_ids:  # if no longer need to add new tracks, returning
                            return

                        track = spotify_link_info['tracks']['items'][i]
                        print(86)
                        # getting yt_url of the track
                        track['full_name'] = get_sp_track_full_name(track['artists'], track['name'])
                        track['yt_url'] = await get_sp_track_yt_url(track['full_name'])
                        if track['yt_url'] is None:
                            await message.channel.send(f'One of the songs in the album/playlist was not found, so this song will not play.',delete_after=5)
                            
                            continue

                        event_loop = asyncio.get_event_loop()
                        track_yt_information = await event_loop.run_in_executor(ThreadPoolExecutor(), extract_info, track['yt_url'])
                        src_track_url = track_yt_information['url']
                        
                        millis=track['duration_ms']
                        millis = int(millis)
                        seconds=(millis/1000)%60
                        seconds = int(seconds)
                        minutes=(millis/(1000*60))%60
                        minutes = int(minutes)
                    
                        duration_string ="%d:%d" % (minutes, seconds)
                        
                     
                        thumbnail = "https://cdn.appleosophy.com/2021/08/e33e2e5aa6c4d1f9e889b22193f2b67ad94fda35.png"

                        if message.guild.id in adding_to_queue_ids:

                            # if the previous songs have already been played, then playing current one
                            if not queues[message.guild.id]:
                                now_playing_pos[message.guild.id] += 1
                                try:
                                    play_music(vc, src_track_url, message.guild.id)
                                except discord.errors.ClientException:
                                    pass
                            print(8141)
                            
                            queues[message.guild.id].append({'url': track['external_urls']['spotify'], 'src_url': src_track_url,'title': track['full_name'],'thumbnail':thumbnail,'duration_string':duration_string})
                            all_queues_info[message.guild.id].append(
                                {'name': track['full_name'], 'url': track['external_urls']['spotify'], 'src_url': src_track_url,'title': track['full_name'] ,'thumbnail':thumbnail,'duration_string':duration_string})

                    adding_to_queue_ids.remove(message.guild.id)

                    # if all tracks weren't found, returning
                    if len(spotify_link_info['tracks']['items']) == 0:
                        await message.channel.send('All tracks from your album/playlist weren\'t found.',delete_after=5)
                        return  await message.delete()
                        

                    await message.channel.send('✅ Spotify playlist/album was fully added to the queue.',delete_after=5)


                elif 'list=' in url:  # adding to queue remaining tracks of YouTube playlist
                    playlist = Playlist(url)
                    print(8143)
                    for i in range(len(playlist.video_urls)):
                        if i == 0:
                            continue

                        if message.guild.id not in adding_to_queue_ids:  # if no longer need to add new tracks, returning
                            return

                        event_loop = asyncio.get_event_loop()
                        information = await event_loop.run_in_executor(ThreadPoolExecutor(), extract_info,
                                                                    playlist.video_urls[i])
                        src_video_url = information['url']
                        duration_string = information['duration_string']
                        thumbnail = information['thumbnail']
                        print(information)
                        if message.guild.id in adding_to_queue_ids:
                            # if the previous videos have already been played, then playing current one
                            if not queues[message.guild.id]:
                                now_playing_pos[message.guild.id] += 1
                                try:
                                    play_music(vc, src_video_url, message.guild.id)
                                except discord.errors.ClientException:
                                    pass
                            print(810)
                            queues[message.guild.id].append({'url': playlist.video_urls[i], 'src_url': src_video_url,'duration_string':duration_string,'thumbnail':thumbnail,'title':information['title']})
                            all_queues_info[message.guild.id].append(
                        
                                {'name': information['title'], 'url': playlist.video_urls[i], 'src_url': src_video_url,'duration_string':duration_string,'thumbnail':thumbnail,'title':information['title']})

                    adding_to_queue_ids.remove(message.guild.id)
                    await message.channel.send('✅ YouTube playlist was fully added to the queue.',delete_after=5)
                    await message.delete()
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel and not after.channel :
        if member.id == 1010454865115365377:
            await changename_basic()

                    



if __name__ == '__main__':
    bot.run(TOKEN)  # bot launch
    asyncio.run(spotify_client.close_client())  # closing Spotify client after exit
