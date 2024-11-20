create table empyre.__mercs (
    playermoniker text not null constraint fk_mercs_playermoniker references empyre.__player(moniker) on update cascade on delete set null,
    price bigint,
    quantity bigint,
    datehired timestamptz,
    duration interval,
    level int
);

grant all on empyre.__mercs to term, sysop;

create view empyre.mercs as
    select m.*,
        timezone(currentmember.tz, datehired) as datehiredlocal,
        timezone(currentmember.tz, datehired + duration) as dateexpireslocal,
        (datehired + duration) as dateexpires
    from empyre.__mercs as m
    left outer join engine.__member as currentmember on (currentmember.loginid = CURRENT_USER)

grant select on empyre.mercs to web, term, sysop;
    