create table if not exists empyre.__island (
    "name" text unique not null primary key,
    "playermoniker" bigint constraint fk_empyre_island_playermoniker references empyre.__player(moniker) on update cascade on delete set null,
    "resources" jsonb
);

create or replace view empyre.island as
    select
        i.*
    from empyre.__island as i
;

--create or replace view empyre.island as
--    select
--        b.*,
--        (attributes->>'memberid')::bigint as memberid,
--        (attributes->>'playerid')::bigint as playerid,
--        (attributes->>'timber')::bigint as timer
--    from engine.__blurb as b
--    where prg='empyre.island'
--;

--grant select on empyre.island to :bbs, :web;
grant all on empyre.__island to :bbs;
