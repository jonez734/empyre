create or replace view empire.newsentry as
    select *,
        attributes->>'message' as message,
        attributes->>'playerid' as playerid,
        attributes->>'memberid' as memberid
        -- attributes->>'status' as status -- 'scratched', etc
    from engine.node
    where attributes ? 'message' and attributes ? 'memberid' and attributes ? 'playerid'
;

grant select on empire.newsentry to apache;
