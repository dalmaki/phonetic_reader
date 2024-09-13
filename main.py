import os
from pydub import AudioSegment
from pydub.playback import play
import asyncio
import threading

import tkinter as tk
from tkinter import filedialog as fd

from async_tkinter_loop import async_handler, async_mainloop

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

def fetch_audio_files(directory):

    # Combine the script directory with the audio directory
    audio_dir = os.path.join(script_dir, directory)

    # List to store audio file names
    audio_files = []

    # Scan the directory for MP3 files
    for file_name in os.listdir(audio_dir):
        if file_name.endswith('.mp3'):
            file_path = os.path.join(audio_dir, file_name)
            audio_files.append([file_path, file_name])

    return audio_files

# Fetch audio files from the 'sound' directory
audio_files = fetch_audio_files('sound')
audio_file_dict = dict()
audio_dict = dict()

# Print the list of file names as a checkpoint
print("Audio files found:")
for [audio_file, audio_file_name] in audio_files:
    print(f"- {audio_file}")
    audio_file_name = audio_file_name[:-4]
    audio_file_dict[audio_file_name] = audio_file

    audio = AudioSegment.from_file(audio_file)
    audio_dict[audio_file_name] = audio

def set_playback_speed(speed):
    for [audio_file, audio_file_name] in audio_files:
        audio_file_name = audio_file_name[:-4]
        audio_file_dict[audio_file_name] = audio_file

        audio = AudioSegment.from_file(audio_file)
        audio_dict[audio_file_name] = speed == 1 and audio or audio.speedup(speed, 150, 25)

# GUI Initialization -----------------------------------------------------------

print("\nProceeding to GUI initialization")

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master, padx=10, pady=10)
        self.pack()

        self.file_path = tk.StringVar()

        self.label = tk.Label(self, text="Phonetic Reader")
        self.label.pack()



        self.file_frame = tk.Frame(self)
        self.file_frame.pack(pady=5)

        self.choose_file_button = tk.Button(self.file_frame, text="Choose File", command=self.choose_file)
        self.choose_file_button.grid(row=1, column=0, padx=5)

        self.file_path_entry = tk.Entry(self.file_frame, textvariable=self.file_path, width=50, state='readonly')
        self.file_path_entry.grid(row=1, column=1)



        self.playback_frame = tk.Frame(self)
        self.playback_frame.pack(pady=5, fill='x')

        self.play_button = tk.Button(self.playback_frame, text="Play", command=async_handler(self.play))
        self.play_button.grid(row=1, column=0, padx=5)

        self.stop_button = tk.Button(self.playback_frame, text="Stop", command=async_handler(self.stop))
        self.stop_button.grid(row=1, column=1, padx=5)
        
        self.stop_button = tk.Button(self.playback_frame, text="Pause", command=async_handler(self.pause))
        self.stop_button.grid(row=1, column=2, padx=10)

        self.playback_speed = tk.DoubleVar()
        self.playback_speed.set(1.0)

        self.speed_label = tk.Label(self.playback_frame, text="Speed:")
        self.speed_label.grid(row=1, column=3, padx=5)

        self.speed_entry = tk.Entry(self.playback_frame, textvariable=self.playback_speed, width=5)
        self.speed_entry.grid(row=1, column=4, padx=5)

        self.speed_button = tk.Button(self.playback_frame, text="Set", command=lambda: set_playback_speed(self.playback_speed.get()))
        self.speed_button.grid(row=1, column=5, padx=10)

        self.go_left_button = tk.Button(self.playback_frame, text="<<", command=self.go_left)
        self.go_left_button.grid(row=1, column=6, padx=5)

        self.position = tk.IntVar()

        self.position_entry = tk.Entry(self.playback_frame, textvariable=self.position, width=5, state='readonly')
        self.position_entry.grid(row=1, column=7, padx=5)

        self.go_right_button = tk.Button(self.playback_frame, text=">>", command=self.go_right)
        self.go_right_button.grid(row=1, column=8, padx=5)

        
        self.content = tk.Text(self, height=10, width=50)
        self.content.pack(pady=5)


        self.status_text = tk.StringVar()
        self.status_text.set("Ready")

        self.status_label = tk.Label(self, textvariable=self.status_text)
        self.status_label.pack()



        self.should_stop = False
        self.should_pause = False
        self.is_playing = False

        self.file_content = None

    def choose_file(self):
        file_types = (
            ('Text files', '*.txt'),
            ('All files', '*.*')
        )

        example_dir = os.path.join(script_dir, 'example')

        file_path = fd.askopenfilename(
            title='Open a text file to read',
            initialdir=example_dir,
            filetypes=file_types
        )

        self.file_path.set(file_path)
        
        f = open(file_path, 'r')
        self.file_content = f.read()
        f.close()

    async def play(self):
        if self.should_pause:
            self.should_pause = False
            return
        
        if self.should_stop:
            self.should_stop = False
            return
        
        if self.is_playing:
            return 

        self.is_playing = True

        self.position.set(0)

        file_path = self.file_path.get()
        if not file_path:
            self.status_text.set("No file chosen")
            return

        if not os.path.exists(file_path):
            self.status_text.set("File does not exist")
            return
        
        # Clear content
        self.content.replace('1.0', 'end', "")
        
        self.status_text.set("3")
        await asyncio.sleep(1.0)
        self.status_text.set("2")
        await asyncio.sleep(1.0)
        self.status_text.set("1")
        await asyncio.sleep(1.0)
        
        self.status_text.set("Playing")

        content = self.file_content

        i = 0
        while i + 1 < len(content):
            if self.should_stop:
                self.should_stop = False
                break

            if self.should_pause:
                while self.should_pause:
                    await asyncio.sleep(0.1)

                self.status_text.set("3")
                await asyncio.sleep(1.0)
                self.status_text.set("2")
                await asyncio.sleep(1.0)
                self.status_text.set("1")
                await asyncio.sleep(1.0)

            i = self.position.get()
            self.position.set(i + 1)

            char = content[i]


            self.content.insert('end', char)

            if char.isalnum():
                audio = audio_dict[char.upper()]
                threading.Thread(target=play, args=(audio,)).start()

                await asyncio.sleep(1.0 / self.playback_speed.get())
            elif char == ',' or char == '.' and i + 1 < len(content) and content[i + 1].isalnum():
                audio = audio_dict['_Decimal']
                threading.Thread(target=play, args=(audio,)).start()

                await asyncio.sleep(1.0 / self.playback_speed.get())
            elif char == '.':
                audio = audio_dict['_Stop']
                threading.Thread(target=play, args=(audio,)).start()

                await asyncio.sleep(1.0 / self.playback_speed.get())
            elif char == ' ':
                await asyncio.sleep(0.5 / self.playback_speed.get())
        
        await asyncio.sleep(1.0 / self.playback_speed.get())
        audio = audio_dict['_Out']
        threading.Thread(target=play, args=(audio,)).start()
        
        self.is_playing = False

        self.status_text.set("Finished playing")


    async def stop(self):
        self.should_pause = False
        self.should_stop = True
        self.status_text.set("Stopped")

    async def pause(self):
        self.should_stop = False
        self.should_pause = True
        self.status_text.set("Paused")

    def go_left(self):
        if self.position.get() == 0:
            return
        i = self.position.get()
        self.position.set(i - 1)

        self.content.delete('end-2c', 'end')

    def go_right(self):
        if self.position.get() == len(self.file_content):
            return
        i = self.position.get()
        self.position.set(i + 1)

        self.content.insert('end', self.file_content[i])


root = tk.Tk()
myapp = App(root)
myapp.master.title("Phonetic Reader")
async_mainloop(root)