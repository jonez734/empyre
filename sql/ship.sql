create or replace view empyre.ship as
    select
        n.*,
        (attributes->>'memberid')::bigint as memberid
    from engine.__node as n
    where prg='empyre.ship'
;

grant select on empyre.ship to apache;
