create table if not exists empyre.__colony (
    name text unique not null primary key,
    founderid bigint not null constraint fk_empyre_colony_founderid references engine.__member(id) on update cascade on delete set null,
    islandname text not null constraint fk_empyre_colony_islandname references empyre.__island(name) on update cascade on delete set null,
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
      founder.moniker as foundermoniker
    from empyre.__colony as c
    left join engine.__member founder on (founder.id = c.founderid)
;

grant select on empyre.colony to :bbs, :web;
