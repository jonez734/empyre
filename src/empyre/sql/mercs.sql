--\echo mercs
create table empyre.__mercs (
    teammoniker text unique not null primary key,
    hiredbymoniker text constraint fk_mercs_hiredbymoniker references empyre.__player(moniker) on update cascade on delete set null,
    price bigint,
    quantity bigint,
    contractstart timestamptz,
    contractduration interval -- turns instead of time?
);

grant all on empyre.__mercs to term, sysop;

create view empyre.mercs as
    select m.*,
        timezone(currentmember.tz, contractstart) as contractstartlocal,
        (contractstart + contractduration) as contractend,
        timezone(currentmember.tz, (contractstart+contractduration)) as contractendlocal -- contractstart + contractduration) as contractendlocal,
    from empyre.__mercs as m
    left outer join engine.__member as currentmember on (currentmember.loginid = CURRENT_USER)
;
grant select on empyre.mercs to web, term, sysop;
    