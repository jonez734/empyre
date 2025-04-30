\echo player
create table if not exists empyre.__player (
--    "id" bigserial unique primary key not null,
    "membermoniker" citext constraint fk_empyre_player_membermoniker references engine.__member(moniker) on update cascade on delete set null,
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

grant all on empyre.__player to term, sysop;
grant select on empyre.player to web, term, sysop;
