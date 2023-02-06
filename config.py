# Config file
import os



def selectPath(name):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)


with open(selectPath("cookies.txt"),"rb") as f:
    file_data = f.read()

TOKEN = ''  # write here your bot token

BOT_COLOR = 0x515596  # color of embeds
# FFMPEG_PATH =  "C:/path/ffmpeg.exe"  # write here your ffmpeg path
COOKIES_FILE_PATH = file_data  # write here your cookies file path



SPOTIFY_CLIENT_ID = ''  # write here your spotify client id
SPOTIFY_CLIENT_SECRET = ''  # write here your spotify client secret
 
FFMPEG_OPTIONS = {  # ffmpeg options
	'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
	'options': '-vn'
}
