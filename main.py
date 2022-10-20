import tkinter as tk
from tkinter import ttk
import pandas as pd
from Spoti_client import SpotifyAPI

CLIENT_ID = '3e263c6365414d75ada53c7cccbe623f'
CLIENT_SECRET = '68ea48bf8bec48d7b4bdf809e74e0f61'
client = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)
root = tk.Tk()
root.geometry("900x900")
root.title('Song Table')

f1 = tk.Frame(root, pady=25)
f1.pack()
f2 = tk.Frame(root, pady=25, padx=25)
f2.pack(expand=True, fill='y')

tv = ttk.Treeview(f2, columns=('1','2','3','4'), show='headings', height=5)
tv.pack(expand=True, fill='y')
tv.heading(1, text='Song')
tv.heading(2, text='Album')
tv.heading(3, text='Artist')
tv.heading(4, text='Artist id')
# para extender el frame 2 verticalmente hacia abajo
f2.grid_rowconfigure(1, weight=4)

def print_song_df(song):
    tv.delete(*tv.get_children())

    df = client.get_song_table({'track':song}, search_type='track')
    for i in df.values.tolist():
        tv.insert('', 'end', values=i)

text = tk.StringVar(root)
song_search = tk.Entry(f1, textvariable=text)
song_search.grid(row=0, column=0)
get_df_button = tk.Button(f1, text='Get song table', command=lambda: print_song_df(song_search.get()), state='disabled')
get_df_button.grid(row=0, column=1)

def upd(*args):
    if len(text.get()) == 0:
        get_df_button.config(state='disabled')
    else: get_df_button.config(state='normal')


text.trace('w', upd)
root.bind('<Return>', lambda x: print_song_df(song_search.get()))
root.mainloop()