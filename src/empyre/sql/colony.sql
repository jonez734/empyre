create table if not exists empyre.__colony (
    name text unique not null primary key,
    ownerid bigint not null constraint fk_empyre_colony_ownerid references engine.__member(id) on update cascade on delete set null,
    islandid bigint not null constraint fk_empyre_colony_islandid references empyre.__island(id) on update cascade on delete set null,
    resources jsonb,
    datefounded timestamptz,
    status text
--    navigator boolean
);
--create or replace view empyre.colony as
--    select b.*,
--        (attributes->>'islandid')::bigint as islandid,
--        (attributes->>'playerid')::bigint as playerid,
--        (attributes->>'grain')::bigint as grain,
--        (attributes->>'serfs')::bigint as serfs,
--        (attributes->>'nobles')::bigint as nobles,
--        (attributes->>'navigator')::boolean as navigator
--    from engine.__blurb
--    where prg='empyre.colony'
--;

grant all on empyre.__colony to :bbs;

create or replace view empyre.colony as
    select 
      c.*,
      owner.moniker as ownermoniker,
      island.name as islandname
    from empyre.__colony as c
    left join engine.__member owner on (owner.id = empyre.__colony.playerid)
    left join engine.__island island on (island.id = empyre.__colony.islandid)

grant select on empyre.colony to :bbs, :web;
