README for the Hotel Quickly Data Warehouse Hack (`hq-dw`)

## Introduction

`hq-dw` is a collection of `django` configurations to run a data warehouse
behind an `ORM` (object relational mapper).  It depends on the remaining
`django` apps: `hq-stage`, `hq-warehouse` and `hq-hotel-mart`, to perform the
database queries.  `hq-dw` glues together the three apps into a coherent
configuration.

## Installation

TODO

    git clone https://github.com/grochmal/hq-dw.git
    cd hq-dw
    virtualenv hq
    source hq/bin/activate
    pip -r requirements.txt

Install the apps (TODO)

Configure the database (TODO)

Development system

    cd hq-dw
    export DJANGO_SETTINGS_MODULE=conf.dev
    python manage.py runserver

Production system with `uwsgi` (TODO)

    cd hq-dw
    python TODO.py

## Design

TODO

## Spreading across several machines

TODO

## Copying

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

