\echo empyre.newsentry
--create table if not exists empyre.__newsentry (
--    "id" bigserial not null unique primary key,
--    "message" text,
--    "status" text,
--    "playerid" bigint references empyre.player(id) on update cascade on delete set null,
--    "memberid" bigint references engine.__member(id) on update cascade on delete set null
--);

-- grant insert, update, delete on empyre.__newsentry to apache;

create or replace view empyre.newsentry as
    select
      *,
      attributes->>'message' as message,
      attributes->>'playerid' as playerid,
      attributes->>'memberid' as memberid,
      attributes->>'status' as status -- 'scratched', etc
    from engine.node -- empyre.__newsentry
    where attributes->>'prg'='empyre' and attributes ? 'message' and attributes ? 'status' and attributes ? 'playerid' and attributes ? 'memberid'
;

grant select on empyre.newsentry to apache;
