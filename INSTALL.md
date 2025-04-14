- install pgdg (postgresql) repo into package manager
- install postgresql-server, whatever is default in pgdg
  * https://yum.postgresql.org/repopackages/
  * https://download.postgresql.org/pub/repos/yum/reporpms/F-41-x86_64/pgdg-fedora-repo-latest.noarch.rpm
  * `sudo dnf install postgresql-server postgresql-contrib postgresql`
  * `sudo /usr/bin/postgresql-setup --initdb`
  * `sudo systemctl start postgresql`
  * `sudo systemctl enable postgresql`
  * `sudo su - postgres` then 'psql -c 'create role jam superuser login;' template1

- python database adapter psycopg3: `pip install psycopg psycopg-pool`
- bbsengine6: `pip install {bbsenginewhl}`
- use bbsengine6.con to 
  * use the bootstrap tool which creates the database, tables, roles, and sets permissions
  * create an account which has SYSOP permission
- empyre: `pip install {empyrewhl}`
- run empyre: `python -m empyre`
