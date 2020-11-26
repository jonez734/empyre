create or replace view empire.player as
    select
        *,
        (attributes->>'memberid')::bigint as memberid,
        (attributes->>'datelastplayed')::timestamptz as datelastplayed,
        (attributes->>'name')::text as name
    from engine.node
    where attributes ? 'memberid' and attributes ? 'grain' and attributes ? 'land'-- and attributes ? 'mills'
;

grant select on empire.player to apache;