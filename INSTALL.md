- install pgdg (postgresql) repo into package manager
- install postgresql-server, whatever is default in pgdg
  * https://yum.postgresql.org/repopackages/
  * https://download.postgresql.org/pub/repos/yum/reporpms/F-41-x86_64/pgdg-fedora-repo-latest.noarch.rpm
  * `sudo dnf install postgresql-server postgresql-contrib postgresql`
  * `sudo /usr/bin/postgresql-setup --initdb`
  * `sudo systemctl start postgresql`
  * `sudo systemctl enable postgresql`
  * `sudo -u postgres psql -c 'create role jam superuser login;' template1`
- install and start up oidentd for auth to postgres
  * sudo dnf install oidentd
  * sudo systemctl enable oidentd
  * sudo systemctl start oidentd
  * @TODO: find url for pgdg signing keys

- python database adapter psycopg3: `pip install psycopg psycopg-pool`
- bbsengine6: `pip install {bbsenginewhl}`
- use bbsengine6.con to 
  * use the bootstrap tool which creates the database, tables, roles, and sets permissions
  * create an account which has SYSOP permission
- empyre: `pip install {empyrewhl}`
- run empyre: `python -m empyre`
- https://download.postgresql.org/pub/repos/apt/README


20.04.6 LTS (Focal Fossa)

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo pip install importlib-resources
[~] [9:03pm] [jam@falcon] % sudo mkdir -p /home/jas/.ssh
[~] [9:10pm] [jam@falcon] % sudo chown jas.jas /home/jas/.ssh
[~] [9:10pm] [jam@falcon] % sudo passwd jas
[~] [9:11pm] [jam@falcon] % sudo chown jas.jas -Rv /home/jas/.ssh
changed ownership of '/home/jas/.ssh/jas_id_rsa_2.pub' from root:root to jas:jas
changed ownership of '/home/jas/.ssh/jas_id_rsa_1.pub' from root:root to jas:jas
ownership of '/home/jas/.ssh' retained as jas:jas
