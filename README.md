# Playing Doom using Phone Call
In this repositry we are implementing few game mechanism using phone dial. I have ran the classic Doom and also made one guessing game. I have used SIM800L for call functionality, and also have stored all the audio .amr files in the available storage in SIM800L. For more info on how to upload/delete files in SIM800L please go through my explanation by clicking on this [link](https://github.com/Jitendra300/SIM800L_internal_memory_guide). I have also used USB-TTL to communicate to SIM800L from my laptop.

# In-Depth Explanation
Through this [blog](https://github.com/martinhol221/SIM800L_DTMF_control/wiki/Loading-ARM-audio-files-in-the-SIM800L-modem) I got to know that the maximum storage available in SIM800L is 40kb. Thus I have made sure that all my .amr files have less quality and thus less size, due to this I often have to put the call on speaker to hear the audio files clearly. The files are uploaded by the process which is extensively covered in this [repo](https://github.com/Jitendra300/SIM800L_internal_memory_guide). 

The files which I have uploaded in SIM800L all belong to guessing game as it needed some audio response when some action is taken by the user. The files in SIM800L are: <br>
- wrong_guess_lq.amr
- correct_guess_lq.amr
- intro_lq.amr

Here lq at the suffix means **low-quality**. And yea you can also see the respective mp3 also in the sounds directory. I have used ffmpeg tool to convert mp3 files to amr files.

In short the circuit diagram I have used is: 
<br><br>
![Circuit Diagram for playing games using phone dial](/images/circuit_diagram.png "Circuit Diagram")
<br><br>

And this is how my breadboard circuit looks like: 
<br><br>
![Breadboard Circuit](/images/breadboard_circuit.jpg "Breadboard Circuit")
<br><br>

Here is a demo of playing doom :<br>
![ Watch Doom Demo](videos/doom_demo.gif)
<br><br>

And here is me playing guessing game:<br>
![Watch Guessing Game Demo](videos/guessing_game_demo.gif)
<br><br>
**Note: ** To view with audio just download and view the guessing_game_demo.mp4 from /videos directory.
# Installation & Running

```
git clone ""
cd ""
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
For Doom:
Before running this we need to make sure to run doom game and switch to its window!

```
sudo -E $(which python) controller.py
```
For Guessing Game:
```
python guessing_game.py
```
# Challenges
- One of the biggest challenges working with SIM800L is that it uses 2G networks thus it can be huge bottleneck for most of us there! I myself had hard time cause I had to switch to places where there would be 2G towers
- The SIM provider should allow 2G networks
- SIM800L needs 2A at max for calling someone.

# Inspiration
- Somewhere in Hackernews I had seen people using telephone dial to play doom.
- I had also seen someone using similar concept of phone dial to play things but they hadn't used one IoT device! 
