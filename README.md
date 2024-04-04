# Initial Setup (New Computer)

A setup guide can be found at the end of [**this video.**](https://youtu.be/e804a0amv50) It’s not as difficult as it looks.
Screenshots can be found [**here**](https://distractedcoder.itch.io/custom-jackbox-game-trivia-racetrack).

1. Download **Anaconda** Python Distribution
    1. <https://www.anaconda.com/download>
    2. Install Anaconda with default settings
2. Open the Start Menu and search for **Anaconda Prompt**
3. In the terminal window, copy and paste the following command
    1. `pip install Flask==1.1.4 Flask-Sockets flask-socketio gevent greenlet markupsafe==2.0.1`
4. Download the Jack’s Box Project
    1. At the top of this page, there should be a green button that says **Code**▾
    2. Click that, then select **Download ZIP**
5. Extract the contents of the ZIP file and move the folder to your Desktop
    1. _You can put the folder wherever you want. Desktop is easiest_
6. Download the latest release of **Piper** (free text-to-speech engine)
    1. <https://github.com/rhasspy/piper/releases>
    2. Click the download option for **piper_windows_amd64.zip**
7. Extract the contents of the ZIP file to `{Project}\Jacks-Box-Project-main\Jacksbox-Python-Data`
    1. Folder should now include these folders: game_data, piper, static, templates
8. Open the new **piper folder** and create a new folder called: **voices**
    1. Folder should now include these folders: espeak-ng-data, pkgconfig, voices
9. Download Ryan’s voice
    1. <https://huggingface.co/rhasspy/piper-voices/tree/v1.0.0/en/en_US/ryan/medium>
    2. Download both **en_US-ryan-medium.onnx** and **en_US-ryan-medium.onnx.json**
        1. Make sure the .json file is renamed to **en_US-ryan-medium.onnx.json**
    3. Move both files into the **piper/voices** folder created earlier

# Changing Settings

If you happen to be streaming this game, **it is very important to hide your IP Address**.

1. Navigate to `{Project}\Jacks-Box-Project-main\Jackbox-Game-Data\Jackbox Game_Data\StreamingAssets`
2. Open **Settings.json** (these settings are universal for server and game data)
    1. **Server Settings:**
        1. If the game fails to automatically identify your IP address, tweak these lines:
            1. `"Address": "x.x.x.x",`
                1. _Type: string_
            2. `"Port": 80,`
                1. _Type: integer_
        2. If you need to mask your IP address in game, tweak this line:
            1. `"DontDisplayIpAddress": false,`
                1. _Type: boolean true or false_
    2. **Trivia Racetrack Settings:**
        1. `"TotalQuestions"`: Total trivia questions
        2. `"QuestionsBeforeLoserBonus"`: How many questions before the last place player is given a boost
        3. `"ShowScoresEveryXQuestions"`: How frequently to show the score table

# Running the Game

1. Open the Start Menu and search for **Spyder** (Spyder looks very complicated but you don’t need to understand anything about the program)
    1. From Spyder Editor, open `{Project}\Jacks-Box-Project-main\Jacksbox-Python-Data\server-TriviaRacetrack.py`
    2. Click the green run script button at the top of Spyder
        1. If you get a popup, just click Ok or Run
        2. Bottom left corner of Spyder should confirm that the server started
    3. Minimize the server but keep it running
        1. If Sypder ever asks about updating, skip the update and disable automatic update checking
2. Start the game located at `{Project}\Jacks-Box-Project-main\Jackbox-Game-Data\Jackbox Game.exe`
3. Play the game! The game will display the link to connect to on the phones (unless hidden).

# Known Issues/Details

1. Everyone must be on the same WiFi network, including the computer hosting the server/game. Keep in mind that if your router broadcasts both a 4G and 5G connection, those are considered separate networks.
2. This is a local server only. There is no access available from the internet.
3. If the announcer fails to read a question, there is a 15 second failsafe in place. This is rare but will not result in the game crashing.
4. Make sure you keep the browser window open the entire time on your phone. Leaving the game in the background may result in missing a question or desyncing.
5. If you are skipped for a question, sorry but you should get the next question once it is ready.
6. The game will very rarely crash, if this happens, there is a button in the bottom right to skip to the results screen.
    **1. If the server crashes, you must close the server and restart. You do not have to close the game, simply back out to the title screen.**


*Disclaimer: This is not a hack or mod of any Party Pack created by Jackbox Games. All code is original.*
