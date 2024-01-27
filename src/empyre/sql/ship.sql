-- @since 20230824
create table if not exists empyre.__ship (
    "name" text unique not null primary key,
    "playerid" bigint constraint fk_empyre_ship_playerid references empyre.__player(id) on update cascade on delete set null,
    "location" text,
    "status" text,
    "manifest" jsonb,
    "navigator" boolean,
    "kind" text, # @ty tmovacik "cargo" first, then "passengers" (dad)
    "datecreated" timestamptz,
    "createdbyid" bigint constraint fk_empyre_ship_createdbyid references engine.__member(id) on update cascade on delete set null,
    "dateupdated" timestamptz,
    "updatedbyid" bigint constraint fk_empyre_ship_updatedbyid references engine.__member(id) on update cascade on delete set null
);

-- @since 20230716
create or replace view empyre.ship as
    select
        s.*,
        player.moniker as playermoniker
    from empyre.__ship as s
    left join empyre.__player as player on (player.id = s.playerid)
;

grant select on empyre.ship to :web, :bbs;
grant all on empyre.__ship to :bbs;
