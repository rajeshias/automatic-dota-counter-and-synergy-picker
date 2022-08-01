import json
from pprint import pprint
import numpy
import pandas
from pygetwindow import PyGetWindowException
from config import name, rank, suggestions
from PIL import ImageFilter, ImageEnhance
import pygetwindow
import time
import pytesseract
import pyautogui
import PIL
import cv2
import glob
import imagehash
from tkinter import ttk
import tkinter as tk

result = {}

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

x, y = pyautogui.size()

x2, y2 = pyautogui.size()
x2, y2 = int(str(x2)), int(str(y2))

top = tk.Tk()

listbox = tk.Listbox(top, height=10,
                     width=15,
                     bg="grey",
                     activestyle='dotbox',
                     font="Helvetica",
                     fg="black")

top.geometry("300x250")

label = tk.Label(top, text="Best Picks:")


while True:
    time.sleep(.6)
    # find new window title
    # z1 = pygetwindow.getAllTitles()
    # # test with pictures folder
    # time.sleep(0.4)
    # z2 = pygetwindow.getAllTitles()
    # z3 = [x for x in z2 if x not in z1]
    # z3 = ''.join(z3)
    # # also able to edit z3 to specified window-title string like: "Sublime Text (UNREGISTERED)"
    # my = pygetwindow.getWindowsWithTitle(z3)[0]
    # # quarter of screen screensize
    # x3 = x2
    # y3 = y2
    # my.resizeTo(x3, y3)
    # # top-left
    # my.moveTo(0, 0)
    # time.sleep(0.6)
    # try:
    #     my.activate()
    # # implementation
    # except PyGetWindowException:
    #     pass
    # # handle exception

    # # save screenshot
    p = pyautogui.screenshot()
    p.save("dota.png")

    # edit screenshot
    im = PIL.Image.open("dota.png")
    im_crop = im.crop((0, 0, x2 // 2, 130))
    im_crop.save(("radiant.png"), quality=100)  # fine tune later
    im_crop = im.crop((x2 // 2, 0, x2, 130))
    im_crop.save(("dire.png"), quality=100)  # fine tune later

    # radiant heroes
    for i in range(5):
        a, b = 208 + (i * 125), 6
        im_crop = im.crop((a, b, a + 113, b + 64))
        im_crop.save((f"r{i}.png"), quality=100)

    # dire heroes
    for i in range(5):
        a, b = 1095 + (i * 125), 6
        im_crop = im.crop((a, b, a + 113, b + 64))
        im_crop.save((f"d{i}.png"), quality=100)

    # # close window
    # my.close()

    radiant_text = pytesseract.image_to_string('radiant.png')
    dire_text = pytesseract.image_to_string('dire.png')

    team = ""
    if name[:10].lower() in radiant_text.lower():
        team = "radiant"
    elif name[:10].lower() in dire_text.lower():
        team = "dire"
    else:
        team = "radiant"

    # def is_template_in_image(small_image, large_image):
    #     res = cv2.matchTemplate(small_image, large_image, cv2.TM_CCOEFF_NORMED)

    #     threshold = 0.6
    #     flag = False

    #     if numpy.amax(res) > threshold:
    #         flag = True
    #     return flag

    def is_image_similiar(img1, img2):

        hash0 = imagehash.average_hash(img1)
        hash1 = imagehash.average_hash(img2)
        cutoff = 11  # maximum bits that could be different between the hashes.

        if hash0 - hash1 < cutoff:
            return True
        else:
            return False

    all_heroes = []
    for filename in glob.glob('heroes/*.png'):  # assuming gif
        im = PIL.Image.open(filename)
        all_heroes.append({"img": im, "name": ''.join(i for i in filename.replace(
            "heroes\\", "").replace(".png", "") if not i.isdigit())})

    radiantHeroes = []
    direHeroes = []

    for i in range(5):
        for hero in all_heroes:
            if is_image_similiar(hero["img"], PIL.Image.open(f'r{i}.png')):
                radiantHeroes.append(hero["name"])
            if is_image_similiar(hero["img"], PIL.Image.open(f'd{i}.png')):
                direHeroes.append(hero["name"])

    radiantHeroes = [*set(radiantHeroes)]
    direHeroes = [*set(direHeroes)]

    if set(['ogre_magi', 'spectre']).issubset(set(radiantHeroes)):  #when no hero is selected, it matches with these two heroes
        if set(['ogre_magi', 'spectre']).issubset(set(direHeroes)):
            radiantHeroes = []
            direHeroes = []

    currentPicks = {
        "allies": radiantHeroes if team == "radiant" else direHeroes,
        "enemies": radiantHeroes if team == "dire" else direHeroes
    }

    # improvisation: make least matching hero pop out
    if len(currentPicks['allies']) > 4:
        currentPicks["allies"].pop()
    if len(currentPicks['enemies']) > 5:
        currentPicks["enemies"] = currentPicks["enemies"][:5]

    with open("structuredData.json") as file:
        data = json.load(file)

    def calibrate(a, b):
        for i in b:
            a[i['id']] = (a.get(i['id'], i['wr'] + i['adv']) +
                          i['wr'] + i['adv']) / 2
        return a

    for ally in currentPicks['allies']:
        allyInfo = data[ally][f'rank{rank}']['tms']
        result = calibrate(result, allyInfo)

    for enemy in currentPicks['enemies']:
        enemyInfo = data[enemy][f'rank{rank}']['ens']
        result = calibrate(result, enemyInfo)

    with open("structuredDataById.json") as file:
        databyid = json.load(file)

    carries = []
    supports = []
    for i in sorted(result, key=result.get):
        heroData = databyid[str(i)]
        if heroData['flags']['carry']:
            carries.append(heroData['iName'])
        if heroData['flags']['support']:
            supports.append(heroData['iName'])


    df = pandas.DataFrame({'CARRY': carries[:suggestions]})
    df.index += 1
    df['SUPPORT'] = supports[:suggestions]

    if radiantHeroes != [] and direHeroes != []:
        print(currentPicks)
        print(df)
    else:
        print('no heroes detected!')

    # for i, hero in enumerate(counters_synergies):
    #     listbox.insert(i, hero)

    #     # pack the widgets
    # label.pack()
    # listbox.pack()

    # # Display untill# User delete(0,END)
    # # exits themselves.
    # top.mainloop()
