-- @since 20230824
create table if not exists empyre.__ship (
    "moniker" text unique not null primary key,
    "playermoniker" text constraint fk_empyre_ship_playermoniker references empyre.__player(moniker) on update cascade on delete set null,
    "location" text,
    "status" text,
    "manifest" jsonb,
    "navigator" boolean,
    "kind" text, --# @ty tmovacik "cargo" first, then "passengers" (dad)
    "datedocked" timestamptz,
    "datecreated" timestamptz,
    "createdbyid" bigint constraint fk_empyre_ship_createdbyid references engine.__member(id) on update cascade on delete set null,
    "dateupdated" timestamptz,
    "updatedbyid" bigint constraint fk_empyre_ship_updatedbyid references engine.__member(id) on update cascade on delete set null
);

-- @since 20230716
create or replace view empyre.ship as
    select
        ship.*,
        timezone(member.tz, datedocked) as datedockedlocal
--        player.moniker as playermoniker
    from empyre.__ship as ship
    left join empyre.__player as player on (player.moniker = ship.playermoniker)
    left join engine.__member as member on (player.moniker = ship.playermoniker and player.memberid = member.id)
;

grant select on empyre.ship to :web, :bbs;
grant all on empyre.__ship to :bbs;
