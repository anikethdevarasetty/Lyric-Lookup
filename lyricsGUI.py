import tkinter
import requests
from PIL import Image, ImageTk
from urllib.request import urlopen, Request
from io import BytesIO
from bs4 import BeautifulSoup
from tkinter.scrolledtext import ScrolledText
import webbrowser
import pickle


root = tkinter.Tk()
root.title("Lyric Lookup")

buttons = []

#methods
def setSearchTerm(term):
    term = search.get()
    root.geometry('340x500')
    for widget in mainFrame.winfo_children():
        if not isinstance(widget, tkinter.Entry):
            widget.destroy()
    if term == "//saved" :
        getSaved()
    else :
        getInfo(term)

def getSaved():
    bar = tkinter.Scrollbar(mainFrame, orient='vertical')
    bar.pack(side = tkinter.RIGHT, fill = tkinter.Y)
    for song in songList :
        l = tkinter.Button(mainFrame, width = 300, text = song['result']['full_title'], command = lambda song=song: selectedSong(song))
        l.pack()

def getInfo(term):
    # apiObj = geniusAPIabstracted.API()
    # apiObj.setQuery(term)
    # response = apiObj.getResponse()

    # for button in buttons: 
    #     button.destroy()
    authenticator = "x_CF3VynuaQGF8gtouHsnKfCdxi53mpbm8l9Shw5eb26VJHqCtA8VqFraMVHFyid"
    query = term
    searchURL = f"http://api.genius.com/search?q={query}&access_token={authenticator}"
    response = requests.get(searchURL)
    jsonResponse = response.json()
    i = 0
    for song in jsonResponse['response']['hits']:
        try:
            l = tkinter.Button(mainFrame, width = 300, text = song['result']['full_title'], command = lambda song=song: selectedSong(song))
            buttons.append(l)
            l.pack()
            i = i + 1
        except:
            continue #need to figure out later

def openYT(url):
    webbrowser.open(url)

def saveSong(song):
    songList.append(song)
    pickle.dump(songList,open("C:\My Stuff\STEM\Programming\Python\lyrics\songList.dat","wb" ))

def selectedSong(song):
    print(song['result']['full_title'])
    for widget in mainFrame.winfo_children():
        if not isinstance(widget, tkinter.Entry):
            widget.destroy()
    songName = tkinter.Label(mainFrame, text = song['result']['title'])
    songName.pack()
    artist = tkinter.Label(mainFrame, text = song['result']['artist_names'])
    artist.pack()
    songid = song['result']['api_path']
    authenticator = "x_CF3VynuaQGF8gtouHsnKfCdxi53mpbm8l9Shw5eb26VJHqCtA8VqFraMVHFyid"
    url = f"http://api.genius.com{songid}?access_token={authenticator}"
    response = requests.get(url)
    jsonResponse = response.json()
    try:
        album = "From " + jsonResponse['response']['song']['album']['name']
        albumlabel = tkinter.Label(mainFrame, text = album)
        albumlabel.pack()
    except:
        print("no album name")
    releaseDate = "Released on " + jsonResponse['response']['song']['release_date_for_display']
    dateLabel = tkinter.Label(mainFrame, text = releaseDate)
    dateLabel.pack()


    coverArtUrl = song['result']['song_art_image_thumbnail_url']
    req = Request(coverArtUrl, headers={'User-Agent': 'Mozilla/5.0'})
    u = urlopen(req)
    raw_data = u.read()
    u.close()

    photo = ImageTk.PhotoImage(data = raw_data)

    cover = tkinter.Label(mainFrame,    image=photo)
    cover.image = photo
    cover.pack()

    #song lyrics
    openLyrics = tkinter.Button(mainFrame, text = "Get Full Lyrics", command = lambda song=song: getLyrics(song))
    openLyrics.pack()

    #youtube link
    media = jsonResponse['response']['song']['media']
    songurl = ""
    for tsong in media:
        if tsong['provider'] == "youtube":
            songurl = tsong['url']
    songButton = tkinter.Button(mainFrame, text = "Open in YouTube", command = lambda url=songurl : openYT(songurl))
    songButton.pack()

    saveButton = tkinter.Button(mainFrame, text = "Save Song", command = lambda song=song : saveSong(song))
    saveButton.pack()

def getLyrics(song):
    # for widget in mainFrame.winfo_children():
    #     widget.destroy()
    lyricsWindow = tkinter.Toplevel(root)
    lyricsWindow.title(song['result']['full_title'])

    url = song['result']['url']
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    # parsed = soup.find_all("div", class_ = "lyrics")
    # for things in parsed:
    #     songLyrics = parsed.find("p")
    #     print(songLyrics.text)

    lyrics = ""
    for tag in soup.select('div[class^="Lyrics__Container"], .song_body-lyrics p'):
        t = tag.get_text(strip=True, separator='\n')
        if t:
            #print(t)
            lyrics += t
            #lyrics += "\n\n"

    lyricsText = ScrolledText(lyricsWindow, width=40, height=30, wrap=tkinter.WORD)
    lyricsText.pack(expand=True, fill=tkinter.BOTH) # pack it in the entire window
    lyricsText.insert(1.0, lyrics)

    lyricsWindow.mainloop()
    

#GUI Widgets
mainFrame = tkinter.Frame(root)
mainFrame.pack()

search = tkinter.Entry(mainFrame, width = 50)
search.bind('<Return>', setSearchTerm)
search.pack()

try:
    songList = pickle.load(open("C:\My Stuff\STEM\Programming\Python\lyrics\songList.dat", "rb"))
except:
    songList = []

root.mainloop()
