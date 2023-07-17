create or replace view empyre.island as
    select
        b.*,
        (attributes->>'memberid')::bigint as memberid,
        (attributes->>'playerid')::bigint as playerid,
        (attributes->>'timber')::bigint as timer
    from engine.__blurb as b
    where prg='empyre.island'
;

grant select on empyre.island to :bbs;
