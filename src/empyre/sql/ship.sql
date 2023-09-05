-- @since 20230824
create table if not exists empyre.__ship (
    "name" text unique not null primary key,
    "ownerid" bigint constraint fk_empyre_ship_memberid references engine.__member(id) on update cascade on delete set null,
    "location" text,
    "status" text,
    "manifest" jsonb,
    "navigator" boolean,
    "datecreated" timestamptz
);

-- @since 20230716
create or replace view empyre.ship as
    select
        s.*,
    from empyre.__ship as s
    left join engine.__member as owner on (owner.id = empyre.__ship.ownerid)
;

grant select on empyre.ship to :web, :bbs;
grant all on empyre.__ship to :bbs;
