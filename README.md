README for the Hotel Quickly Data Warehouse Hack (`hq-dw`)


## Introduction

`hq-dw` is a collection of `django` configurations to run a data warehouse
behind an `ORM` (Object Relational Mapper).  It depends on the remaining
`django` apps: `hq-stage`, `hq-warehouse` and `hq-hotel-mart`, to perform the
database queries.  `hq-dw` glues together the three apps into a coherent
configuration.


## Table of Contents

1.  [Installation](#install)
    *   [Requirements](#install-req)
    *   [Postgres configuration](#install-conf)
    *   [Create database and user](#install-db)
    *   [Virtual environment](#install-venv)
    *   [Clone the warehouse configuration](#install-wh)
    *   [Install dependencies](#install-deps)
    *   [Install the warehouse packages](#install-pkg)
    *   [Development system](#install-dev)
    *   [Production environment variables](#install-prod)
    *   [Extra notes on a reliable web server](#install-uwsgi)
2.  [Running the Warehouse](#run)
    *   [ETL process](#run-etl)
    *   [Mart API](#run-api)
    *   [Extensions](#run-ext)
3.  [Design](#design)
    *   [Staging area](#desing-stage)
    *   [Warehouse](#design-warehouse)
    *   [Mart](#design-mart)
4.  [Spreading Across Several Machines](#dist)
    *   [Why would you like to distribute?](#dist-why)
    *   [Example setup](#dist-example)
    *   [What would you need to change](#dist-conf)
5.  [Frequent Questions](#faq)
    *   [Why do you use an ORM?](#faq-orm)
    *   [But isn't an ORM slower than stored procedures?](#faq-slow-orm)
    *   [Things are in memory, won't the system be out of memory?](#faq-mem)
    *   [Why Django?](#faq-django)
    *   [Would you use Django in production in a large warehouse?](#faq-prod)
6.  [Copying](#copy)


## Installation  { #install }

The warehouse works on top of other tools, the `RDMS` for a start, we have
certain requirements before the installation can begin.

### Requirements  { #install-req }

We will need the following pieces of software before we can install and run the
warehouse.  These are the basic (system) requirements, further packages will be
installed inside the virtual environment of the warehouse itself.

*   `Postgres 9.x` - A recent version of `postgres` is needed, I am running
   `postgres 9.5` but any `9.x` version shall suffice.

*   `Postgres headers` - On some operating systems the development headers are
    included in a different package (e.g. `postgres-dev` on Debian based
    distros).  The headers are needed to compile the python bindings.

*   `gcc` and `make` - We will compile the `python` bindings for the `postgres`
    database, we need these two to perform this.

*   `Python 3` - We will use `python3`, the newest version of `python` since it
    deals with `utf-8` better than `python2`.  This may not be the default
    version of python on your distro.

*   `virtualenv3` - A python virtual environment for `python3`, not for
    `python2`.  This is often packaged as a separate package by distros, i.e.
    there is one package for `virtualenv2` and one for `virtualenv3`.  OSX has
    no `virtualenv3` equivalent see my [my answer on stack overflow][stov] for
    a workaround on OSX.

*   `git` - To clone the warehouse pieces from `github`.

[stov]: http://stackoverflow.com/questions/38292345/how-to-force-mkproject-virtualenvwrapper-to-use-python3-as-default/

### Postgres configuration  { #install-conf }

First of all we need to install a database.  `Postgres` will be our choice,
there are plethora of way of installing it (OS repositories, `Postgres` own
repositories, compiling from source, etc.) therefore we will not go into detail
on this.  Instead we will make a couple of assumptions about the installation
and allow the reader to change them accordingly to his own `postgres`
installation.  We will assume that:

*   `PGROOT` is `/var/lib/postgres)`.

*   `Postgres` run as the user `postgres` and group `postgres`.

*   We start `postgres` with:

        /usr/bin/pg_ctl -w -t 120 -D /var/lib/postgres/data start

*   We use the default port (`5432`).

*   We use `systemd` to start `postgres` at boot time.

*   We use `rsyslog` as the *Syslog* utility.

A `postgres` database needs to be initialised before it can run.  If you
already have a `postgres` instance running you can ignore this section but at
least skim the configuration example below to check whether you may want to
check some configuration parameters on your instance.

Change into the `postgres` user (this is normally accomplished by `su -
postgres` as root, but configurations vary) and execute:

    initdb --locale en_GB.UTF-8 -E UTF-8 -D /var/lib/postgres/data

You can set your locale to your language but leave the encoding as `UTF-8`.
This is really important since the default encoding will be guessed from the
client if you do not set it, and that is not what you want in most cases.

Assuming that we now have a `postgres` instance we need to configure it.  The
default configuration that comes with `postgres` is normally focused on a
transactional database with lots of updates, this is very different from a
warehouse.  We update `/var/lib/postgres/data/postgresql.conf` with:

    # Assuming that the database runs on the same server,
    # if it not the case this needs to be changed appropriately
    listen_addresses = 'localhost'
    max_connections = 200

    # Just in case (it probably is already enabled by default)
    full_page_writes = on
    track_counts = on

    # We can pump up the memory for buffers and caches
    shared_buffers = 64MB
    work_mem = 16MB
    maintenance_work_mem = 32MB

    # Vacuum shall will be less needed thanks to the fact that there are almost
    # no updates but more needed since we have bigger caches.  Increase its
    # cost but also increase the number of workers.
    vacuum_cost_delay = 20ms
    autovacuum = on
    autovacuum_max_workers = 18

    # Be permisive with deadlocks (no quick updates are needed)
    checkpoint_segments = 6
    deadlock_timeout = 3s

    # Logging for a warehouse needs to be rotated,
    # also enabling syslog is wise since it shall run mostly unattended
    log_destination = 'stderr,syslog'
    logging_collector = on
    log_directory = 'pg_log'
    log_filename = 'postgresql-%a.log'
    log_truncate_on_rotation = on
    log_rotation_age = 1d
    log_rotation_size = 0
    syslog_facility = 'LOCAL3'

    # Use a UTF-8 encoding by default
    # (change apropriately for your language, but keep the UTF-8 encoding)
    lc_messages = 'en_US.UTF-8'
    lc_monetary = 'en_US.UTF-8'
    lc_numeric = 'en_US.UTF-8'
    lc_time = 'en_US.UTF-8'
    datestyle = 'iso, dmy'

You can leave the `postgres` user environment now (or just leave the shell open
since we will need that use again).

Most ditros today use `systemd` therefore starting `postgres` shall be done
with:

    systemctl start postgres.service

But feel free to start it with:

    /usr/bin/pg_ctl -w -t 120 -D /var/lib/postgres/data start

If you are only testing.  In a proper warehouse installation the database will
need to be configured to start under `systemd` since we need it to start at
system boot/restart.

### Create database and user  { #install-db }

Once `postgres` is running create a `django` user with permissions to create
databases.  This user will later create the databases needed.

    $ psql
    postgres=# create user django with createdb password 'password';

Change the *'password'* to something hard to guess if the database can be
accessed from outside.  You need to execute the command as the user `postgres`
(you may need to `su` into the user again).

### Virtual environment  { #install-venv }

Next we will create a virtual environment for the application.  A virtual
environment allows us to install specific `python` packages without the need to
change the current system-wide `python` installation.  Moreover everything ina
virtual environment can be executed as a normal user, no need to be root to
install things (much safer).  Choose a user (that is not root), select a
directory (we will assume `~/warehouse`) and from inside it run:

    virtualenv3 venv

This creates a virtual environment (for `python3`) in `~/warehouse/vnev`.  Next
we need to switch to that environment:

    source ~/warehouse/venv/bin/activate

This alters the paths for `python` binaries and libraries, and also the `PS1`
environment variable to remind you that you are in a virtual environment.  Your
shell shall look along the lines of:

    (venv) [me@machine] $

Everything else that we will be doing during the installation shall be inside
the virtual environment, therefore remember to check your shell to ensure that
you are inside it.

### Clone the warehouse configuration  { #install-wh }

    git clone https://github.com/grochmal/hq-dw.git
    cd hq-dw

### Install dependencies  { #install-deps }

    pip -r requirements.txt

### Install the warehouse packages  { #install-pkg }

    git clone https://github.com/grochmal/hq-stage.git
    cd hq-stage
    pip install .
    cd ..
    git clone https://github.com/grochmal/hq-warehouse.git
    cd hq-warehouse
    pip install .
    cd ..
    git clone https://github.com/grochmal/hq-mart.git
    cd hq-mart
    pip install .
    cd ..

If you need to alter the code (to try different things) use:

    pip install -e .

Instead.

### Development system  { #install-dev }

    cd hq-dw
    export DJANGO_SETTINGS_MODULE=conf.dev
    python manage.py runserver

### Production environment variables  { #install-prod }

    cd hq-dw
    python TODO.py

### Extra notes on a reliable web server  { #install-uwsgi }

A reliable system would need much more.  A reverse proxy and load balancer,
akin of `nginx` and a real webserver, e.g. `uwsgi`.  TODO


## Running the Warehouse  { #run }

TODO

### ETL process  { #run-etl }

    /path/to/script/extract-data.sh
    /path/to/script/load-data.sh

### Mart API { #run-api }

    /path/to/script/load-mart.sh
    python3 manage.py runserver

### Extensions  { #run-ext }

The error fixing in the stage area can be vastly improved.  An HTTP interface
for loading data into batches would be very useful too.

The webserver definitely must not be run with Django's basic webserver.


## Design  { #design }

The first rule of data warehousing is: No matter how well behaved your data
sources are, someone at some point will send you rubbish, be prepared to
recover from that.

Therefore I am treating the data files as external data and assuming that the
data in them is not clean.

A data warehouse is divided into at least three pieces:

1.  A staging area, to which input data is loaded *"as is"*
2.  The warehouse, which have a clear division in *fact* and *dimension* tables
3.  One or more data marts, which use some of the data in the warehouse for
    specific purposes

Now let's see how the HQ specific warehouse divides its work across the three
parts.

### Staging area  { #design-stage }

For each data source a table is created and all columns are set to
VARCHAR(255).  If a piece of data has more than 255 character it is not the
type of data that shall be stored in a data warehouse, we truncate such
columns.

We try to load as much data as possible in the exact same format it comes.  If
a column is empty it will be populated as empty, if it has a space it will
receive a space, if it shall be a number but has letters the letters are
loaded.  This behaviour allows us to fix problematic data inside he staging
area instead of searching for the problematic rows in the input files.

This also allows to design an operator interface to the staging area, in which
an operator would be able to fix problematic rows without the clutter of the
correct rows.

Apart from the columns describing the input data several other status columns
are present in every record in the staging area.  These include several flags
indicating errors and whether the data was uploaded to the warehouse, insert
data and a batch.

The batch is a simple feature that allows for grouping of records together.
This allows for an easy way to delete a big amount of data that was wrongly
inserted and amendments to inserted data before it is processed and uploaded
into the warehouse.

In the HQ warehouse we have a small number of input files (only 3), and batches
are not needed since we never insert into the same table twice.  But the
setting of all columns to VARCHAR(255) allows us to catch several errors
without the need to review the input files.

### Warehouse  { #design-warehouse }

The focus in the warehouse design is on *facts* and *dimensions*, yet, in the HQ
warehouse, that has already been done for us.  Another important detail is
database configuration, since queries may run for a long time.  In the HQ
warehouse the *date/time* dimension is not present, therefore dates can be
found in tables.  In a real warehouse the *date/time* dimensions would be the
most used dimension.

Database configuration was outlined above in [Installation](#install), and it
serves mostly the warehouse.  If the warehouse grows and the staging area and
mart are moved to different server instances the configuration for the
warehouse shall be kept.

The data in the warehouse can be assumed to be correct.  If data is incorrect
there is a problem with the procedure of retrieving it from the staging area.
The retrieval procedure shall only accept row in the staging area that are
correct and can build correct rows in the warehouse, all incorrect rows are
marked as such in the staging area and never reach the warehouse.

### Data Mart  { #design-mart }

The data mart is populated from the warehouse, therefore we can assume that 
TODO


## Spreading across several machines { #distributed }

TODO

### Why would you like to distribute?  { #dist-why }

The warehouse became too big to run on a single machine.

### Example setup  { #dist-example }

`uwsgi` is really needed here.

### What would you need to change  { #dist-conf }

Three different database servers.  TODO


## Frequent Questions  { #faq }

A FAQ is a list of questions and answers that allow for the explanation of
specific decisions that would be difficult to fit in any other section.  The
following list is an excerpt of decisions about technologies used and reasons
why I digressed from the original proposal:

### Why do you use an ORM?  { #faq-orm }

I saw too many data warehouses that were impossible to debug.  Since stored
procedures are very quick using them to perform the load of data from the stage
tables to the warehouse tables (or warehouse to mart) looks like a good idea.
But it isn't!  Stored procedures have limited functionality on how to deal with
errors.  The original purpose of errors in stored procedure is to fail the
entire procedure and rollback.

Rollback the entire procedure in a warehouse is not acceptable.  A warehouse
will almost always be loaded with at least one row of data that is slightly
incorrect, and re-running the entire load procedure over and over is time
consuming.  Instead the procedure must load all correct data and log the
incorrect data in one go.  To perform that the typical workaround are insert
triggers.  The insert triggers call another stored procedure to perform the
logging of the error.  But the logging may fail as well, therefore another
insert trigger is often present for the logging.  Which again calls another
stored procedure.

This becomes even more pronounced when the stage, warehouse and mart databases
are on separate instances.  And, at some point a every data warehouse will grow
big enough to need to separate its pieces into different instances.

It is a vicious hell of procedure inserting into a table with triggers, which
call another procedure, which inserts into a table with triggers, which call
another procedure.  Basically exponential complexity.

An `ORM` (Object Relational Mapper) allows me to use a higher level language
and I can process all required tables in a single, well defined, procedure.  In
a higher level language I can not only deal with errors cleanly but also insert
the errors in the proper error tables in a standardised way (a library call).

Moreover, an `ORM` can cleanly communicate and work with different instances of
a database, one thing that stored procedures cannot do.  Stored procedures are
limited to the database instance they're stored in.

### But isn't an ORM slower than stored procedures?  { #faq-slow-orm }

At first sight *yes*.  An `ORM` will read data into memory and, only after
processing it, it will write it back to disk.  Loading the data into memory may
happen over the network, making it even slower.

On the contrary a stored procedure makes a pipeline: disk `->` memory `->`
disk, which is very fast.  Yet, on a reasonable warehouse data is never
processed by a single stored procedure, neither it is processed inside a single
instance of a database.  Therefore the overhead of sending the data through the
network and keeping it in memory during the processing is just the same with
stored procedures once a data warehouse grows.

### Things are in memory, won't the system be out of memory?  { #faq-mem }

If you code things badly *yes*.  The division between *facts* and *dimensions*
is very important when constructing the warehouse, even more important if the
processing happens in an `ORM`.  Joins need to be cached, and will be cached by
the database if the queries are using a certain table repeatedly.  The only
difference with an `ORM` is that we have the power to decide which rows to
cache and which do not.

A database does not always perform the best caching decisions, moreover the
cache size is limited.  If we control the queries, and cache *dimension* data,
we can use a more effective cache.

Caching the *factis* on the other hand would leave us out of memory quickly.  A
database that has a well defined cache size just writes down the cached pages
once a record is not requested anymore.  That is a good caching strategy for
*facts*, and we want to keep that part of the cache in he database.

In summary we can optimise the caching strategy to our needs: *dimensions* in
the `ORM` *facts* in the database.  And doing it correctly will both: not
leave the system where the `ORM` is running out of memory, and make a better us
of database cache.

### Why Django?  { #faq-django }

TODO

### Would you use Django in production in a large warehouse?  { #faq-prod }

Probably not.


## Copying  { #copy }

Copyright (C) 2016 Michal Grochmal

This file is part of `hq-dw`.

`hq-dw` is free software; you can redistribute and/or modify all or parts of it
under the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

`hq-dw` is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

The COPYING file contains a copy of the GNU General Public License.  If you
cannot find this file, see <http://www.gnu.org/licenses/>.

