#!/usr/bin/env python

import re
import sys

import ttyio4 as ttyio

#
# >>> os.system("tput setaf 1 ; echo -n 'foo!'; tput sgr0; echo")
#

buf = """
{red}Lorem {reverse}ipsum {blink}dolor{/blink} sit amet,
consectetur {cyan}adipiscing elit,{/reverse} {purple}sed do eiusmod tempor
incididunt ut labore{green} et dolore {blue}magna aliqua.  {yellow}Ut enim
ad minim {orange}veniam, quis nostrud exercitation ullamco {brown}laboris
nisi ut aliquip ex ea {lightred}commodo consequat.  Duis aute irure
{gray}dolor in reprehenderit{/bold} in {strike}voluptate velit esse{/strike}
cillum dolore eu fugiat nulla pariatur.  {italic}Excepteur sint{/italic}
occaecat {lightgreen}cupidatat non proident, sunt in {lightblue}culpa qui
officia {underline}deserunt mollit anim id{/underline} minim veniam,
{lightgray}quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea
commodo consequat.  {bold}{green}Duis aute{/green}{/bold} irure dolor in
reprehenderit in voluptate est laborum.{/all}"""

# buf = buf.replace("\n", " ")

print (buf)
print

buf = "{cyan}cyan here{/cyan} {lightgreen}lightgreen here{/all}"
ttyio.echo(buf)
sys.exit(0)

#print ()
commandre = re.compile("\\{\\/?[^\\{]+\\}")#.match(s)
wordre = re.compile("([^\s\\{]+)")
emojire = re.compile(":([^\s]+):") # :lol:
# match = commandre.match(buf)
# print("match=%r" % (match))
# sys.exit(0)

value = ""
token = None
nodes = []

# 3 possible tokens: WORD, COMMAND, and WHITESPACE
for ch in buf:
    if ch == "{":
        if len(value) > 0:
            nodes.append({"token":"WORD", "value":value})
        token = "COMMAND"
        value = ""
    elif ch == "}":
        nodes.append({"token":"COMMAND", "value":"{%s}" % (value)})
        value = ""
        token = None
    elif ch.isspace() is True:
        nodes.append({"token":"WORD", "value":value})
        nodes.append({"token":"WHITESPACE", "value":ch})
        value = ""
        token = None
    else:
        value += ch
    # print (token, value)
#print(nodes)

terminalwidth = ttyio.getterminalwidth()
width = terminalwidth

#                .byte cursor_cyan // (default color)
#                .byte cursor_white
#                .byte cursor_red
#                .byte cursor_cyan
#                .byte cursor_purple
#                .byte cursor_green
#                .byte cursor_blue
#                .byte cursor_yellow
#                .byte cursor_orange
#                .byte cursor_brown
#                .byte cursor_lt_red
#                .byte cursor_gray1
#                .byte cursor_gray2
#                .byte cursor_lt_green
#                .byte cursor_lt_blue
#                .byte cursor_gray3

# https://www.c64-wiki.com/wiki/Color
# https://en.wikipedia.org/wiki/ANSI_escape_code
mcicommands = (
{ "command": "{clear}",      "ansi": "2J" },
{ "command": "{home}",       "ansi": "0;0H" },
{ "command": "{clreol}",     "ansi": "0K" },
{ "command": "{/all}",       "ansi": "0m" },

{ "command": "{bold}",       "ansi": "1m" },
{ "command": "{/bold}",      "ansi": "22m" },
{ "command": "{faint}",      "ansi": "2m" },
{ "command": "{italic}",     "ansi": "3m" },
{ "command": "{/italic}",    "ansi": "23m" },
{ "command": "{underline}",  "ansi": "4m" },
{ "command": "{/underline}", "ansi": "24m" },
{ "command": "{blink}",      "ansi": "5m" },
{ "command": "{/blink}",     "ansi": "25m" },

{ "command": "{strike}",     "ansi": "9m" },
{ "command": "{/strike}",    "ansi": "29m" },

{ "command": "{magenta}",    "ansi": "35m" },

{ "command": "{reverse}",    "ansi": "7m" },
{ "command": "{/reverse}",   "ansi": "27m" },

{ "command": "{white}",      "ansi": "38;2;255;255;255",  "rgb": (255,255,255) }, # 37m
{ "command": "{red}",        "ansi": "38;2;136;0;0m",     "rgb": (136,0,0) }, # 31m
{ "command": "{cyan}",       "ansi": "38;2;170,255,238m", "rgb": (170,255,238) }, # 36m
{ "command": "{purple}",     "ansi": "38;2;204;68;204m",  "rgb": (204, 68, 204) }, # 35m
{ "command": "{green}",      "ansi": "38;2;0;204;85m",    "rgb": (0,204,85) }, # 32m
{ "command": "{blue}",       "ansi": "38;2;0;0;170m",     "rgb": (0,0,170) }, # 34m
{ "command": "{yellow}",     "ansi": "38;2;238;238;119m", "rgb": (238,238,119) }, # 33m
{ "command": "{orange}",     "ansi": "38;2;221;136;85m",  "rgb": (221,136,85) },
{ "command": "{brown}",      "ansi": "38;2;102;68;0m",    "rgb": (102,68,0) },
{ "command": "{lightred}",   "ansi": "38;2;255;119;119m", "rgb": (255, 119, 119) },
{ "command": "{darkgray}",   "ansi": "38;2;51;51;51m",    "rgb": (51, 51, 51) },
{ "command": "{gray}",       "ansi": "38;2;119;119;119m", "rgb": (119, 119, 119) },
{ "command": "{lightgreen}", "ansi": "38;2;170;255;102",  "rgb": (170, 255, 102) },
{ "command": "{lightblue}",  "ansi": "38;2;0;136;255m",   "rgb": (0, 136, 255) },
{ "command": "{lightgray}",  "ansi": "38;2;187;187;187m", "rgb": (187, 187, 187) },
{ "command": "{black}",      "ansi": "38;2;0;0;0m",       "rgb": (0,0,0) } # 30m
)

# print ("-start-")
buf = ""
pos = 0
for n in nodes:
    token = n["token"]
    value = n["value"]
    if token == "WORD":
        if len(value)+pos > width:
            pos = 0
            buf += "\n"
        else:
            pos += len(value)
            buf += value
    elif token == "WHITESPACE":
        if pos > 0:
            buf += " "
            pos += 1
    elif token == "COMMAND":
        value = value.lower()
        print("value=%r" % (value))
        for item in mcicommands:
            command = item["command"]
            ansi = item["ansi"]
            if value == command:
                # print("value == k")
                buf += "\033[%s" % (ansi)
                break
    else:
        buf += value

# ttyio.echo(buf)
print(buf)

buf = ""
for n in nodes:
    token = n["token"]
    value = n["value"]
    if token != "COMMAND":
        buf += value
print
print
print(buf, len(buf))
