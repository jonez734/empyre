\echo island
create table if not exists empyre.__island (
    "name" text unique not null primary key,
    "playermoniker" text constraint fk_empyre_island_playermoniker references empyre.__player(moniker) on update cascade on delete set null,
    "resources" jsonb,
    "status" text,
    "datediscovered" timestamptz,
    "discoveredbymoniker" text constraint fk_empyre_island_discoveredbymoniker references empyre.__player(moniker) on update cascade on delete set null
);

grant all on empyre.__island to term, sysop;

create or replace view empyre.island as
    select
        i.*,
        timezone(currentmember.tz, i.datediscovered) as datediscoveredlocal
    from empyre.__island as i
    left join engine.__member as currentmember on (currentmember.loginid = current_user)
;

grant select on empyre.__island to term, web, sysop;
grant all on empyre.__island to term, sysop;
