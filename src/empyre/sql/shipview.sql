-- @since 20230716
create or replace view empyre.ship as
    select
        s.*,
        timezone(currentmember.tz, s.datedocked) as datedockedlocal,
        timezone(currentmember.tz, s.datecreated) as datecreatedlocal,
        timezone(currentmember.tz, s.dateupdated) as dateupdatedlocal
--        player.moniker as playermoniker
    from empyre.__ship as s
    left join empyre.__player as player on (player.moniker = s.playermoniker)
    left join engine.__member as member on (player.moniker = s.playermoniker and player.memberid = member.id)
    left join engine.__member as currentmember on (currentmember.loginid = current_user)
;

grant select on empyre.ship to :web, :bbs;
