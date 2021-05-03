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
- [ ] "Your army requires 10,271 bushels this year." defaults to 0 (wrong).
- [ ] reconsider use of the 'node table' for games. does empyre even need subnodes for anything?

## contributors
- thanks to ryan for 'empire6' and lots of ideas.

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

```
Your army requires 10,271 bushels this year.
Give them how many? 10271
```
defaults to 0

```
This year's harvest is 26,389 bushels

Your people require 20,281 bushels of grain this year

You have 26,389 bushels and 221,216 coins
grain: [B]uy [S]ell [C]ontinue [E]dit: Continue
Give them how many? 20281
```
