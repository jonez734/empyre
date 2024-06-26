create table if not exists empyre.__player (
    "id" bigserial unique primary key not null,
    "memberid" bigint constraint fk_empyre_player_memberid references engine.__member(id) on update cascade on delete set null,
    "moniker" text unique,
    "datelastplayed" timestamptz,
    "datecreated" timestamptz,
    "rank" bigint,
    "previousrank" bigint,
    "datepromoted" timestamptz,
    "turncount" bigint,
    "weatherconditions" bigint,
    "soldierpromotioncount" bigint,
    "combatvictorycount" bigint,
    "coins" bigint,
    "beheaded" boolean,
    "taxrate" bigint,
    "resources" jsonb
);

create or replace view empyre.player as
    select
        p.*,
        timezone(currentmember.tz, datelastplayed) as datelastplayedlocal,
        timezone(currentmember.tz, datepromoted) as datepromotedlocal
    from empyre.__player as p
    left outer join engine.__member as currentmember on (currentmember.loginid = CURRENT_USER)
;
--create or replace view empyre.player as
--    select
--        b.*,
--        extract(epoch from (b.attributes->>'datelastplayed')::timestamptz) as datelastplayedepoch,
--        (attributes->>'memberid')::bigint as memberid,
--        (attributes->>'playerid')::bigint as playerid,
--        (attributes->>'name') as name
--    from engine.__blurb as b
--    where prg='empyre.player'
--;

grant all on empyre.__player to :bbs;
grant select on empyre.player to :web, :bbs;
