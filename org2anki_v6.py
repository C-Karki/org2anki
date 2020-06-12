# org2anki
# v6
# Final version
# A script to parse my org notes and convert them into anki cards

from orgparse import load
from pathlib import Path
import subprocess
import os

# org file to parse
orgFile = load('/home/chitij/Documents/studies/medicine.org')
# fields generator to supply the anki fields that the card maker will need
def fieldGen(orgFile):
    fields = {} # dictionary to hold the fields
    topic = '' # main topic or the root of the tree
    subTopic = '' # sub topics of the branches of the tree
    for node in orgFile[1:]: # go through each node in the tree
        if node.todo != None: # skip blank todo nodes
            continue
        if node.level == 2: # record the topic as the root of the tree
            topic = '=(' + str.upper((node.get_heading())) + ')='
            subTopic = '' # clear out the record of branch path
        if node.level == 3: # start recording branch paths
            subTopic =  topic + '-[' + str(node.get_heading()) + ']'
        if (node.level > 3):
            subTopic = subTopic + '-[' + node.get_heading() + ']'
            if(node.previous_same_level != None):
                crap = '-['+node.previous_same_level.get_heading()+']'
                if crap in subTopic:
                    subTopic = subTopic.replace(crap, '')
        # generate field when a leaf of the tree is reached
        if (node.children == []) and (node.get_body() != "") and (node.level > 2):
            # removestrings gathered from previous paths down the tree
            if(node.previous_same_level != None):
                crap = '-['+node.previous_same_level.get_heading()+']'
                if crap in subTopic:
                    fields[subTopic.replace(crap, '')] = node.get_body()
                    subTopic = subTopic.replace('-[' + node.get_heading() + ']', '')
                    continue
            # without previous paths to worry about
            fields[subTopic] = node.get_body() # add the path and leaf in the dictionary
            subTopic = subTopic.replace('-[' + node.get_heading() + ']', '') # clear record of leaf
            if (node.next_same_level == None) and (node.level > 3):
                parent = node.get_parent()
                while parent.level != 3:
                    subTopic = subTopic.replace('-[' + parent.get_heading() + ']', '')
                    parent = parent.get_parent()


    return (fields)

# generate an org file compatible with anki-editor in emacs
# this is better because I can preserve org formatting goodies
# I need to add append function
def cardGen(fields, filePath):
    # local variables
    if Path(filePath).exists() is False: #create file if not exists
        Path(filePath).touch()
    ankiFile = open(Path(filePath), 'a+')
    ankiCard = '''* Item
    :PROPERTIES:
    :ANKI_DECK: Respiratory
    :ANKI_NOTE_TYPE: Basic
    :END:\n''' #anki card format and properties
    front = '** Front\n' # insert field for front of the card
    back = '** Back\n'    # insert field for back of the card

    for frontField in fields.keys():
        if frontField not in ankiFile.read():
            backField = fields[frontField]
            text = ankiCard + front + frontField + '\n' + back + backField + '\n'
        ankiFile.write(text)
    ankiFile.close()

cards = fieldGen(orgFile)
exportFile = '/home/chitij/Documents/studies/anki/respi_anki2.org'
cardGen(cards, exportFile)
#if ("anki" not in (p.name() for p in psutil.process_iter())):
#    subprocess.Popen('anki')




