# -*- coding: utf-8 -*-
# author: Ethosa
from random import choice, randint
from time import sleep
from os import listdir

from saya import Vk  # version 0.1.46 or later
from mchains import MarkovChains  # version 0.1 or later
import regex
from gtts import gTTS


vk = Vk(login=88005553535, password="qwertyuiop", debug=True)
# Images folder
# this folder should contain only images.
folder = "images/"
can_delete = False
# "F" images
photos = [
    "photo556962840_457244346", "photo556962840_457244348",
    "photo556962840_457244349"
]


@vk.on_message_new
def getmessage(event):
    print(event)
    if "object" in event and "from" in event["object"] and event["object"]["from"] == '556962840':
        mid = event["message_id"]
        # Edit message which contains "F" text.
        if event["text"] == "F":
            print("editing \"F\"...")
            vk.messages.edit(message_id=mid, message="", attachment=choice(photos),
                             peer_id=event["peer_id"])
        # Roleplay commands.
        # e.g. "рп съесть" -> "*съела*"
        elif regex.findall(r"\A\s*рп[\S\s]+[уеыаоияэ](ть\b|ться\b)[\S\s]*\s*\Z", event["text"]):
            text = event["text"].strip()[2:].strip()
            while regex.findall(r"\A\s*[\S\s]+[уеыаоияэ](ть\b|ться\b)[\S\s]*\s*\Z", text):
                text = regex.sub(r"\A\s*([\S\s]+[уеыаоияэ])(ться\b)([\S\s]*)\s*\Z",
                                 r"*\1лась\3*", text)
                text = regex.sub(r"\A\s*([\S\s]+[уеыаоияэ])(ть\b)([\S\s]*)\s*\Z",
                                 r"*\1ла\3*", text)
            vk.messages.edit(message_id=mid,
                             message=text,
                             peer_id=event["peer_id"])
        # Say
        # e.g. "сказать привет"
        elif regex.findall(r"\Aсказать[\S\s]+\Z", event["text"]):
            text = event["text"]
            # Delete the message and set voice recording activity.
            vk.messages.delete(message_ids=mid, delete_for_all=1)
            vk.messages.setActivity(peer_id=event["peer_id"], type="audiomessage")
            # call to google text to speech.
            tts = gTTS(regex.findall(r"\Aсказать([\S\s]+)\Z", text)[0], lang='ru')
            tts.save('hello.ogg')
            vk.messages.setActivity(peer_id=event["peer_id"], type="audiomessage")
            uploaded = vk.uploader.format(
                vk.uploader.document_message(
                    "hello.ogg", doc_type="audio_message",
                    peer_id=event["peer_id"]),
                "doc"
                )
            vk.messages.setActivity(peer_id=event["peer_id"], type="audiomessage")
            vk.messages.send(message_id=mid, attachment=uploaded,
                             peer_id=event["peer_id"], random_id=randint(0, 100000))
        # Markov Chains
        # Collects text from the last 200 messages in a conversation, then generates a message and sends it.
        elif regex.findall(r"\A\s*\$ген", event["text"]):
            mchains = MarkovChains()
            text = ""
            vk.messages.delete(message_ids=mid, delete_for_all=1)
            messages = vk.messages.getHistory(peer_id=event["peer_id"], count=200)["response"]["items"]
            text = " ".join(i["text"] for i in messages)
            mchains.to_chains(text)
            not_sended = True
            while not_sended:
                try:
                    vk.messages.send(message=mchains.genstr(randint(3, 20)),
                                     peer_id=event["peer_id"],
                                     random_id=randint(0, 10000),
                                     disable_mentions=1)
                    not_sended = False
                except:
                    pass

# start loop
while 1:
    photo = "%s%s" % (folder, choice(listdir(folder)))
    if can_delete:
        # Delete old photo
        p_id = vk.photos.get(album_id="profile", count=1, rev=1)["response"]["items"][0]["id"]
        a = vk.photos.delete(photo_id=p_id)
        print(a)
    # Upload new photo
    p = vk.uploader.profile_photo(photo, owner_id=556962840)
    if "response" in p:
        p = p["response"]
        can_delete = True
        print("changed!", photo)
    else:
        can_delete = False
    # Delete wall post
    if "post_id" in p:
        vk.wall.delete(post_id=p["post_id"])
    sleep(60*5)
