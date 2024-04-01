-- @since 20230824
create table if not exists empyre.__ship (
    "moniker" text unique not null primary key,
    "playermoniker" text constraint fk_empyre_ship_playermoniker references empyre.__player(moniker) on update cascade on delete set null,
    "location" text,
    "status" text,
    "manifest" jsonb,
    "navigator" boolean,
    "kind" text, --# @ty tmovacik "cargo" first, then "passengers" (dad)
    "datedocked" timestamptz,
    "datecreated" timestamptz,
    "createdbymoniker" text constraint fk_empyre_ship_createdbyid references engine.__member(moniker) on update cascade on delete set null,
    "dateupdated" timestamptz,
    "updatedbymoniker" text constraint fk_empyre_ship_updatedbyid references engine.__member(moniker) on update cascade on delete set null
);

grant all on empyre.__ship to :bbs;
