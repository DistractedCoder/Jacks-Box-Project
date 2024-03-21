from flask import Flask, render_template
from flask_sockets import Sockets
import socket as socketLibrary#ip address
import os, sys
import csv
import threading
import random
import subprocess
import json

#################################################################################################
#################################################################################################
####                                                                                         ####
#### Update ADDRESS to your IP address if the auto IP detection does not work. Wifi Specific ####
#### Settings found in ..\Jackbox-Game-Data\Jackbox Game_Data\StreamingAssets\Settings.json  ####
####                                                                                         ####
#################################################################################################
#################################################################################################




SERVER_TYPE="TriviaRacetrack"

app = Flask(__name__)
sockets = Sockets(app)

stop_threads = False
allTrivia = []
currentlyUsedTrivia = [] #this will be up to 500 previous questions, insert only first
currentlyGeneratingTTS = False;
loserCallouts = []


#load IP address from unity settings
with open('../Jackbox-Game-Data/Jackbox Game_Data/StreamingAssets/Settings.json', 'r', encoding='utf-8') as file:
    settingsJsonData = json.load(file)

address = settingsJsonData["ServerSettings"]["Data"]["Address"]
port = settingsJsonData["ServerSettings"]["Data"]["Port"]
maskIpAddress = settingsJsonData["ServerSettings"]["Data"]["DontDisplayIpAddress"]


# List to keep track of connected WebSocket clients
connected_sockets = []

@sockets.route('/websocket')
def websocket(ws):
    global allTrivia, currentlyUsedTrivia, currentlyGeneratingTTS,connected_sockets
    connected_sockets.append(ws)
    try:
        while not ws.closed:
            original_message = ws.receive()
            if original_message:
                print('Received message:', original_message)
                message = original_message.split(";")
                
                if (message[0] == "unity_validate"):
                    #reset connected sockets
#                    connected_sockets = []
#                    connected_sockets.append(ws)
                    #send server name back to unity
                    for socket in connected_sockets:
                        socket.send("python_server;" + SERVER_TYPE)
                    
                if (message[0] == "unity_01_generate_questions"):
                    #get total questions and begin generation
                    #threaded
                    total = int(message[1])
                    generateTTSThread = threading.Thread(target=lambda: PickTriviaAndGenerateTTS(total), daemon=True)
                    generateTTSThread.start()
                
                if (message[0] == "unity_01_stop_generate_questions"):
                    #stop TTS generation if necessary
                    currentlyGeneratingTTS = False
                    connected_sockets = []
                    
                
                if (message[0] == "unity_02_get_question"):
                    #send question
                    #       0                1        2         3         5       6
                    #["Which of ... fur?","Reptile","Bird","Amphibian","Mammal*",""]
                    current = int(message[1])
                    for socket in connected_sockets:
                        socket.send("python_03_send_question;" + ";".join(allTrivia[currentlyUsedTrivia[current]]))
#                        socket.send("python_03_send_question;" + ";".join(allTrivia[2])) #temp
                    
                if (message[0] == "unity_confirmation_login"):
                    #threaded
                    threading.Thread(target=lambda: GenerateLoserPlayerCallout(message[1]), daemon=True).start()
                
                #message is forwarded
                if (message[0] == "unity_reload_webpage"): #only for new games
                    #forward message
                    for socket in connected_sockets:
                        socket.send(original_message)
                    #reset connected sockets
                    connected_sockets = []
                        
                if (message[0] == "phone_00_login"):
                    #forward message
                    for socket in connected_sockets:
                        socket.send(original_message)
                        
                if (message[0] == "unity_error" or message[0] == "unity_confirmation_login"):
                    #forward message
                    for socket in connected_sockets:
                        socket.send(original_message)
                
                if (message[0] == "phone_skip_intro"):
                    #forward message
                    for socket in connected_sockets:
                        socket.send(original_message)
                
                if (message[0] == "unity_04_send_answers"):
                    #forward message
                    for socket in connected_sockets:
                        socket.send(original_message)
                        
                if (message[0] == "phone_05_send_answer"):
                    #forward message
                    for socket in connected_sockets:
                        socket.send(original_message)
                    
                if (message[0] == "unity_reset_to_waiting"):
                    #forward message
                    for socket in connected_sockets:
                        socket.send(original_message)
                

    except Exception as e:
        print(e)
    finally:
        # Remove the WebSocket from the list when the connection is closed
        connected_sockets.remove(ws)

@app.route('/')
def index():
    return render_template('index.html')


def LoadTriviaQuestions():
    global allTrivia
    data = ""
    with open("game_data/TriviaRacetrack/trivia_all.txt", 'r', encoding='utf-8') as content_file:
        data = content_file.read().split("\n")
    
    for i in range(len(data)):
        data[i] = data[i].strip().split(';')
        #all trivia is correct length
#        if (len(data[i]) != 6):
#            print(i,data[i])
    
    allTrivia = data
    
    #threaded, aborted only if unity game starts the generation, backs out of the game, and loads back in
def PickTriviaAndGenerateTTS(total):
    global allTrivia, currentlyUsedTrivia, currentlyGeneratingTTS
    currentlyGeneratingTTS = True
    print("past trivia:",len(currentlyUsedTrivia))
    for i in range(total):
        temp = random.randint(0,len(allTrivia))
        while (temp in currentlyUsedTrivia): #avoid duplicates
            temp = random.randint(0,len(allTrivia))
        currentlyUsedTrivia.insert(0,temp)
        
    currentlyUsedTrivia = currentlyUsedTrivia[:500]
    
    for i in range(total):
        command = "echo \"" + CleanTextForPiper(allTrivia[currentlyUsedTrivia[i]][0]) + "\" | .\\piper\\piper.exe -m .\\piper\\voices\\en_US-ryan-medium.onnx -f piper\\game_data\\TriviaRacetrack\\trivia-" + str(i) + ".wav --noise_w 1.2 -q"

        # Use subprocess.run() without check=True to wait for the command to complete
        if (currentlyGeneratingTTS):
            #this is how we abort the thread
            subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if (i == 0):
                print("question 1 generated")        
    if (currentlyGeneratingTTS):
        print("all audio generated")
    currentlyGeneratingTTS = False
    
    #threaded
def GenerateLoserPlayerCallout(name):
    message = random.choice(loserCallouts)
    command = "echo \"" + CleanTextForPiper(message.replace("{0}",name)) + "\" | .\\piper\\piper.exe -m .\\piper\\voices\\en_US-ryan-medium.onnx -f piper\\game_data\\TriviaRacetrack\\trivia-callout-" + name.replace(":","") + ".wav --noise_w 1.0 -q"
    subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
    
def CleanTextForPiper(string):
    #accents don't appear in powershell. didn't feel like figuring out if it worked from python
    string = string.replace("é","e").replace("ó","o").replace("ô","o").replace("ø","o").replace("ú","u").replace("û","u").replace("ć","c")
    #quotes kill the echo command
    string = string.replace("\'","").replace("\"","").replace("‘","").replace("’","").replace("“","").replace("”","").replace("\r"," ").replace("\n"," ").replace(":"," ")
    return string.strip()


if __name__ == '__main__':
    if not os.path.exists("piper/game_data/TriviaRacetrack/"):
        os.makedirs("piper/game_data/TriviaRacetrack/")
    
    
    # auto collect IP of machine and update secret.js
    if (address.lower() == "x.x.x.x"):
        ip_address = socketLibrary.gethostbyname(socketLibrary.gethostname())
        address = ip_address
    
    #update secret data from /templates/js/
    if not os.path.exists("static/js/"):
        os.makedirs("static/js/")
    secretfile=open("static/js/secret.js","w")
    secretfile.write('address = "' + address + '";port = "' + str(port) + '";')
    secretfile.close()
    
    
    #read in all Trivia
    LoadTriviaQuestions()
    
    #load loser callouts
    with open('game_data/TriviaRacetrack/narrator messages.csv', 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            # 'row' is a list containing the values in each row
            if ("losercallout-" in row[0]):
                loserCallouts.append(row[1])



    try:
        print("Server for [" + SERVER_TYPE + "]")
        if (maskIpAddress):
            print("Server Started at X.X.X.X:" + str(port))
        else:
            print("Server Started at " + address + ":" + str(port))
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
    
        server = pywsgi.WSGIServer((address, port), app, handler_class=WebSocketHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        stop_threads = True
#        color_thread.join()
        