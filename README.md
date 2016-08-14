README for the Hotel Quickly Data Warehouse Hack (`hq-dw`)


## Introduction

`hq-dw` is a collection of `django` configurations to run a data warehouse
behind an `ORM` (Object Relational Mapper).  It depends on the remaining
`django` apps: `hq-stage`, `hq-warehouse` and `hq-hotel-mart`, to perform the
database queries.  `hq-dw` glues together the three apps into a coherent
configuration.

The final warehouse is quite different from the assignment at [bi-dev][bidev].
There are a couple of reasons for it.  First of all this is the first time I
could make *all* design decisions for a warehouse, and I always wanted to try
building a warehouse purely through an ORM.  Therefore I have spent much more
time on this than one would expect.  In a certain way, after seeing a lot of
bad warehouse designs, I just wanted to check is such a warehouse design
(through an ORM) will work out.  And I'm quite pleased with the result.

[bdev]: https://github.com/HQInterview/BI-developer

A second reason for why the warehouse looks as it does is that we have 6 hours
of difference between London and Bangkok.  In such conditions I preferred to
follow Godwin's Law (see note below) and make all decisions myself.  Some key
differences are:

*   The staging are loads the data from the CSV files as if they could be
    dirty.  This follows a more real world scenario where we cannot ever be
sure if a data provider will not send complete garbage.

*   The staging area and the warehouse are different databases, not schemas.
    This allows for distributing the warehouse better, and possbily configure
both databases in different ways.

*   The API endpoint is made against a data mart.  And the data mart is in yet
    another database.   The data mart can be reloaded out of the warehouse to
contain only fresh data (making the queries faster).

*   The API endpoint require an extra argument, the time of the query.  This is
    needed because most of the data we have is for 2015.  Rather than making
the query based on the current date and time we allow for queries that happened
in the past.  In a real world scenario we should match against the time the
query is made against the system but that is not possible with historical data.

*   The warehouse tries to make up for missing data with several heuristics.
    For example, we match foreign exchanges that we cannot find for a certain
date against the most recent foreign exchanges for the given currencies.  We
also try to match hotel offers based on the duration of stay if we cannot
exactly match check-in and check-out dates.

*   There is one extra API, an API to load data into the staging area.  It
    probably does not work since I have not tested it, but it is a good feature
to have.

*   There is a web interface to all records in all databases.  This allows for
    checking the correctness of rows easier and quicker than writing SQL.

*   A web interface to the staging area allows to update records, notably
    records that were marked as erroneous during data cleansing.  The actual
form submit button is not provided (but trivial to add) since I'm hosting this
code on a server that uses no authentication at all.

*   The ETL process is much more strict.  We do not first load the data from
    the staging area into the warehouse and then check for errors.  We try to
find all errors during the loading and never add erroneous record to the
warehouse.  The checking code is also much simpler in python than it would be
in SQL.

Note: Godwin's Law (actually Ward Cunningham's Law) says that people are
better and faster at correcting than at answering an inquiry.  In other words,
asking a question is less effective than providing a wrong answer.  Therefore I
just went and made decisions and assumptions as I went through the coding.  In
general the code has a lot of documentation strings and comments explaining
quirky parts.  See also the FAQ on how to understand Django code.


## Table of Contents

1.  |0x100| Installation
    *   |0x101| Quick Start (TL;DR)
    *   |0x102| Requirements
    *   |0x103| Postgres configuration
    *   |0x104| Create database and user
    *   |0x105| Virtual environment
    *   |0x106| Clone the warehouse configuration
    *   |0x107| Install dependencies
    *   |0x108| Install the warehouse packages
    *   |0x109| Install the development system
    *   |0x10a| Configuration
    *   |0x10b| Production environment variables
    *   |0x10c| Extra notes on a reliable web server
2.  |0x200| Running the Warehouse
    *   |0x201| ETL process
    *   |0x202| Mart API
    *   |0x203| Extensions
3.  |0x300| Design
    *   |0x301| Staging area
    *   |0x302| Warehouse
    *   |0x303| Mart
4.  |0x400| Spreading Across Several Machines
    *   |0x401| Why would you like to distribute?
    *   |0x402| Example setup
    *   |0x403| What would you need to change
5.  |0x500| Frequent Questions (FAQ)
    *   |0x501| I expected to see SQL and got a Web Framework, what gives?
    *   |0x502| OK, but why do you use an ORM?
    *   |0x503| But isn't an ORM slower than stored procedures?
    *   |0x504| Things are in memory, won't the system be out of memory?
    *   |0x505| Why Django?
    *   |0x506| Would you use Django in production in a large warehouse?
    *   |0x507| I do not know Django, how do it check the DB optimisation?
    *   |0x508| Why do you believe that optimisation by caching is better?
    *   |0x509| There are a lot of quirks with python 3, why did you use it?
    *   |0x50a| That is quite a lot of code, how long did it take?
6.  |0x600| Copying


## |0x100| Installation

The warehouse works on top of other tools, the `RDMS` for a start, we have
certain requirements before the installation can begin.  We will need a working
`postgres` database and a working `python3` environment.  Best effort has been
performed to try to make the code database and operating system agnostic, but
it has only been tested with `postgres` and `sqlite` and only on Linux (`Arch`
and `CentOS`).

Note that, if you are going to use it on a new virtual machine, the code is
much easier to install on an OS that uses `python3` as the default python.
Arch Linux (and all its forks), Fedora, Gentoo, and Ubuntu (I believe) are the
distros that use `python3` by default (but consider *not* using Ubuntu, since
it places things in non-standard places and I cannot be bothered to test that).
Distros that use `python2` by default will require a couple of tricks to create
`python3` virtual environments: If you must use such a distro you may wish to
use `pip3` to install `virtualenv` and then manually softlink the created
script to `virtualenv3`.

### |0x101| Quick Start (TL;DR)

A full explanation of the install procedure will follow later.  Just note that
`python3` and `pip3` may be named just `python` and `pip` on distros that use
`python3` by default (that is the case with Arch Linux).

Install:

*   `postgres` and `postgres-dev` with your package manager.
*   `gcc` with you package manager.
*   `python3` and `pip3` with your package manager.
*   `vitualenv3` with your package manager or using `pip3`.
*   `git` with you package manager.

Create a couple of databases that will hold the data:

    $ su - postgres
    $ psql
    =# create user django with password 'password';
    =# create database dev_auth with owner django encoding 'utf-8';
    =# create database dev_stage with owner django encoding 'utf-8';
    =# create database dev_warehouse with owner django encoding 'utf-8';
    =# create database dev_hotel_mart with owner django encoding 'utf-8';

Install the warehouse packages (as any user you want, not `root` please):

    mkdir testhq
    cd testhq
    virtualenv3 venv-hq
    source venv-hq/bin/activate
    git clone https://github.com/grochmal/hq-dw.git
    git clone https://github.com/grochmal/django-hq-stage.git
    git clone https://github.com/grochmal/django-hq-warehouse.git
    git clone https://github.com/grochmal/django-hq-hotel-mart.git
    cd hq-dw/hq-dw
    export DJANGO_SETTINGS_MODULE=conf.dev
    export HQ_DW_CONF_PATH=`pwd`
    pip install -r requirements.txt
    cd ../../django-hq-stage/
    pip install -e .
    cd ../django-hq-warehouse/
    pip install -e .
    cd ../django-hq-hotel-mart/
    pip install -e .

The full code (including the dependencies) uses about 60MBs of disk space.
Next, start the development webserver (we will talk about a production
webserver later):

    cd ../hq-dw/hq-dw/
    python manage.py migrate --database default
    python manage.py migrate --database stage
    python manage.py migrate --database warehouse
    python manage.py migrate --database hotel_mart
    python manage.py runserver
    # go to http://localhost:8000/

Leave the development server running in the shell and open a new one.  We will
need to enter the virtual environment once again, and we will get the files to
load.

    cd testhq
    source venv-hq/bin/activate
    export DJANGO_SETTINGS_MODULE=conf.dev
    export HQ_DW_CONF_PATH=`pwd`/hq-dw/hq-dw
    mkdir data
    cd data
    wget -O hq-currency.csv https://s3-ap-southeast-2.amazonaws.com/hq-bi/bi-assignment/lst_currency.csv
    wget -O hq-forex.csv https://s3-ap-southeast-2.amazonaws.com/hq-bi/bi-assignment/fx_rate.csv
    wget -O hq-offer.csv https://s3-ap-southeast-2.amazonaws.com/hq-bi/bi-assignment/offer.csv

Finally, run the warehouse scripts (which should be in the PATH inside the
virtual environment) to ETL the data all the way to the mart.  This procedure
takes a considerable amount of time:

    hqs-load-table -f ./hq-currency.csv -t currency
    hqs-load-table -b 1 -f ./hq-forex.csv -t exchange-rate
    hqs-load-table -b 1 -f ./hq-offer.csv -t offer
    hqw-checkout-batch -v -b 1
    hqm-pop-hours -v -y 2016
    hqm-reload -v

Test the `API` endpoint.  The endpoint uses HTTP codes as error indicators
therefore use curl's `-i` to print the HTTP headers of the response.

    curl -i 'http://localhost:8000/api/?queryat=2016-06-07T11&hotelid=169&checkindate=2016-06-25&checkoutdate=2016-06-26'

I have developed and tested the code on Arch Linux, using the most recent
packages available on that OS.  The above should work on that distro, yet to
understand possible quirks with the installation please read forward.

### |0x102| Requirements

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
there is one package for `virtualenv2` and one for `virtualenv3`.  OSX has no
`virtualenv3` equivalent see my [answer on stack overflow][stov] for a
workaround on OSX.

*   `git` - To clone the warehouse pieces from `github`.

[stov]: http://stackoverflow.com/questions/38292345/how-to-force-mkproject-virtualenvwrapper-to-use-python3-as-default/

### |0x103| Postgres configuration

First of all we need to install an `RDBMS`.  And `Postgres` is our choice,
there are plethora of way of installing it (OS repositories, `Postgres` own
repositories, compiling from source, etc.) therefore we will not go into detail
on this.  Instead we will make a couple of assumptions about the installation
and allow the reader to change them accordingly to his own `postgres`
installation.  We will assume that:

*   `PGROOT` is `/var/lib/postgres)`.

*   `Postgres` runs as the user `postgres` and group `postgres`.

*   We start `postgres` with (or an equivalent command):

        /usr/bin/pg_ctl -w -t 120 -D /var/lib/postgres/data start

*   We use the default port (`5432`).

*   We use `systemd` to start `postgres` at boot time.

*   We use `rsyslog` as the *Syslog* utility (this is only needed for a
    production environment).

A `postgres` database needs to be initialised before it can run.  If you
already have a `postgres` instance running you can safely ignore this section.
Yet, you may want to at least skim the configuration example below to check
whether you may want to change some configuration parameters on your instance.

Change into the `postgres` user (this is normally accomplished by `su -
postgres` (often as root, but configurations vary) and execute:

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
    # (give more on bigger machines)
    shared_buffers = 64MB
    work_mem = 16MB
    maintenance_work_mem = 32MB

    # Vacuum shall less needed thanks to the fact that there are almost
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

Most distros today use `systemd` therefore starting `postgres` shall be done
with (as root):

    systemctl start postgres.service

But feel free to start it with:

    /usr/bin/pg_ctl -w -t 120 -D /var/lib/postgres/data start

If you are only testing.  In a proper warehouse installation the database shall
configured to start under `systemd` since we want it to start at system
boot/restart.

### |0x104| Create database and user

Once `postgres` is running create a `django` user (or some user name that you
feel more comfortable with, but you will need to change the warehouse
configuration to use that user).  Also create the databases that will be used
by the warehouse (yes, there are several of them):

    $ psql
    =# create user django with createdb password 'password';
    =# create user django with password 'password';
    =# create database dev_auth with owner django encoding 'utf-8';
    =# create database dev_stage with owner django encoding 'utf-8';
    =# create database dev_warehouse with owner django encoding 'utf-8';
    =# create database dev_hotel_mart with owner django encoding 'utf-8';

Change the *'password'* to something hard to guess if the database can be
accessed from outside.  You need to execute the command as the user `postgres`
(you may need to `su` into the user again).  If you change the password, you
*will* need to change the warehouse configuration to use the new password.

You can now leave the `postgres` user environment now.

### |0x105| Virtual environment

Next we will create a virtual environment for the application.  A virtual
environment allows us to install specific `python` packages without the need to
change the current system-wide `python` installation.  Moreover everything in a
virtual environment can be executed as a normal user, no need to be root to
install things (much safer).

Choose a user to install the warehouse as (a user that preferably is not root),
select a directory (we will assume `~/warehouse`) and from inside it run:

    virtualenv3 venv

There are some quirks with python virtual environment thanks to the
incompatibilities between `python2` and `python3`.  I strongly recommend using
a distro that uses `python3` as the default `python`, in which case you can use
`virtualenv` instead of `virtualenv3`.  Yet, if your distro does not use
`python3` by default you will need to install `virtualenv` though `pip3`, and
then make sure that the `python3` interpreter is used to run the `virtualenv`
script.  For example instead of:

    virtualenv3 env

You will need to perform:

    python3 `which virtualenv` env

Once we have a virtual environment (for `python3`) in `~/warehouse/vnev`.  Next
we need to switch to that environment:

    source ~/warehouse/venv/bin/activate

This alters the paths for `python` binaries and libraries, and also sets the
`PS1` environment variable to remind you that you are in a virtual environment.
Your shell shall look along the lines of:

    (venv) [me@machine] $

Everything else that we will be doing during the installation shall be from
inside the virtual environment, therefore remember to check your shell to
ensure that you are inside it.

### |0x106| Clone warehouse configuration

Assuming we are inside `~/warehouse` let us get the warehouse configuration
from `github` and go in there:

    git clone https://github.com/grochmal/hq-dw.git
    cd hq-dw/hq-dw

The `conf` directory contains the configuration and it has a hierarchy as
follows:

    base.py
    |
    +-- dev.py
    |   |
    |   +--dev_sqlite.py
    |
    +-- prod.py

That means that `dev.py` inherits all settings from `base.py` and
`dev_sqlite.py` inherits from `dev.py` and also from `base.py`.  Either
`dev.py`, `dev_sqlite.py` or `prod.py` can be used as full configuration files
(`base.py` cannot be used).

For a basic install we will use `dev.py`.  We will discuss how to transform the
development install into a production ready warehouse later.  Let us export a
couple of environment variables so that other packages will be able to find our
configuration.  Assuming that we are inside `~/warehouse/hq-dw//hqdw`, perform:

    export DJANGO_SETTINGS_MODULE=conf.dev
    export HQ_DW_CONF_PATH=`pwd`

Note: If you are using a different postgres user than `django` and/or a
different password, edit `conf/dev.py`.  The lines that need to be edited shall
be self explanative.

### |0x107| Install dependencies

The warehouse depends on a couple of third party packages, which we will need
to install inside the virtual environment.  One of the requirements is
`psycopg2` (python bindings for the postgres database), we will need `gcc` and
headers for the postgres database to be used.

Assuming that we are at `~/warehouse/hq-dw` we need to perform:

    pip -r requirements.txt

Make sure that you are inside the virtual environment, otherwise it will
complain that it cannot install the packages into `/usr/` (and we do not want
to dirty our OS).

### |0x108| Install the warehouse packages

Now that we have all requirements and configuration let's install the warehouse
packages.  Each repository contains a python package that can be installed with
`pip` (or with `easy_install`).  Make sure you are inside the virtual
environment, then, assuming you are in `~/warehouse`, perform:

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

A clever trick with `pip` is that it can install softlinks instead of the
actual files into the virtual environment.  This way if something goes wrong
you can change the code directly in the repository (i.e. you do not need to
search where the code was installed).  To achieve this use:

    pip install -e .

Instead of

    pip install .

The editable package option is acceptable for a development environment.  In
production it is discouraged since it makes the code load slightly slower.

### |0x109| Install the development system

We have the databases configured the warehouse installed and now we only need
to create the schemas in the databases.  Make sure you are in the virtual
environment and that `DJANGO_SETTINGS_MODULE` is set to `conf.dev`, then,
assuming that you are at `~/warehouse` perform:

    cd hq-dw/hq-dw/
    python manage.py migrate --database default
    python manage.py migrate --database stage
    python manage.py migrate --database warehouse
    python manage.py migrate --database hotel_mart

That will build the correct tables and indexes in each database.  Now we can
run the webserver and enjoy our installed warehouse.  From the same environment
do:

    python manage.py runserver

And it will run a development server at http://localhost:8000 , where you shall
go next.  The development server will block the shell session, a more suitable
webserver that can be used in production is discussed in the next sessions.
Leave the development server running or remember how to start it for when it is
needed.  The webserver does not need to be running to run the ETL process, yet
it must be started from the python virtual environment.

This is as far as you need to go to install a test warehouse.  The two
following sections are a discussion of configuration options that may be used
for a production system.  But wait all tables are still empty!  To actually run
the ETL process jump forward to the *Running the Warehouse* section.

### |0x10a| Configuration

The development warehouse is pre-configured, yet several configuration
parameters can be changed to suit needs.  First of all, the warehouse uses four
different databases:

*   `default`: Contains the authentication information and `Django` session
    management.

*   `stage`: The staging area of the warehouse, contains dirty data (containing
    errors) before cleaninsing.

*   `warehouse`: Actual warehouse for querying, stores clean data.

*   `hotel_mart`: Data mart for the best price query.

These databases, together with the description of the connection can be found
in the `DATABSES` variable in the configuration.

In several batch jobs we commit several record at once to the database.  This
speeds up the write speed but requires memory to hold the records before the
commit.  On a machine with a lot of memory you can increase it, the variable
name in the configuration and the default are:

    HQ_DW_COMMIT_SIZE = 1024

We also have a default price for a day in any hotel.  In a real world scenario
we would have the prices for the hotels.  But, since we do not have the hotel
data, we just calculate that if we do not match any offer we just give a price
of number of days times the following (in the default currency):

    HQ_DW_DAY_PRICE = 100.0
    HQ_DW_DEFAULT_CURRECNY = 'USD'

The last important variable in the configuration file is `ALLOWED_HOSTS`.  For
the development warehouse its setting does not matter, but for a production
system it is very important.  We talk about it below.

### |0x10b| Production environment variables

To build a production system we need several other pieces of software.  For a
start the webserver that comes with `Django` is not fast enough or reliable
enough for a production environment.  We are also using default passwords, and
these passwords are available at `github` for anyone to see.  That's all pretty
bad.

How you deploy your production system is up to you (the next section discusses
one possible scenario).  Yet, how to change the default passwords, and not
include them in clear text in files you may submit to a code repository can be
done as using environment variables.  For an example `conf/prod.py` is
included, using that file as the configuration (by placing `conf.prod` inside the
`DJANGO_SETTINGS_MODULE` environment variable) you need to set the following
environment variables to use as configuration parameters.

*   `HQ_DW_SECRET_KEY`: A byte string, can be anything but must remain secret.
*   `HQ_DW_AUTH_NAME`: The database user for the webserver database.
*   `HQ_DW_AUTH_PASS`: The password for the webserver database user.
*   `HQ_DW_WAREHOUSE_NAME`: Database user for the warehouse database.
*   `HQ_DW_WAREHOUSE_PASS`: Password for the warehouse user.
*   `HQ_DW_STAGE_NAME`: Database user for the stage database.
*   `HQ_DW_STAGE_PASS`: Password of the stage user.
*   `HQ_DW_HOTEL_MART_NAME`: Database user for the hotel data mart.
*   `HQ_DW_HOTEL_MART_PASS`: Password of the data mart user.

Note that the users of the four databases doe not need to be the same.  Below
we explain how to distribute the system and use different database servers for
each database.  Also, note that the default names of the databases in `prod.py`
is different from the database names in `dev.py`.  You need to create these
database on the postgres instance they are meant to be run (or change their
names in the configuration).

### |0x10c| Extra notes on a reliable web server

First of all we need a real webserver in front of the warehouse if we are going
to expose the web function (e.g. correction of errors in the staging area) to
operators.  Apache, nginx are some options, apache can run a django based
application with `mod_wsgi`, whilst nginx need a WSGI webserver to serve the
django based application.  One option of a WSGI webserver is `uwsgi`.

In a real world scenario we would also likely need a cache on the reverse
proxy.  Yet, how to deploy the system is again a matter of taste.  What is
important for the warehouse is that it needs to know what `Host:` header to
expect.  In the configuration file the `ALLOWED_HOSTS` variable needs to be set
to a list of all `Host:` headers that the warehouse may expect.  For example:

    ALLOWED_HOSTS = [ 'warehous.hq.com' , 'dw.hq.com' ]

Requests with a different `Host:` header will be rejected.  Wildcards are
allowed therefore you could set it to `[ '*' ]`, but that would be horrible
from a security standpoint.


## |0x200| Running the Warehouse

We have an installed warehouse, and the core of a warehouse is its ETL process.
We also have the data mart installed and running and API.  This section discuss
how the ETL process can be run, how the data mart can be populated and how the
API is accessed.

Everything needs to be performed from the python virtual environment we did
setup during the installation.  Also, we need the environment variables we set
during the installation.  If you followed the installation instructions above
you shall be able to enter the virtual environment and set the environment
variables by doing the following:

    source ~/warehouse/venv/bin/activate
    export DJANGO_SETTINGS_MODULE=conf.dev
    export HQ_DW_CONF_PATH=~/warehouse/hq-dw/hq-dw

If you are using a different directory than `~/warehouse` modify the above
lines accordingly.  In theory any user that has read access to the virtual
environment can run the ETL process but it is better to use the user that
installed the warehouse, for consistency.

Note: the virtual environment did set the `PATH` variable for us, therefore the
commands in this section are in the execution path.  If you cannot find a
command cross check if you are actually inside the virtual environment.

### |0x201| ETL process

The ETL process consists of loading the CSV files into the tables in the
staging area and then loading the warehouse from the staging area.  We start by
getting the files:

    cd ~/warehouse
    mkdir data
    cd data
    wget -O hq-currency.csv https://s3-ap-southeast-2.amazonaws.com/hq-bi/bi-assignment/lst_currency.csv
    wget -O hq-forex.csv https://s3-ap-southeast-2.amazonaws.com/hq-bi/bi-assignment/fx_rate.csv
    wget -O hq-offer.csv https://s3-ap-southeast-2.amazonaws.com/hq-bi/bi-assignment/offer.csv

To load each file we use `hqs-load-table`, it load the CSV file into the
relevant table in the staging area.  The loaded data is assigned a batch,
batches are used to group data together when uploading to the warehouse.  When
you run `hqs-load-table` it will print the batch it used, you can also give it
the `-b` parameter to suggests a batch number to use.  For example we can
perform the following:

    $ hqs-load-table -f ./hq-currency.csv -t currency
    ...
    Batch: [ 1 ]
    $ hqs-load-table -b 1 -f ./hq-forex.csv -t exchange-rate
    $ hqs-load-table -b 1 -f ./hq-offer.csv -t offer

This will reuse batch number 1 for all data loaded from the three CSV files.
The full set of flags used by `hqs-load-table` can be found on the [github of
the staging area package][stag].

[stag]: https://github.com/grochmal/django-hq-stage

Next we can load the batch into the warehouse.  To perform this we use
`hqw-checkout-batch` with the batch number was printed by `hqs-load-table`, as
follows:

    hqw-checkout-batch -v -b 1

The `-v` makes the call verbose.  Since it may be a rather long running command
it might be useful to see the verbose output.  The full set of flags can be
seen on the [github of the warehouse package][ware].

[ware]: https://github.com/grochmal/django-hq-warehouse

Once the load into the warehouse was attempted erroneous data in the staging
area was marked as *in error*, and the fields that were considered to hold
erroneous data were noted.  To print a list of erroneous rows in the staging
area you can call `hqs-print-errors`, the script will output URLs that point to
the records on the web interface of the warehouse.  You need to run
`hqs-print-errors` on each table separately, fore example:

    hqs-print-errors -t currency
    hqs-print-errors -t exchange-rate
    hqs-print-errors -t offer

If the web interface is running you can follow the URL in a browser, correct
the given data and submit the form (the submit button is currently not
present).  Or, if the row is deemed unsalvageable, you can mark the error as
ignored.

After correcting the errors you can reload the batch with `hqw-checkout-batch`
(the rows already loaded will not be reloaded, just the ones that could not be
loaded).  Or you can use `hqw-checkout-table` to load only the erroneous rows
in a single table, for example:

    hqw-checkout-table -t offer

The cycle of fixing the errors and attempting load into the warehouse can be
attempted as many times as needed, until the row is inserted into the warehouse
correctly.

### |0x202| Mart API

The data mart is meant to be an API endpoint that processes the query as fast
as it can.  To speed up the mart we can define the time frame it is meant to
server, i.e. we load the mart only with a fraction of the data from the
warehouse.  This makes sense since the majority of the data in the warehouse is
historical data whilst the mart serves real time queries on rather new data.

To define a time frame for the mart you call `hqm-pop-hours`, for example:

    hqm-pop-hours -tv -y 2015
    hqm-pop-hours -v -y 2016

Note that `-t` will truncate the tables, allowing for the mart to be reloaded
with completely fresh data.  The command used loaded all of 2015 and 2016 as
viable times for offers.  Any offer that is not valid during that period will
not be loaded and any offer that is valid only partially during that period is
loaded partially.

To load offers (and currencies) and build the caches (links between offers and
validity times) you need to call `hqm-reload`.  For example:

    hqm-reload -v

The full set of flags for `hqm-pop-hours` and `hqm-reload` can be seen on the
[github of the hotel mart package][mart].

[mart]: https://github.com/grochmal/django-hq-hotel-mart

The mart may take some time to load, yet more than one mart can be configured.
Therefore if a new mart for 2016 and 2017 needs to be loaded, it can be done
whilst the current mart is running.  Later a switch between marts can be
performed.

The API itself is available when the web interface is running, in a production
environment where the API needs to be fast a real webserver is needed.  The API
is queries with a `GET` requests, with the following arguments:

*    `queryAt`: The moment in time the query is made, this is needed because we
     do not have data for the current time. In a real world situation the mart
API would use the current date and time but it is not possible with historical
data. The argument is an ISO data followed by T and a two digit hour (e.g.
2015-11-11T11 is November the 11th, 2015, at 11AM).

*    `hotelId`: The hotel for which we are checking prices, it is an integer
     value.

*    `checkinDate`: An ISO 8601 date, the day for which we are planning to
     start our stay at the hotel.

*   `checkoutDate`: And ISO 8601 date, the last day of our stay.

One way to test the API is to call it using the `curl` program, fore example:

    curl -i 'http://localhost:8000/api/?queryat=2016-06-07T11&hotelid=169&checkindate=2016-06-25&checkoutdate=2016-06-26'

The API returns errors as HTTP codes therefore the `-i` in the `curl` call is
useful (it prints the HTTP headers of the response).

### |0x203| Extensions

Compared to the required warehouse we have a some extended functionality.  Some
of it is just an extension of what the original design proposes other parts are
completely new, here we shortly discuss the differences. After that we discuss
what would need be improved further in the current warehouse.

The web interface for all records and notably for error correction is much
better than writing SQL to try to fix bad data.  SQL is not meant to be used as
a cherry picking update language, more often than not a typo in SQL produces
problems (e.g. "delete from table <Enter>... oh shiiit!").

An API lo load the data into the staging area using `POST` is available but
probably does not work.  This API would allow for automation for data
providers, yet, to be able to work as such, the API needs several improvements.
Currently the load API can only receive single items, we would need to define a
maximum number of items per request and a proper batch management.

The `hqs-print-errors` script is a dirty hack.  In reality we should have that
as part of the web interface, i.e. we should not need to run the script but
instead have a screen that already presents all (non-ignored) errors to us.
This is actually an easy improvement to do.

One last thing that is certainly needed in the current warehouse is a proper
logging system.  The current `yield+print` logging is reaching its limits,
anything more complex than what we have will overstretch the logging.


## |0x300| Design

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

### |0x301| Staging area

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
are not really needed since we never insert into the same table twice.  But the
setting of all columns to VARCHAR(255) allows us to catch several errors
without the need to review the input files.

### |0x302| Warehouse

The focus in the warehouse design is on *facts* and *dimensions*, yet, in the
HQ warehouse, that has already been done for us.  Another important detail is
database configuration, since queries may run for a long time.  In the HQ
warehouse the *date/time* dimension is not present, therefore dates can be
found in tables.  In a real warehouse the *date/time* dimensions would be the
most used dimensions.

Database configuration was outlined above in the Installation section, and it
serves mostly the warehouse.  If the warehouse grows and the staging area and
mart are moved to different server instances the configuration for the
warehouse database instance shall be kept.

The data in the warehouse can be assumed to be correct.  If data is incorrect
there is a problem with the procedure of retrieving it from the staging area.
The retrieval procedure shall only accept rows in the staging area that are
correct and only build correct rows in the warehouse, all incorrect rows are
marked as such in the staging area and never reach the warehouse.

### |0x303| Data Mart

The data mart is populated from the warehouse, therefore we can assume that the
data it is fetching is correct.  The mart does not need all the data in the
warehouse, therefore we allow for it to load only pieces of it.

A mart is configured to store data only for a couple of years.  For example, in
2016, it makes sense to store hotel offers for 2016 and 2017 but does not make
sense to have the offers for 2015 in there.  Less data in the mart mean queries
against less data, which in turn means faster queries.

The mart is queried based on the validity of offers at the moment the query is
fired (at least it should be in a real world scenario).  Therefore we cache the
validity of each offer against all days, and hours within these days, in the
time period the mart is configured for.  The cache makes querying the data mart
much easier (and faster).

We do not have enough data to perform real-time queries to the mart.  This
limits the possibility of testing the mart.  To overcome this a new query
parameter was added: `query_at`.  Thanks to this parameter we can simulate
queries happening at any point in time.  For a real world application of the
mart we would need to either remove the parameter and use the current time, or
place extra logic in a system in front of the data mart (e.g. in the load
balancer) that would add the parameter based on the current time.

The design of loading only specific years is useful when the data in the mart
becomes old.  For if we have a mart for 2016 and 2017, in the middle of 2017 we
will want to drop most of the data.  In that case we can build a second mart
for 2017 and 2018 and switch the marts once the second mart is ready.


## |0x400| Spreading across several machines

The warehouse is extensively configurable, and, thanks to the fact that it is
based on a web framework, can easily be run with different parts of it on
different machines.

TODO

### |0x401| Why would you like to distribute?

The warehouse became too big to run on a single machine. TODO

### |0x402| Example setup

`uwsgi` is really needed here.  TODO

### |0x403| What would you need to change

Three different database servers.  TODO


## |0x500| Frequent Questions (FAQ)

A FAQ is a list of questions and answers that allow for the explanation of
specific decisions that would be difficult to fit in any other section.  The
following list is an excerpt of decisions about technologies used and reasons
why I digressed from the original proposal.

### |0x501| I expected to see SQL and got a Web Framework, what gives?

I worked on a couple of warehouses and saw several issues in how they were
designed.  First of all was the overuse of triggers which I talk more about in
the next question, second was the complexity of the code that checks for
correct data.  SQL, even procedural SQL is not an expressive language for
branching conditions.  SQL is a language for query definition, not far off
functional languages, but data verification is better achieved with plain
procedural structured syntax.

Verification is better in procedural languages because we want to check for all
errors when a row of data comes in, not fail on the first error.  It is nicer
with an operator of the warehouse to try to give him as much information as
possible up front, instead of forcing him to re-run the verification procedure
over and over.  Therefore performing checking in `python` is considerably
better than trying to achieve the same by bending SQL syntax.  Django uses an
Object Relational Model (ORM) to perform SQL whilst it keeps the syntax within
the python environment as pure python objects.

Postgres allows for procedures to be written in `python`, and that is a path we
could try.  But it does not allow to perform caching inside these procedure,
which is our next point.

Caching in Django (or in python in general) can be performed in memory, in
other words we have much more control over what is cached and how.  In a real
world scenario we would use a memory based database (e.g. `redis`) to manage
the caches.  This caching allows us to make less queries to the database, and
allows for a better use of the cache inside the `RDMBS` (e.g. the database does
not need to fetch the currency rows or keep them in cache, it only needs to
keep track of the primary key index of the currency table).

As a bonus, Django gives us an almost free web interface.  One thing that
people ask for most often in a warehouse is an interface to look whether
certain rows have been loaded or not, or an interface to update erroneous rows
that does not require knowledge of SQL.  We have both, and changing the display
of the interfaces is trivial since we are using a templating engine.

### |0x502| OK, but why do you use an ORM?

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

### |0x503| But isn't an ORM slower than stored procedures?

At first sight *yes*.  An `ORM` will read data into memory and, only after
processing it, it will write it back to disk.  Loading the data into memory may
happen over the network, making it even slower.

On the contrary a stored procedure makes a pipeline: disk `->` memory `->`
disk, which is very fast.  Yet, on a reasonable warehouse data is never
processed by a single stored procedure, neither it is processed inside a single
instance of a database.  Therefore the overhead of sending the data through the
network and keeping it in memory during the processing is just the same with
stored procedures once a data warehouse grows.

### |0x504| Things are in memory, won't the system be out of memory?

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

### |0x505| Why Django?

I am most familiar with Django as a web framework and it is the `ORM` I am most
familiar with as well.  A real warehouse needs an interface to a database
(probably several databases), an engine to verify erroneous data, and a web
interface for operators.  Django provides all pieces.

Moreover, I worked on a project where we used Django as a web interface for a
warehouse.  After the initial setup we noticed that we started migrating
functionality from procedures in the database into django.  That situation gave
birth to the idea of making a warehouse fully in django (yet, we could not
rewrite half a project at that point).

To be fair Django's `ORM` has several limitations, notably it cannot build a
query with an `OR` inside the `WHERE` clause (although you can get around it
with a `(query1) UNION ALL (query2)`).  All limitations have decent
workarounds, and you can also query using raw SQL, but you need to keep them in
mind when building database indexes.

### |0x506| Would you use Django in production in a large warehouse?

Probably not.  A really huge warehouse, processing Tera bytes of rows per day
would not be suitable to be deployed on an `RDBMS`.  Django can be slow
sometimes, and it is very closely coupled together, i.e. its `ORM` is coupled
with the templating system, with the engine, etc.  Therefore it would be
troublesome to substitute django's `ORM` to use a NoSQL database for certain
pieces.

For a really huge warehouse, I'd try to do something very similar to this one
but with loser coupling.  Using `pyramid` for the web part and coupling it with
`sqlalchemy` for the SQL and with something like `datastax` or a `mongodb`
binding for the more speed hungry (and not ACID required) records.  To be fair
that would be an interesting project to try.

### |0x507| I do not know Django, how do it check the DB optimisation?

Yeah, OK.  That's the downside of doing it in django.  Django has an awesome
tutorial that can be found with a trivial google search, but that would be if
you are curious, below I explain how to read the Django files in this
repository and in the repositories of each warehouse package.

In this repository we have:

*   Several files in the `conf` directory.  These are read by Django as
   configuration parameters and then available in `django.seetings`.

*   `hq/routers.py` which is just a simple trick to route the SQL queries to
   the correct database based on the object being queried.

*   `conf/urls.py` is the entry point for the web interface, it defines how
   URLs are handled.

All packages have the following files and/or directories:

*   `models.py` is the file that defines the tables.  It is the most important
   file for us.  Each class in there is a table (unless it has `abstract =
True` specified).  Each class variable in a class table is a column, the type
of the column is defined by the object type assigned to the variable, and other
parameters for the column are arguments to the constructor of this object.

*   Notable arguments that define columns are `db_index` which produces an
   index on the column and `default` which operates like the SQL parameter of
the same name 9gives a default value if `NULL` is inserted).

*   A `Meta` class can be defined on a table class to make several changes on
   how the resulting table behaves.  An `abstract` field on a `Meta` class
forces a table to not be built for a table class, this is useful to inherit
such a class (with all its fields) into a different class that will build a
table.  `unique_together` produces unique indexes (and constraints) on the
given columns, `index_together` produces non-unique indexes.

*   `views.py` and `urls.py` contain the webserver functionality, `urls.py`
   just drive the URLs home to the views which send a response.  Most views are
trivial, the only two views that are more complex are the `API` calls in the
staging area package and the data mart package.  How the return is performed
from these views is heavily commented.

*   `command_line.py` is a file not used by django, but added to create the
   command line tools used by the warehouse ETL process.  In there we have
functions that are entry points for each command line tool, which function is
used for which tool is defined in `setup.py`.  The functions simply process
their arguments and use django objects to communicate with the database.

*   Finally the `templates` directory in each package holds the templates used
   to display the responses from the views.  All static content (e.g. `CSS` and
`javascript`) is included in the templates for simplicity (that's actually bad
practice, but otherwise it would complicate the installation).

Where the `ORM` queries become too complex I have added comments that explain
them in SQL.

### |0x508| Why do you believe that optimisation by caching is better?

It is not necessarily better, in the case at hand it is better.  Since the
warehouse maintains consistency it will check foreign keys on each insert.  Yet
on a failure we will not know which foreign key failed, and we want to be able
to tell an operator what is wrong.  The only way for us to check which foreign
key failed is to query the tables to which they point and find the queries that
do not return results.  Making extra queries (which may be several for a single
insert) whilst we are already inserting hundreds of thousands of rows is not a
good idea.

One may argue that the database will need to check the foreign keys during the
insert operation, and therefore will need to select from the tables that the
foreign keys point to.  That is correct, but the database does not need to
select actual records from the linked tables.  Foreign keys are indexed
therefore to check them the database only needs to search the index.  Therefore
our in memory cache is an actual performance boots.

### |0x509| There are a lot of quirks with python 3, why did you use it?

To fair, I have started the project in `python2` but a week in I discovered
that `numpy` and `scipy` (the two major libraries that are holding systems from
upgrading to `python3`) finally released their `python3` compatible versions.
This means that a switch to `python3` is over the horizon, and who does not
switch to it will end with an unsupported version.

The move to `python3` is finally happening and it would be unwise to not switch
too.  I use `python3` extensively these days because I use a distro that has
`python3` as the main python (arch) and I am lazy to add that extra character
to use `python2` to all scripts.  Yet, this was the first big piece of code
using `python3`.

### |0x50a| That is quite a lot of code, how long did it take?

It took some 90-100 hours of work, but this is a rather rough estimate since I
did not count.  About 30% of the code I have copied from another project
(notably the front-end), which helped a lot.

Several other things could be done, for example, there isn't a single test
written.  But that would be unnecessary "gold-plating", i.e. overworking a
project that already is good enough for its purpose.  I had a lot of fun with
this piece of code, when I saw the phrase "feel free to over-deliver" in the
requirements I was already happy that I will able to make something that I may
reuse someday.

The only thing that I would like to do with this code that I could not is to
test the entire thing on a postgres database.  Due to limitations of
computation power I have currently available I did not manage to test the
warehouse with the full ~800MB data.  I'm pretty confident about the robustness
of the code, but, given that there are no unit tests, it is as far as
confidence can go.


## |0x600| Copying

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

