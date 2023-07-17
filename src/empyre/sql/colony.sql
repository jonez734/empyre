create or replace view empyre.colony as
    select b.*,
        (attributes->>'islandid')::bigint as islandid,
        (attributes->>'playerid')::bigint as playerid,
        (attributes->>'grain')::bigint as grain,
        (attributes->>'serfs')::bigint as serfs,
        (attributes->>'nobles')::bigint as nobles,
        (attributes->>'navigator')::boolean as navigator
    from engine.__blurb
    where prg='empyre.colony'
;
