create table if not exists empyre.__colony (
    name text unique not null primary key,
    founderid bigint not null constraint fk_empyre_colony_founderid references empyre.__player(id) on update cascade on delete set null,
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
      founder.moniker as foundermoniker,
      timezone(currentmember.tz, c.datefounded) as datefoundedlocal
    from empyre.__colony as c
    left join empyre.__player as founder on (founder.id = c.founderid)
    left join engine.__member as currentmember on (currentmember.loginid = current_user)
;

grant select on empyre.colony to :bbs, :web;
