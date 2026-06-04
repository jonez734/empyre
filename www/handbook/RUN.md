# run empyre

$ python -m empyre --databasename=zoid6 --databasehost=127.0.0.1

The `--databasename` and `--databasehost` flags are required so that all
subsystems (including `bbsengine6.notify`) build connection pools against
the correct database. Without them, the notify subsystem falls back to the
`BBSENGINE6_DBNAME` env var (default `bbsengine6`) and a UNIX socket, which
will fail if your database is named `zoid6` or only listens on TCP.
