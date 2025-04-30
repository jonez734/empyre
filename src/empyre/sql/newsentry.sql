\echo newsentry
create table if not exists empyre.__newsentry (
    "id" bigserial not null unique primary key,
    "message" text,
    "status" text,
    "datecreated" timestamptz,
    "playermoniker" citext references empyre.__player(moniker) on update cascade on delete set null,
    "membermoniker" citext references engine.__member(moniker) on update cascade on delete set null
);

create or replace view empyre.newsentry as
    select
      ne.*
    from empyre.__newsentry as ne
    left join engine.__member m on (m.moniker = ne.membermoniker)
    left join empyre.__player p on (p.moniker = ne.playermoniker)
;

grant select on empyre.newsentry to web, term, sysop;
grant all on empyre.__newsentry to term, sysop;
