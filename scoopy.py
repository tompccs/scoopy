#!/usr/bin/env python

from sys import argv
from subprocess import call
from math import floor, ceil

import curses
import re
import feedparser
import sklearn

from sklearn.externals import joblib

TRAINER_TITLE = "==== SCOOPY Interactive Trainer ===="

DEFAULT_FEEDS = ('http://feeds.nature.com/nphoton/rss/current',
 'http://aip.scitation.org/action/showFeed?type=etoc&amp;feed=rss&amp;jc=apl',
 'http://www.nature.com/nmat/current_issue/rss/index.html',
 'http://feeds.nature.com/srep/rss/current',
 'http://feeds.nature.com/NaturePhysicalSciencesResearch',
 'http://feeds.nature.com/NatureLatestResearch',
 'http://science.sciencemag.org/rss/current.xml',
 'http://advances.sciencemag.org/rss/current.xml',
 'http://metadata.osa.org/rss/infobase/aop_feed.xml',
 'http://metadata.osa.org/rss/infobase/ao_feed.xml',
 'http://metadata.osa.org/rss/infobase/boe_feed.xml',
 'http://metadata.osa.org/rss/infobase/josaa_feed.xml',
 'http://metadata.osa.org/rss/infobase/josab_feed.xml',
 'http://metadata.osa.org/rss/infobase/optica_feed.xml',
 'http://metadata.osa.org/rss/infobase/ome_feed.xml',
 'http://metadata.osa.org/rss/infobase/opex_feed.xml',
 'http://metadata.osa.org/rss/infobase/ol_feed.xml',
 'http://metadata.osa.org/rss/infobase/prj_feed.xml',
 'http://www.spie.org/x2402.xml?ss=rss',
 'http://www.spie.org/x2416.xml?ss=rss',
 'http://www.spie.org/x2400.xml?ss=rss',
 'http://www.spie.org/x2406.xml?ss=rss',
 'http://ieeexplore.ieee.org/rss/TOC10.XML',
 'http://ieeexplore.ieee.org/rss/TOC50.XML',
 'http://ieeexplore.ieee.org/rss/TOC42.XML',
 'http://onlinelibrary.wiley.com/rss/journal/10.1002/(ISSN)1521-4095')

DEFAULT_BROWSER = "firefox"
DATASET_LOCATION = "data.pkl"

KEY_RELEVANT = 1
KEY_IRRELEVANT = 2

def interactive_trainer(stdscr, feeds=DEFAULT_FEEDS, dataset=[]):
    stdscr.clear()

    stdscr.addstr(0,0,"Loading...")
    
    for feed_url in feeds:
        stdscr.clear()
        title_pos = (curses.COLS-len(TRAINER_TITLE))//2
        stdscr.addstr(0,title_pos if title_pos >= 0 else 0,TRAINER_TITLE,
                      curses.A_STANDOUT)
        stdscr.addstr(curses.LINES//2,curses.COLS//2,"Loading feed...")
        stdscr.addstr(curses.LINES//2+1,2,"Fetching feed from URL: {}".format(feed_url))
        stdscr.refresh()

        feed = feedparser.parse(feed_url)
        try:
            ftitle = feed['feed']['title']
            if ftitle == None:
                raise KeyError
            else:
                look_at_previous_item = False
                advancing_to_next_feed = False
                for entry_num in range(len(feed.entries)):
                    stdscr.clear()

                    if advancing_to_next_feed:
                        break
                    
                    entry = feed.entries[entry_num if not look_at_previous_item else entry_num - 1]
                    
                    title_pos = (curses.COLS-len(TRAINER_TITLE))//2
                    stdscr.addstr(0,title_pos if title_pos >= 0 else 0,TRAINER_TITLE,
                                  curses.A_STANDOUT)
                    stdscr.addstr(2,2," -- {}".format(ftitle.encode('ascii', 'xmlcharrefreplace')))
                    stdscr.addstr(3,2," -- Article {} of {}".format(entry_num,len(feed.entries)))
                    stdscr.addstr(4,2,"'{}'".format(entry.title.encode('ascii',
                                                                       'xmlcharrefreplace')))

                    # print as much of the abstract as we have room for on the terminal
                    numlines = curses.LINES - 10
                    abstract_words = entry.description.split(" ")
                    word_index = 0
                    for row in range(numlines):
                        currentline = ""
                        while word_index < len(abstract_words) and \
                              len(currentline + abstract_words[word_index]) < curses.COLS - 2:
                            currentline = currentline + " " + abstract_words[word_index]
                            word_index += 1
                        stdscr.addstr(row + 8,0,currentline.encode('ascii', 'xmlcharrefreplace'))
                    if word_index < len(abstract_words) - 1 and row >= numlines - 1:
                        stdscr.addstr(row + 9,0,"[truncated]")

                    stdscr.addstr(curses.LINES - 2, 0,
                                  "PRESS: 'j' -> RELEVANT; 'o' -> NOT RELEVANT; " + \
                                  "'[space]' -> READ; 'q' -> QUIT")
                    stdscr.addstr(curses.LINES - 1, 0,
                                  "       'i' -> IGNORE;   'f' -> NEXT JOURNAL; " + \
                                  ("'u' -> UNDO;" if \
                                  not look_at_previous_item and \
                                   not entry_num == 0 else ""))
                    
                    advancing_to_next_item = False
                    while not advancing_to_next_item:
                        choice = stdscr.getkey()
                        if choice == "j":
                            dataset.append([entry.title, KEY_RELEVANT])
                            advancing_to_next_item = True
                            look_at_previous_item = False
                        elif choice == "o":
                            dataset.append([entry.title, KEY_IRRELEVANT])
                            advancing_to_next_item = True
                            look_at_previous_item = False
                        elif choice == "i":
                            advancing_to_next_item = True
                            look_at_previous_item = False
                        elif choice == " ":
                            call([DEFAULT_BROWSER, entry.link])
                        elif choice == "f":
                            advancing_to_next_feed = True
                            advancing_to_next_item = True
                            look_at_previous_item = False
                        elif choice == "u" and not look_at_previous_item and not entry_num == 0:
                            if len(dataset) > 0: dataset.pop()
                            look_at_previous_item = True
                            advancing_to_next_item = True
                        elif choice == "q":
                            return dataset
        except KeyError:
            continue
    

def load_existing_dataset(location=DATASET_LOCATION):
    try:
        existing_file = open(DATASET_LOCATION, 'rb')
        dataset = joblib.load(existing_file)
        existing_file.close()
    except FileNotFoundError as e:
        dataset = []
    return dataset

def save_dataset(dataset, location=DATASET_LOCATION):
    if dataset != None and len(dataset) > 0:
        joblib.dump(dataset, location, compress=True)
    
def start_interactive_trainer(feeds=DEFAULT_FEEDS, ds_location=DATASET_LOCATION):
    # This function builds a training set
    dataset = []
    curses.wrapper(interactive_trainer, feeds, dataset)

    # Load an existing dataset, if it exists, and append the new additions
    existing_dataset = load_existing_dataset(ds_location)

    for entry in existing_dataset:
        dataset.append(entry)
    
    save_dataset(dataset, ds_location) 

def load_akregator_feeds(filename):
    fin = open(filename, 'r')

    urls = []
    
    for line in fin:
        m = re.search("(?<=xmlUrl\=\")[^\"]+",line)
        if m != None:
            urls.append(m.group(0))

    fin.close()
    return urls

def main(args):
    print("Scoopy is a command-line utility to help you keep up with")
    print("research relevant to you")
    print()


if __name__ == '__main__':
    main(argv)

