import telebot
#file with the token
import keys
#to log
from datetime import datetime
import json
import time
#to delete files
import os
#to download
import requests
#for conversion
from pydub import AudioSegment
from pydub.playback import play
#for playback
import vlc
#notes:
#pydub si incasina e a volte non parte, o non si ferma
#from playsound import playsound #playsound è semplice ma non stoppabile e una sopra l'altra, e fa dei click
#import pygame # pygame  può stopparsi,ma distorce
#text-to-speech
from gtts import gTTS
language = "it"

token = keys.telegram_bot_token

bot = telebot.TeleBot(token)
player = vlc.MediaPlayer()
#starting status of voice/audio playing
muted = False
#starting status of Text-to-speech
tts = True

#log function
def log(str_passed):
    #print on shell
    print(str_passed)
    #and write on file
    with open('log.txt', 'a+') as filelog:
        if not filelog.read().endswith('\n'):
            filelog.write('\n')
        filelog.write(str_passed)
        filelog.close()
    return


############## COMMANDS FOR THE BOT ##################
#when it starts or someone asks help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hi, I'm " + bot.get_me().first_name + ", send me any audio (music or voice) (max 20 MB) and I will play it in the kitchen of Bocca4 \nYou can use commands:\n /help to see this \n /status to see status, like muted or not \n")

#asking the status of the bot
@bot.message_handler(commands=['status'])
def send_status(message):
    global muted
    global tts
    bot.reply_to(message, "Bot is working\nBot is" + (" " if muted else " NOT ") +"MUTED\nTTS is" + (" " if tss else " NOT ") +" ENABLED")

#change muted or not
@bot.message_handler(commands=['toggle_muted'])
def set_mute(message):
    global muted
    muted = not muted
    bot.reply_to(message, "Bot is" + (" " if muted else " NOT ") +"MUTED")
    sender = message.from_user.first_name
    log(sender + (" " if muted else " NOT ") +"MUTED the bot at "+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

#asks the bot for the last 5 people sent audio/voices
@bot.message_handler(commands=['lastlog'])
def send_log(message):
    with open('log.txt') as filelog:
        lastlog=""
        for line in (filelog.readlines() [-5:]):
            lastlog+= line
    bot.reply_to(message, "Last messages are: \n" + lastlog)
    sender = message.from_user.first_name

#size of the temporary folder that contains all the audio received
@bot.message_handler(commands=['tmp_size'])
def send_size(message):
    bot.reply_to(message, "Folder size is: \n" + str(sum(d.stat().st_size for d in os.scandir('./tmp') if d.is_file())/1000000)  + " MB")

#delete the audios in the temporary folder to free space
@bot.message_handler(commands=['tmp_delete'])
def send_del(message):
    mydir="./tmp"
    #deleting all files
    filelist = [ f for f in os.listdir(mydir)]
    for f in filelist:
        os.remove(os.path.join(mydir, f))
    #deleting directory
    os.rmdir(mydir)
    #creating directory
    os.mkdir(mydir)
    bot.reply_to(message, "Files in folder tmp deleted")
    sender = message.from_user.first_name
    log(sender + " DELETED TMP at "+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

#stops the last audio playing
@bot.message_handler(commands=['stop'])
def send_size(message):
    global player
    player.stop()
    bot.reply_to(message, "Stopped")
    sender = message.from_user.first_name
    log(sender + " STOPPED at "+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


############## MESSAGES HANDLED ##################
# Handles all sent AUDIO files
@bot.message_handler(content_types=['audio'])
def handle_docs_audio(message):
    global muted
    if not muted:
        sender = message.from_user.first_name
        #log msg RECEIVED
        log(sender + " sent a audio at "+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        bot.send_message(message.chat.id,"audio received")
        bot_message_id=message.message_id+1
        #retrieve file link
        file_id = message.audio.file_id
        file = bot.get_file(file_id)
        try:
            file_path = file.file_path
            global token
            link = "https://api.telegram.org/file/bot"+token+"/"+file_path
            #DOWNLOAD link
            print("Download of: " + link)
            #bot.edit_message_text("audio downloading",chat_id=message.chat.id, message_id=bot_message_id)
            #bot.send_message(message.chat.id,"audio downloading")
            myfile = requests.get(link)
            filename=datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+"-"+sender
            fileformat = link.split('.')[-1]
            open('./tmp/'+filename+"."+fileformat, 'wb').write(myfile.content)
            #CONVERSION
            #print('Ok, conversion...')
            #bot.send_message(message.chat.id,"audio converting")
            #sound = AudioSegment.from_file("./tmp/"+filename+"."+fileformat, format=fileformat)
            #sound.export("./tmp/"+filename+".mp3", format="mp3")
            #deleting old file to leave only the mp3
            #os.remove("./tmp/"+filename+"."+fileformat)
            #PLAY
            print('OK, Playing!')
            #bot.edit_message_text("audio played!",chat_id=message.chat.id, message_id=bot_message_id)
            bot.send_message(message.chat.id,"audio playing!")
            #sound = AudioSegment.from_file("./tmp/"+filename+"."+fileformat, fileformat)
            #play(sound)
            #pygame.mixer.init()
            #pygame.mixer.music.load("./tmp/"+filename+"."+fileformat)
            #pygame.mixer.music.play()
            global player
            player = vlc.MediaPlayer("./tmp/"+filename+"."+fileformat) #changed this to mp3 if you convert
            player.play()
        except ApiTelegramException as e:
            bot.send_message(message.chat.id,"*Error* " +file.description)
    else:
        bot.send_message(message.chat.id,"Someone did a mess, \nthe BOT is MUTED")


# Handles all sent VOICE files
@bot.message_handler(content_types=['voice'])
def handle_docs_voice(message):
    global muted
    if not muted:
        sender = message.from_user.first_name
        #log msg RECEIVED
        log(sender + " sent a voice at "+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        #bot.send_message(message.chat.id,"voice received")
        bot_message_id=message.message_id+1
        #retrieve file link
        file_id = message.voice.file_id
        file = bot.get_file(file_id)
        file_path = file.file_path
        global token
        link = "https://api.telegram.org/file/bot"+token+"/"+file_path
        #DOWNLOAD link
        print("Download of: " + link)
        #bot.edit_mesassage_text("voice downloading",chat_id=message.chat.id, message_id=bot_message_id)
        #bot.send_message(message.chat.id,"voice downloading")
        myfile = requests.get(link)
        filename=datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+"-"+sender
        fileformat = link.split('.')[-1]
        open('./tmp/'+filename+"."+fileformat, 'wb').write(myfile.content)
        #CONVERSION
        print('Ok, conversion...')
        #bot.edit_message_text("voice converting",chat_id=message.chat.id, message_id=bot_message_id)
        sound = AudioSegment.from_file("./tmp/"+filename+"."+fileformat, format="ogg") #it's .oga but ogg works
        sound.export("./tmp/"+filename+".mp3", format="mp3")
        #deleting old file to leave only the mp3
        if os.path.exists("./tmp/"+filename+"."+fileformat):
            os.remove("./tmp/"+filename+"."+fileformat)
        else:
            print("The file does not exist")
        #PLAY
        print('OK, Playing!')
        #bot.edit_message_text("voice played!",chat_id=message.chat.id, message_id=bot_message_id)
        global player
        player = vlc.MediaPlayer("./tmp/"+filename+".mp3")
        player.play()
        #send voice
        #voice = open('./tmp/voice.ogg', 'rb')
        #bot.send_voice(message.chat.id, voice)
    else:
        bot.send_message(message.chat.id,"Someone did a mess, \nthe BOT is MUTED")

#handling OTHER MESSAGES
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    global muted
    global tts
    if not muted and tts:
        sender = message.from_user.first_name
        #log
        #log(sender + " sent a message at "+ datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(sender + " sent a message TTS at "+ datetime.now().strftime('%Y-%m-%d %H:%M:%S')) #not logged
        #reply the same message
        #bot.send_message(message.chat.id, " From " + sender + " -> " + message.text)
        #bot.send_message(message.chat.id, "send me a voice and I will play it, why texting me???")
        global language
        text = sender + " dice: " + message.text
        print('generationg audio...')
        speech = gTTS(text = text, lang = language, slow = False)
        print('saving audio...')
        speech.save("text.mp3")
        print('OK, Playing!')
        global player
        player = vlc.MediaPlayer("./text.mp3")
        player.play()

#main loop
for x in range(6):
    try:
        print("##### BOT STARTED #####")
        #POLLING
        bot.polling()
    except Exception:
        print(Exception)
        print("#attempt " + str(x+1) + "/6 in 20 seconds\n\n")
        time.sleep(20)
