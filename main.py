import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import os
import platform
import glob
import pygame as pg
import random
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.m4a import M4A
from mutagen.flac import FLAC
from mutagen.wave import WAVE
from mutagen.aac import AAC


global playing, paused, starting_second, is_favorite, repeat, song_length
playing = False
paused = False
starting_second = 0
is_favorite = False
repeat = False
song_length = 0


playlist = {}
playlist_favorite = {}
song_formats = (("MP3 Files", "*.mp3"), ("M4A Files", "*.m4a"), ("FLAC Files", "*.flac"),
                ("MP4 Files", "*.mp4"), ("WAV Files", "*.wav"), ("AAC Files", "*.aac"))
os_ = platform.system()
username = os.getlogin()
if os_ == "Windows":
  computermusic_dir = "c:\\users\\" + username + "\\music"
elif os_ == "Linux":
  computermusic_dir = "/home/" + username + "/Music"
else:
  exit(0)

class Scale(ttk.Scale):
    """a type of Scale where the left click is hijacked to work like a right click"""

    def __init__(self, master=None, **kwargs):
        ttk.Scale.__init__(self, master, **kwargs)
        self.bind('<Button-1>', self.set_value)

    def set_value(self, event):
        self.event_generate('<Button-3>', x=event.x, y=event.y)
        return 'break'


# stripping the directory and format of the song
def strip_song(song):

    # check if the directory ends with / or \
    if song.rfind("/") == -1:
        slash = "\\"
    else:
        slash = "/"

    song_dir = song[: song.rfind(slash) + 1]
    song_format = song[song.rfind("."):]
    song_name = song[song.rfind(slash) + 1: song.rfind(".")]

    return (song_dir, song_name, song_format)


# finding and adding all the songs in computer music folder
def find_song(song_box):
    computermusic_songs = []
    for song_format in song_formats:
        if os_ == "Windows":
            files = glob.glob(computermusic_dir + "\\**\\" +
                            song_format[1], recursive=True)
        else:
            files = glob.glob(computermusic_dir + "/**/" + song_format[1], recursive=True)
        computermusic_songs += files

    for song in computermusic_songs:
        song_dir, song_name, song_format = strip_song(song)
        playlist[song_name] = [song_dir, song_format, False]
        song_box.insert(tk.END, song_name)


# adding song(s) (from the menu)
def add_song():
    songs = filedialog.askopenfilenames(
        initialdir=computermusic_dir, filetypes=song_formats)
    for song in songs:
        song_dir, song_name, song_format = strip_song(song)
        if not song_name in playlist:
            playlist[song_name] = [song_dir, song_format, False]
            songbox_playlist.insert(tk.END, song_name)


# calculating song duration in hours, minutes and seconds
def song_duration(length):
    hours = length // 3600
    length %= 3600
    mins = length // 60
    length %= 60
    seconds = length

    return hours, mins, seconds


# updating label on song position
def play_time(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin):
    global playing, paused, starting_second, repeat, song_length

    current_time = int(starting_second + pg.mixer.music.get_pos() / 1000)

    if current_time >= song_length:
        pg.mixer.music.stop()

    cur_hour, cur_min, cur_sec = song_duration(current_time)
    song_time_str.config(text=f"{cur_hour} : {cur_min} : {cur_sec}")

    len_hour, len_min, len_sec = song_duration(song_length)
    song_time_fin.config(text=f"{len_hour} : {len_min} : {len_sec}")

    song_slider.config(value=current_time)
    song_slider.config(to=song_length)

    if pg.mixer.music.get_busy() or paused:
        song_time_str.after(500, lambda: play_time(
            song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin))
    else:
        playing = False
        paused = False
        starting_second = 0
        if repeat:
            play(song_box, btn_play, btn_heart,
                 song_slider, song_time_str, song_time_fin)
        else:
            btn_play["image"] = img_btn_play
            song_time_fin.config(text="0 : 0 : 0")


# playing song
def play(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin, selected=False):
    global playing, paused, repeat, starting_second, song_length

    if song_box.size() != 0:
        if selected:
            try:
                song_name = song_box.get(song_box.curselection()[0])
                playing = False
                paused = False
                starting_second = 0
            except:
                return
        else:
            song_name = song_box.get(tk.ACTIVE)
        song_dir = playlist[song_name][0]
        song_format = playlist[song_name][1]
        song = song_dir + song_name + song_format

        song_format = song_format.lower()
        # song duration
        if song_format == ".mp3":
            songinfo = MP3(song)
        elif song_format == ".m4a":
            songinfo = M4A(song)
        elif song_format == ".flac":
            songinfo = FLAC(song)
        elif song_format == ".mp4":
            songinfo = MP4(song)
        elif song_format == ".wav":
            songinfo = WAVE(song)
        elif song_format == ".aac":
            songinfo = AAC(song)
        else:
            messagebox.showerror(
                title="Error!", message="Something went wrong..Please choose another song!")
            return

        song_length = int(songinfo.info.length)
        if repeat and starting_second > song_length:
            starting_second = 0

        if not playing and not paused:
            try:
                playing = True
                pg.mixer.music.load(song)
                if repeat:
                    pg.mixer.music.play(loops=-1, start=starting_second)
                else:
                    pg.mixer.music.play(loops=1, start=starting_second)
                btn_play["image"] = img_btn_pause

                for song in playlist:
                    if song == song_name:
                        if playlist[song][2]:
                            btn_heart["image"] = img_btn_heart_solid
                        else:
                            btn_heart["image"] = img_btn_heart_outline
            except:
                pass
        elif playing and not paused:
            paused = True
            pg.mixer.music.pause()
            btn_play["image"] = img_btn_play
        elif playing and paused:
            paused = False
            pg.mixer.music.unpause()
            btn_play["image"] = img_btn_pause

        if pg.mixer.music.get_busy() or paused:
            playing = True
        else:
            playing = False

        play_time(song_box, btn_play, btn_heart,
                  song_slider, song_time_str, song_time_fin)


# selecting the next song to play
def next(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin):
    global playing, paused, starting_second

    try:
        if song_box.size() != 0:
            next_song_index = song_box.curselection()[0] + 1
            song_box.selection_clear(0, tk.END)
            if next_song_index < song_box.size():
                song_box.activate(next_song_index)
                song_box.select_set(next_song_index, last=None)
            else:
                song_box.activate(0)
                song_box.select_set(0, last=None)

            playing = False
            paused = False
            starting_second = 0
            play(song_box, btn_play, btn_heart,
                 song_slider, song_time_str, song_time_fin)
    except:
        pass


# selecting the previous song to play
def previous(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin):
    global playing, paused, starting_second

    try:
        if song_box.size() != 0:
            prev_song_index = song_box.curselection()[0] - 1
            song_box.selection_clear(0, tk.END)
            if prev_song_index >= 0:
                song_box.activate(prev_song_index)
                song_box.select_set(prev_song_index, last=None)
            else:
                song_box.activate(song_box.size() - 1)
                song_box.select_set(song_box.size() - 1, last=None)

            playing = False
            paused = False
            starting_second = 0
            play(song_box, btn_play, btn_heart,
                 song_slider, song_time_str, song_time_fin)
    except:
        pass


# skipping forward the song (10 seconds)
def skip_forward(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin):
    global playing, paused, starting_second, repeat, song_length

    if pg.mixer.music.get_busy() or paused:
        current_second = int(
            starting_second + (pg.mixer.music.get_pos() / 1000))
        starting_second = current_second + 10
        if starting_second >= song_length and not repeat:
            starting_second = song_length
        elif starting_second >= song_length and repeat:
            starting_second = 0

        playing = False
        paused = False
        play(song_box, btn_play, btn_heart,
             song_slider, song_time_str, song_time_fin)
    else:
        starting_second = 0


# skipping backward the song (10 seconds)
def skip_backward(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin):
    global playing, paused, starting_second

    current_second = int(starting_second - (pg.mixer.music.get_pos() / 1000))
    starting_second = current_second - 10
    if starting_second < 0:
        starting_second = 0

    playing = False
    paused = False
    play(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin)


# choosing to add or remove to favortie song playlist
def add_to_favorites(song_box, btn_heart, song_slider, song_time_str, song_time_fin):
    global playing, paused, starting_second

    song_name = song_box.get(tk.ACTIVE)
    is_favorite = False
    for song in playlist:
        if song == song_name:
            is_favorite = playlist[song_name][2]

    # changing heart image
    song_name = song_box.get(tk.ACTIVE)
    if not is_favorite:
        try:
            song_dir = playlist[song_name][0]
            song_format = playlist[song_name][1]
            playlist_favorite[song_name] = (song_dir, song_format)
            songbox_favorites.insert(tk.END, song_name)
            playlist[song_name][2] = True
            btn_heart["image"] = img_btn_heart_solid
        except:
            pass
    else:
        playlist[song_name][2] = False
        btn_heart["image"] = img_btn_heart_outline
        playlist_favorite.pop(song_name, None)
        li = songbox_favorites.get(0, last=tk.END)
        songbox_favorites.delete(li.index(song_name))

        if song_box == songbox_favorites:
            playing = False
            paused = False
            starting_second = 0
            song_slider.config(value=0)
            song_time_str.config(text="0 : 0 : 0")
            song_time_fin.config(text="0 : 0 : 0")
            pg.mixer.music.stop()


# choosing a random song to play
def shuffle(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin):
    global playing, paused, starting_second

    if song_box.size() != 0:
        rand_song_index = random.randint(0, song_box.size() - 1)
        song_box.selection_clear(0, tk.END)
        song_box.activate(rand_song_index)
        song_box.select_set(rand_song_index, last=None)

        playing = False
        paused = False
        starting_second = 0
        play(song_box, btn_play, btn_heart,
             song_slider, song_time_str, song_time_fin)


# choosing to play song repeatedly or not
def repeat_song(btn_repeat, song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin):
    global playing, paused, starting_second, repeat

    repeat = not repeat
    if repeat:
        btn_repeat["image"] = img_btn_repeat
    else:
        btn_repeat["image"] = img_btn_norepeat

    playing = False
    paused = False
    starting_second = 0
    play(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin)


# playing the song on the slider position
def slide(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin):
    global playing, paused, starting_second

    starting_second = song_slider["value"]
    playing = False
    paused = False
    play(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin)


# initializing tkinter
root = tk.Tk()
WIDTH, HEIGHT = 620, 500
root.title("Music Player")
root.geometry(f"{WIDTH}x{HEIGHT}")

# initializing pygame
pg.init()
pg.mixer.init()

# loading images
img_btn_play = tk.PhotoImage(file="img_play.png")
img_btn_pause = tk.PhotoImage(file="img_pause.png")
img_btn_next = tk.PhotoImage(file="img_next.png")
img_btn_previous = tk.PhotoImage(file="img_previous.png")
img_btn_skip_forward = tk.PhotoImage(file="img_skip_forward.png")
img_btn_skip_backward = tk.PhotoImage(file="img_skip_backward.png")
img_btn_heart_solid = tk.PhotoImage(file="img_heart_solid.png")
img_btn_heart_outline = tk.PhotoImage(file="img_heart_outline.png")
img_btn_shuffle = tk.PhotoImage(file="img_shuffle.png")
img_btn_repeat = tk.PhotoImage(file="img_repeat.png")
img_btn_norepeat = tk.PhotoImage(file="img_norepeat.png")

# tabs
tab_control = ttk.Notebook(root)
tab_playlist = ttk.Frame(tab_control)
tab_favorites = ttk.Frame(tab_control)
tab_control.add(tab_playlist, text="Playlist")
tab_control.add(tab_favorites, text="Favorites")
tab_control.pack(expand=1, fill="both")

# creating a song box for all songs
fnt_songname = ("Arival", 12, "bold")
songbox_playlist = tk.Listbox(tab_playlist, width=WIDTH, height=15,
                              font=fnt_songname, bg="lightgray", fg="black", selectbackground="darkblue")
songbox_playlist.pack()

# creating a song box for favorite songs
songbox_favorites = tk.Listbox(tab_favorites, width=WIDTH, height=15,
                               font=fnt_songname, bg="lightgray", fg="black", selectbackground="darkblue")
songbox_favorites.pack()


def fill_tab(tab, song_box):

    # creating a frame for buttons
    frame_controls = tk.Frame(tab, bg="lightblue")
    frame_controls.pack(pady=5)

    # creating a frame for slider
    frame_slider = tk.Frame(tab)
    frame_slider.pack(pady=15)

    # creating buttons
    btn_play = tk.Button(
        frame_controls, borderwidth=0, image=img_btn_play, command=lambda: play(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin))
    btn_next = tk.Button(
        frame_controls, borderwidth=0, image=img_btn_next, command=lambda: next(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin))
    btn_previous = tk.Button(
        frame_controls, borderwidth=0, image=img_btn_previous, command=lambda: previous(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin))
    btn_skip_forward = tk.Button(
        frame_controls, borderwidth=0, image=img_btn_skip_forward, command=lambda: skip_forward(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin))
    btn_skip_backward = tk.Button(
        frame_controls, borderwidth=0, image=img_btn_skip_backward, command=lambda: skip_backward(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin))
    btn_heart = tk.Button(
        frame_controls, borderwidth=0, image=img_btn_heart_outline, command=lambda: add_to_favorites(song_box, btn_heart, song_slider, song_time_str, song_time_fin))
    btn_shuffle = tk.Button(
        frame_controls, borderwidth=0, image=img_btn_shuffle, command=lambda: shuffle(song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin))
    btn_repeat = tk.Button(
        frame_controls, borderwidth=0, image=img_btn_norepeat, command=lambda: repeat_song(btn_repeat, song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin))

    # creating labels for current song position and the song length
    fnt_song_time = ("Arival", 10, "bold")
    song_time_str = tk.Label(
        frame_slider, text="", relief=tk.GROOVE, width=10, font=fnt_song_time)
    song_time_fin = tk.Label(
        frame_slider, text="", relief=tk.GROOVE, width=10, font=fnt_song_time)

    # song slider
    song_slider = Scale(frame_slider, orient=tk.HORIZONTAL, from_=0, to=100, length=360, value=0, command=lambda x: slide(
        song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin))

    song_time_str.grid(row=0, column=0, padx=10)
    song_slider.grid(row=0, column=1, padx=10)
    song_time_fin.grid(row=0, column=2, padx=10)

    # playing the song selected in song box
    song_box.bind("<<ListboxSelect>>", lambda x: play(
        song_box, btn_play, btn_heart, song_slider, song_time_str, song_time_fin, True))

    # setting buttons on the frame controls
    btn_shuffle.grid(row=0, column=0, padx=3, pady=20)
    btn_skip_backward.grid(row=0, column=1, padx=3)
    btn_previous.grid(row=0, column=2, padx=3)
    btn_play.grid(row=0, column=3, padx=3)
    btn_next.grid(row=0, column=4, padx=3)
    btn_skip_forward.grid(row=0, column=5, padx=3)
    btn_heart.grid(row=0, column=6, padx=3)
    btn_repeat.grid(row=0, column=7, padx=3)

    # menu
    menu_main = tk.Menu(root)
    root.config(menu=menu_main)
    menu_add = tk.Menu(menu_main, tearoff=0)
    menu_main.add_cascade(label="Add", menu=menu_add)
    menu_add.add_command(label="Add song to playlist",
                         command=add_song)

    if tab == tab_playlist:
        find_song(song_box)


fill_tab(tab_playlist, songbox_playlist)
fill_tab(tab_favorites, songbox_favorites)


# setting tkinter mainloop
root.mainloop()
