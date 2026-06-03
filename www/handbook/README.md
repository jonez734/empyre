# empyre

## todo

- [ ] how to move/build sawmill,forts on island
- [x] player 'attributes' are now called 'resources'
- [ ] different types of ships (cargo, passenger) @ty dad,tmojd,ryan @since 20240107 @project 8568
- [x] make sure all attributes with a price have a singular and plural defined.
- [x] missing "each" on the end of the prompt in investments()
- [x] maint mode should prompt for handle, default to currentloginname, tab-complete.
- [ ] if there are no shipyards, do not allow purchase of ships
- [x] if there are no stables, do not allow acquiring horse(s)
- [ ] need sawmill to use lumber to build stables, ships, etc
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
- [x] scratch news
- [ ] bbs edit -> empyre coin exchange rate no longer hard-coded.
- [x] update adjust() to check for 0 nobles
- [x] update adjust() to check for not enough nobles w a call to pluralize()
- [ ] adjust() needs serious work re: nobles, soldiers
- [ ] zircon quest repeats blurbs twice
- [ ] fix "You need 26 more coins to purchase a acre" (grammar)
- [ ] You need 1.0 more coin to purchase a bushel (call int())
- [x] even with more than enough nobles, adjust() constantly defects a bunch of soldiers. when checking, player.nobles has been set to 2, even tho shortly before that, I set the number of nobles to be more than enough for the number of soldiers.
- [ ] player.status()
  * [ ] show 'soldiers' in red if it exceeds nobles*20
  * [ ] show 'ships' in red if not enough shipyards (10 ships each)
  * [ ] show 'horses' in red if not enough stables (50 horses each)
- [x] You need 29 more coins to purchase a acre
- [ ] adjust(): reduce the number of soldiers until it is under the player.nobles*20 threshhold.
- [x] replace {reverse} with {bggray}{white} and replace {/reverse} with {/all}
- [ ] You have no soldiers! when plague wipes out 993, player.soldiers=1392
- [x] harvest(): give serfs all the grain player has
- [x] adjust(): says 'no soldiers' but soldierpay > 0.
  * soldierpay is calculated based on player.soldiers, player.taxrate, player.combatvictory, and player.palaces.
- [ ] The barbarians will sell their grain to you for 1.0 coin each (floating point price, call int())
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
- [x] in player.edit(), if t == bool, call ttyio.inputboolean() not ttyio.inputchar() (uclug 2021-06-08)
- [ ] getplayerid(args, playername) returns None or playerid
- [x] in tourney(), echo the number of acres lost when attacking yourself.
- [x] check to be sure handling of boolean attributes in player.edit() is correct.
- [x] use ttyio.inputboolean() instead of ttyio.inputchar() in some places.
- [x] change inputplayername() to return playername instead of playerid
- [x] dbh.commit() a new player record.
- [x] playerid shows up in engine.node, but not empyre.player
- [x] psycopg2.errors.UndefinedColumn: column "memberid" does not exist
- [x] sysop tool to maintain players
- [ ] add index/etc so that duplicate player names (case insensitive) are not allowed across all modules
  * could write code instead of doing it in the db
  * (https://dba.stackexchange.com/questions/161313/creating-a-unique-constraint-from-a-json-object/161345)[Creating a UNIQUE constraint from a JSON object]
- [x] log entries should not show up in a 'select * from empyre.player' query.
- [x] add 'prg' column to engine.__node to simplify views.
- [x] add 'memberid' to self.attributes, and attributes->>'memberid' to view.
- [x] 'prg' attribute causing problems w empyre.player view
- [x] in maint mode, unable to edit 'name' attribute: 'jonez' is always invalid.
  * fixed by using verifyPlayerNotFound instead of the default verifyPlayerFound
- [ ] when player is edited, make logentries
  * [ ] after adding newsentry, return nodeid so subnodes can be made
- [ ] "army requires" -> if player.bushels == 0, show a message, and do not allow entering more bushels than available.
- [x] set defaults so that a new player can get through the first round wo going bankrupt.
- [x] fix empyre.play() handling of datelastplayedepoch (call (time.mktime())[https://stackoverflow.com/questions/41699998/converting-time-to-epoch-python/41700208]
- [x] datelastplayedepoch=0 should display None in player.stats()
- [ ] column width of player.status() is not correct when grain > 1000
- [ ] player.setattribute() and player.getattribute() performance
- [x] !after editing an attribute
  * new value is saved but not displayed
  * reload/update modified player record
  * player.status() looks at player.attributes, which does not get updated by edit()
  * solution was to set player = p *if* playerid matches
- [ ] in player.save(), be verbose about *which* exception has been raised.
- [x] use localtime() instead of gmtime() for player.datelastplayed. wrong timezone is displayed.
- [x] "Your army requires 201 bushels this year, and you have <x> bushels"
- [x] add call to bbsengine.title() in quests()
- [x] function empyre.title() -- careful about using 'title' as a local variable in loops (main menu, quests, etc)
- [ ] penalty for starving army
- [ ] penalty for starving horses
- [x] player.datelastplayed not properly updated (call localtime() instead of gmtime())
- [x] make default for town() input a "Q"
- [x] problem with grain calculation -- calculation error swapped "<" with ">" and it's fixed.
- [ ] show player.isdirty() result in bottom bar (setarea())
- [x] add stables to investments menu (10,000 each)
- [x] change horsesrequire = random.randint(2, 7) bushels
- [x] update player.adjust() to free horses when there are not enough stables
  * zircon awards 50 horses wo checking for enough stables
  * zircon should award enough stables, too
- [x] !after changes to use player.getattribute() and player.setattribute(), empyre no longer starts up
  * thought the problem was that player.getattribute("memberid") was returning more than the "name" key, but that is not it.
  * ultimately, getplayer() is returning the entire attribute dict instead of only the value. misuse of getattribute()?
  * getattribute is working as designed
  * added some ttyio.echo() calls to narrow down problem. "dat" is the correct value (10)
  * it looks like there is a getattribute() call for "memberid" which returned a dict instead of the value, like player.getattribute() does.
  * did a 'select * from empyre.player' and it turns out the memberid attribute has been corrupted.
  * all player attributes are corrupted. player.getattribute() returns a dict, getattr() returns only the value. not wise to make sweeping changes given diff return values.
  * set about updating all calls to player.getattribute() so they handle the dict properly.
  * properly using player.getattribute() may fix another issue with editing attributes.
  * player.status() is broken (too much whitespace). total columns? cosmetic. 
  * empyre starts now. have not tried to play a turn.
  * playing through a turn works.
  * player is being saved correctly as a result of going through every call to player.getattribute() and writing code to handle it correctly.
  * solution: player = p
- [x] when showing how many bushels the horse(s) require, eliminate the number value ("your 1 horse ..." looks wrong)
- [x] in maint mode, default 'player name' to current player name for edit()
- [ ] in combat, make sure only soldiers w assigned nobles are used (consider 10,000 soldiers for only 2 nobles, win every time wo a limit)
- [ ] after freeing 999 horses, it still calculates bushel requirements
- [x] horses freed are not saved
- [ ] add more ranks
- [ ] graffiti wall for next player to read
- [ ] where does lumber come from? islands have specific number of trees, after trees are gone, done. no more lumber. plant trees?
- [ ] handle morning, noon, night. 
- [ ] seasons
- [ ] fishing for bushels from ships (stigg, ryan)
- [ ] "You need 1 more coin to purchase a bushel" -- add cost per bushel
- [ ] enhance "yearly report" similar to empire deluxe.
- [ ] census report from empire deluxe
- [ ] allow more than one island?
- [ ] allow diff cargo per ship?
- [x] 50 horses per stable (mdl.emp.delx1.txt)
- [ ] spices are only on the colony or the fleet, not the mainland
- [ ] poll for notifications (combat)
- [ ] "%s mills are overworked!": use bbsengine.pluralize()
- [x] handle 'breaking even' in P&L
- [ ] make a way to enforce all int attributes to be ints (not floats) so that every usage does not involve calling int()
- [x] tab-complete of attribute names in edit()
- [x] edit attribute does not work
- [ ] make sure feeding horses is realistic and adjust harvest to match (mom)
- [x] add "player status" to maint menu w a prompt for the player
- [x] if editing a player, check to see if it is current player before player = p
- [x] in "natural disaster bank", do not prompt if credits < 1
- [ ] finite number of acres in entire game (@since 20220217)
- [x] market module - trade commodities (grain, land, horses, timber, spices) in turn flow (@since 20260203)
- [ ] finite number of coins in entire game (@since 20220217)
- [ ] implement "sneak attack" (@since 20220217)

## contributors
- ryan for 'empire6' (including c64list's labels), valuable variable tracing, and lots of ideas.
- uclug's June 2021 meeting for help w troubleshooting of the new player problem.
- stigg for coming up with the name 'empyre' and lots of ideas

## notes

- tried changing empyre.newsentry and empyre.player to not use the node table
  * thought 'newsentry' would work out ok until I needed an fk to empyre.player which would require a 'materialized view', which means a delay of however often I run a cron to update data.
  * 'player' might be able to stand on it's own, except my code makes use of updatenodeattributes(), and handling the exceptions (lastplayed, name, etc) will confuse the code and make it more difficult to teach.
  * [postgresql materialized views](https://www.postgresqltutorial.com/postgresql-materialized-views/)
  * in the end, decided that the complexity of the node table is not enough to justify not using it.
  * using engine.node, possible to add notes and other items to a player or newsentry.
- [ ] check if there is a member account for the current username before trying to create a new player (@since 20211216)
- [ ] realtorsadvice(): fix "name 'buf' not defined" (1391) (@since 20211216)
- [ ] news() does not show a timezone, even after calling time.tzset()
- [ ] "You have no stables for 1 horse is, 1 horse is set free." (@since 20211216)
- [ ] use :moneybag: as needed (@since 20220223)
- [ ] use :sun: and :thunder-cloud-and-rain: (@since 20220224)
- [ ] use maint, set coins to 2000, "sysop options" still shows 0 coins (@since 20220224)
- [ ] when Player is loaded from storage, be sure to set all obj attrs to loaded values so isdirty() is accurate (@since 20220410)
- [ ] make sure datelastplayedepoch is updated properly (@since 20220410)
- [ ] Player
    - when initialized, populated with default values
    - when a player is selected, self.attributes is populated
    - as a result, Player is always "dirty" since it is diff than default values
    - would save a save() if Player was initialized properly on load
    - reload player record after maint of current player (@since 20220522)
- [ ] trade() (@since 20220411)
    - [x] update bottombar after every call so dirty flag is updated (rightbuf) (@since 20220411)
    - [x] do not show player stats after a transaction by default. add 'Y' option to menu (@since 20220412, @done 20220422)
- [ ] player.save() gets called in maint mode even if the choice is not to save (@since 20220411)
- [ ] player.revert() builds self.attributes (which is a seq of dicts) values based on Player object attrs (@since 20220411)
- [ ] in player.status(), extend width by 2, result is "lastplayed" vs "lastplay.."
- [ ] if more than one player for given memberid, make sure player name input can deal with empty input (@since 20220422)
- [x] "other players" list is empty, but shows box chars anyway (@since 20220430 @done 20220430)
    * uses bbsengine.ResultIter()
- [x] go over every call to bbsengine5.setarea() and set most of them to 'stack=False' (@since 20220511 @done 20220522)
- [x] if a dragon has been killed, echo diff message based on if it is the *only* dragon (@since 20220522 @done 20220522)
- [ ] establish /usr/share/empyre/ and put text files related to quests there to start (@since 20220522)
- [ ] keep track of which quests have been completed, date, and a count (@since 20220719)
- [ ] rename empyremodules to modules (@since 20220801 @done 20220801)
- [ ] track if a ship is made by a shipyard. change adjust() to only track those shipyards (@since 20220810)
- [ ] where to get navigators (instead of making it automagic) (@since 20220810)
- [ ] trap INTR/EOF when ship(s) are docked, reset so docks are free (@since 20220810)
- [ ] Ship
- [ ] Port
- [ ] make _version a resource instead of using a py file
- [ ] handle beheading properly (@since 20220829)
- [ ] handle "no nobles" in zircon-fail.txt (@since 20220829)
- [x] python -m empyre works, but running from letteredolive does not (@since 20220828 @done 20220829)
- [ ] exports are limited to grain only.
- [ ] sell excess sawmills/etc? calc required sawmills, offer to sell excess (@since 20220907)
- [ ] drydock should allow recruiting navigators.
- [ ] min 1 navigator per ship. wo navigator, better chance of wrecking or failing to reach an island
