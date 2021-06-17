--create table if not exists empyre.__player (
--    "id" bigserial unique primary key not null,
--    "memberid" bigint constraint fk_engine_node_createdbyid references engine.__member(id) on update cascade on delete set null,
--    "attributes" jsonb,
--   "datelastplayed" timestamptz
--);

create or replace view empyre.player as
    select
        n.*,
        extract(epoch from (n.attributes->>'datelastplayed')::timestamptz) as datelastplayedepoch,
        (attributes->>'memberid')::bigint as memberid,
        (attributes->>'playername') as playername
    from engine.__node as n
    where attributes ? 'playername' and attributes ? 'datelastplayedepoch' and attributes ? 'memberid' and attributes->>'prg'='empyre'
;

grant select on empyre.player to apache;
