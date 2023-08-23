-- @since 20230716
create or replace view empyre.ship as
    select
        b.*,
        (attributes->>'memberid')::bigint as memberid,
        (attributes->>'manifest')::array as manifest,
        (attributes->>'location')::text as location,
        (attributes->>'status')::text as status,
        (attributes->>'name')::text as name
    from engine.__blurb as b
    where prg='empyre.ship'
;

grant select on empyre.ship to :web, :bbs;
