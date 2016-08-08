DELETE = """
    drop table if exists ulsIDs;
    drop table if exists records;
    drop table if exists locations;
    drop table if exists frequencies;
    drop table if exists emissions;
    drop table if exists towers;
"""

CREATE = """
    create table if not exists ulsIDs (
        rkey integer primary key,
        service text not null,
        status text not null
    );

    create table if not exists records (
        rkey integer primary key not null,
        title text not null,
        callsign text not null,
        status text not null,
        service text not null,
        eligibility text
    ) without rowid;

    create table if not exists locations (
        id integer primary key,
        rkey integer references records not null,
        lkey integer not null,
        type text not null,
        desc text,
        latitude real,
        longitude real
    );

    create table if not exists frequencies (
        id integer primary key,
        rkey integer references records not null,
        fkey integer not null,
        lkey integer not null,
        frequency integer not null,
        power integer
    );

    create table if not exists emissions (
        id integer primary key,
        rkey integer references records not null,
        fkey integer not null,
        emission text not null
    );

    create table if not exists towers (
        tkey integer primary key not null,
        latitude real,
        longitude real
    ) without rowid;
"""

INIT = """
    pragma foreign_keys = on;
"""
