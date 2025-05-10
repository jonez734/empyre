from bbsengine6 import io, member, util, database

from .. import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None


def _merccount(args, **kwargs):
    sql:str = "select count(*) from empyre.mercs"
    dat:tuple = ()

import random

def generate_merc_teams_with_costs(min_members=10, max_teams=10, max_members_per_team=50, min_cost_per_member=10, max_cost_per_member=50):
    """
    Generate a random number of mercenary teams with a random number of members and calculate their total cost.
    
    Args:
        min_members (int): Minimum number of members per team.
        max_teams (int): Maximum number of teams.
        max_members_per_team (int): Maximum number of members in a team.
        min_cost_per_member (int): Minimum cost per member.
        max_cost_per_member (int): Maximum cost per member.

    Returns:
        dict: A dictionary where keys are team names and values are dictionaries with member count and total cost.
    """
    # Generate a random number of teams
    num_teams = random.randint(1, max_teams)
    
    # Create teams with random members and costs
    teams = {}
    for i in range(1, num_teams + 1):
        num_members = random.randint(min_members, max_members_per_team)
        cost_per_member = random.randint(min_cost_per_member, max_cost_per_member)
        total_cost = num_members * cost_per_member
        teams[f"Team_{i}"] = {
                    "members": num_members,
                    "cost_per_member": cost_per_member,
            "total_cost": total_cost
        }
    
    return teams

# Example usage
#merc_teams = generate_merc_teams_with_costs()
#for team, details in merc_teams.items():
#    print(f"{team}: {details['members']} members, {details['cost_per_member']} coins per member, total cost {details['total_cost']} coins.")

### Explanation:
#1. **Added Parameters**:
#   - `min_cost_per_member`: Minimum cost per member (default is 10 coins).
#   - `max_cost_per_member`: Maximum 
#cost per member (default is 50 coins).
#2. **Calculation**:
#   - Each team's cost is calculated as `num_members * cost_per_member`.

def main(args:object, player=None, **kwargs):
    util.heading("mercs")
    cur = kwargs.get("cur", None)
    if cur is None:
        with database.connect(args) as conn:
            with database.cursor(conn) as cur:
                merccount = _merccount(cur)
    else:
        merccount = _merccount(cur)
    if merccount == 1:
        io.echo(f"{{var:labelcolor}}there is {{var:valuecolor}}1 merc team")
    elif merccount == 0:
        io.echo(f"{{var:labelcolor}}there are {{var:valuecolor}}no merc teams")
    else:
        io.echo(f"{{var:labelcolor}}there are {{var:valuecolor}}{merccount} merc teams")
    if io.inputboolean("{{var:promptcolor}}generate teams? {{var:optioncolor}}[yN]{{var:promptcolor}}: {{var:inputcolor}}", "N") is True:
        merc_teams = generate_merc_teams_with_costs()
    for team, details in merc_teams.items():
        print(f"{team}: {details['members']} members, {details['cost_per_member']} coins per member, total cost {details['total_cost']} coins.")
