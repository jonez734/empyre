create or replace view empyre.island as
    select
        n.*,
        (attributes->>'memberid')::bigint as memberid
    from engine.__node as n
    where prg='empyre.island'
;

grant select on empyre.island to apache;
