\echo empyre.newsentry
create table if not exists empyre.__newsentry (
    "id" bigserial not null unique primary key,
    "message" text,
    "status" text,
    "datecreated" timestamptz,
    "playerid" bigint references empyre.__player(id) on update cascade on delete set null,
    "memberid" bigint references engine.__member(id) on update cascade on delete set null
);

create or replace view empyre.newsentry as
    select
      ne.*
    from empyre.__newsentry as ne
;

grant select on empyre.newsentry to :web, :bbs;
grant all on empyre.__newsentry to :bbs;
