# empyre

## todo
- [x] make sure all attributes with a price have a singular and plural defined.
- [x] missing "each" on the end of the prompt in investments()
- [x] maint mode should prompt for handle, default to currentloginname, tab-complete.
- [ ] palaces
  * player.palaces in 10% increments sometimes
  * other places, you buy a complete palace
  * combat
  * rank
- [x] change place where main() calls title() so it is after the clear screen / initscreen calls.
- [ ] inputplayername has *case sensitive* tab complete
- [ ] completer for edit player profile attribute
  * attributes are not shortened like in player.status()
  * can this be done cleanly using readline?
- [ ] timber
- [ ] scratch news
- [ ] bbs edit -> empyre coin exchange rate no longer hard-coded.
- [ ] update adjust() to check for 0 nobles
- [ ] update adjust() to check for not enough nobles w a call to pluralize()
- [ ] adjust() needs serious work re: nobles, soldiers
- [ ] zircon quest repeats blurbs twice
- [ ] fix "You need 26 more coins to purchase a acre" (grammar)
- [ ] You need 1.0 more coin to purchase a bushel (call int())
- [ ] even with more than enough nobles, adjust() constantly defects a bunch of soldiers. when checking, player.nobles has been set to 2, even tho shortly before that, I set the number of nobles to be more than enough for the number of soldiers.
- [ ] in player.status(), show 'soldiers' in red if it exceeds nobles*20
- [x] You need 29 more coins to purchase a acre
- [ ] adjust(): reduce the number of soldiers until it is under the player.nobles*20 threshhold.
- [x] replace {reverse} with {bggray}{white} and replace {/reverse} with {/all}
- [ ] You have no soldiers! when plague wipes out 993, player.soldiers=1392
- [ ] harvest(): give serfs all the grain player has
- [x] adjust(): says 'no soldiers' but soldierpay > 0.
  * soldierpay is calculated based on player.soldiers, player.taxrate, player.combatvictory, and player.palaces.
- [ ] The barbarians will sell their grain to you for 1.0 coin each (floating point price)
- [ ] Your army requires 13,921 bushels this year. Give them how many? 0 (wrong default)
- [ ] add 'your stats' ("Y") to investments()
- [ ] "Your army requires 10,271 bushels this year." input defaults to 0 (wrong).
- [ ] reconsider use of the 'node table' for games. does empyre even need subnodes for anything?
- [ ] when a new player is created calculate rank (currently defaults to None)

- [ ] make sure player.name is set correctly on new player (set to None) (uclug 2021-06-08)
  * player.setattribute() added
  * fixed database empyre.player view to use engine.node instead of a separate table. problem solved.
  * updated player.new()
    - set attributes to defaults
    - set player.name and player.attributes["name"] based on inputplayername() result
- [ ] in player.edit(), if t == bool, call ttyio.inputboolean() not ttyio.inputchar() (uclug 2021-06-08)
- [ ] getplayerid(args, playername) returns None or playerid
- [x] in tourney(), echo the number of acres lost when attacking yourself.
- [ ] check to be sure handling of boolean attributes in player.edit() is correct.
- [ ] use ttyio.inputboolean() instead of ttyio.inputchar() in some places.
- [x] change inputplayername() to return playername instead of playerid
- [ ] dbh.commit() a new player record.
- [x] playerid shows up in engine.node, but not empyre.player
- [x] psycopg2.errors.UndefinedColumn: column "memberid" does not exist
- [ ] sysop tool to maintain players
- [ ] add index/etc so that duplicate player names (case insensitive) are not allowed across all modules
  * could write code instead of doing it in the db
  * (https://dba.stackexchange.com/questions/161313/creating-a-unique-constraint-from-a-json-object/161345)[Creating a UNIQUE constraint from a JSON object]
- [x] log entries should not show up in a 'select * from empyre.player' query.
- [x] add 'prg' column to engine.__node to make views easier.
- [x] add 'memberid' to self.attributes, and attributes->>'memberid' to view.
- [x] 'prg' attribute causing problems w empyre.player view
- [x] in maint mode, unable to edit 'name' attribute: 'jonez' is always invalid.
  * fixed by using verifyPlayerNotFound instead of the default verifyPlayerFound
- [ ] when player is edited, make logentr(y|ies)
  * [ ] after adding newsentry, return nodeid so subnodes can be made
- [ ] "army requires" -> if player.bushels == 0, show a message, and do not allow entering more bushels than available.
- [ ] set defaults so that a new player can get through the first round wo going bankrupt.
- [x] fix empyre.play() handling of datelastplayedepoch (call (time.mktime())[https://stackoverflow.com/questions/41699998/converting-time-to-epoch-python/41700208]
- [x] datelastplayedepoch=0 should display None in player.stats()
- [ ] column width of player.status() is not correct when grain > 1000
- [ ] player.setattribute() and player.getattribute() performance
- [ ] after editing an attribute
  * new value is saved, but not displayed
  * reload/update modified player record
  * player.status() looks at player.attributes, which does not get updated by edit()
- [ ] in player.save(), be verbose about *which* exception has been raised.
- [x] use localtime() instead of gmtime() for player.datelastplayed. wrong timezone is displayed.
- [x] "Your army requires 201 bushels this year, and you have <x> bushels"
- [x] add call to bbsengine.title() in quests()
- [x] function empyre.title() -- careful about using 'title' as a local variable in loops (main menu, quests, etc)
- [ ] does starving your army cause probs when attacking or defending? should it?
- [x] player.datelastplayed not properly updated (call localtime() instead of gmtime())
- [x] make default for town() input a "Q"
- [x] problem with grain calculation -- calculation error swapped "<" with ">" and it's fixed.
```
This year's harvest is 9,731 bushels

Your people require 8,841 bushels of grain this year

You have 9,731 bushels and 4,235 coins
grain: [B]uy [S]ell [C]ontinue [E]dit: Continue
Give them how many? 8841

 player.grain=0 
Your army requires 141 bushels this year and you have no bushels.
 armyrequires=141 player.grain=0 
Give them how many? 0
```
```
Your army requires 10,271 bushels this year.
Give them how many? 10271
```

```
This year's harvest is 26,389 bushels

Your people require 20,281 bushels of grain this year

You have 26,389 bushels and 221,216 coins
grain: [B]uy [S]ell [C]ontinue [E]dit: Continue
Give them how many? 20281
```
- [ ] make sure the zircon script fails a small part of the time
- [ ] when terminal less than full screen, bottom bar is not updated correctly.
- [ ] horses should require a certain amount of grain per year. penalty if they are not maintained.
- [ ] figure some way to handle multi-player at a time

## contributors
- ryan for 'empire6' (including c64list's labels), valuable variable tracing, and lots of ideas.
- uclug's June 2021 meeting for help w troubleshooting of the new player problem.
- stigg for coming up with the name 'empyre'

## notes
```
quest [123?Q]: 3 -- Seek Arch-Mage Zircon's Help
    Warning: Zircon's help is a gamble!
Your rivals are pressing you hard!  In desperation, you have undertaken a long and dangerous journey.  Now at last you stand before Castle
Dragonmare, the home of Arch-mage Zircon.  It is your hope that you can convince him to help you..


Your rivals are pressing you hard!  In desperation, you have undertaken a long and dangerous journey.  Now at last you stand before Castle
Dragonmare, the home of Arch-mage Zircon.  It is your hope that you can convince him to help you..


Zircon says he must consult the bones...
You are gifted 40,000 bushels, 1,000 serfs, and 10 tons of spices by Arch-Mage Zircon.
Quest Completed.
Not enough nobles!
You have no soldiers!
jonez: dirty. saving.
calling 'tourney'
tourney.100: otherplayer=None

Traceback (most recent call last):
  File "/usr/lib64/python3.9/runpy.py", line 197, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/usr/lib64/python3.9/runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "/home/jam/projects/empyre/empyre.py", line 2383, in <module>
    main()
  File "/home/jam/projects/empyre/empyre.py", line 2377, in main
    mainmenu(args, currentplayer)
  File "/home/jam/projects/empyre/empyre.py", line 1702, in mainmenu
    callback(args, player)
  File "/home/jam/projects/empyre/empyre.py", line 2339, in play
    res = f(args, player)
  File "/home/jam/projects/empyre/empyre.py", line 140, in tourney
    if otherplayer.nobles < 2:
AttributeError: 'NoneType' object has no attribute 'nobles'
```

- tried changing empyre.newsentry and empyre.player to not use the node table
  * thought 'newsentry' would work out ok until I needed an fk to empyre.player which would require a 'materialized view', which means a delay of however often I run a cron to update data.
  * 'player' might be able to stand on it's own, except my code makes use of updatenodeattributes(), and handling the exceptions (lastplayed, name, etc) will confuse the code and make it more difficult to teach.
  * [postgresql materialized views](https://www.postgresqltutorial.com/postgresql-materialized-views/)
  * in the end, decided that the complexity of the node table is not enough to justify not using it.
  * using engine.node, possible to add notes and other items to a player or newsentry.
