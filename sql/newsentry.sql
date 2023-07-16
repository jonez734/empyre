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
      b.*,
      (b.attributes->>'message')::text as message,
      (b.attributes->>'playerid')::bigint as playerid,
      (b.attributes->>'memberid')::bigint as memberid,
      (b.attributes->>'status')::text as status -- 'scratched', etc
    from engine.blurb as b -- empyre.__newsentry
    where prg='empyre.newsentry' and attributes ? 'message' and attributes ? 'playerid' and attributes ? 'memberid'
;

grant select on empyre.newsentry to :web;
