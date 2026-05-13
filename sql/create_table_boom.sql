-- Tree records: one row per unique tree (boomcode).
-- Mirrors the structure of gws.locatie.
-- Run before create_table_boom_meting.sql.

CREATE TABLE IF NOT EXISTS gws.boom (
    boom_id                  serial           PRIMARY KEY,
    boomcode                 text             UNIQUE NOT NULL,  -- "Boom- code" from xlsx
    boomnaam                 text,                              -- "Boomnaam" column from xlsx
    soort                    text,                              -- "Soort" column from xlsx
    soort_group              text,                              -- 'Beuken' | 'Essen' | 'Eiken' | 'undefined'
    geom                     geometry(Point, 28992),            -- RD New, matches gws.locatie
    longitude_wgs84          double precision,
    latitude_wgs84           double precision,
    exclude_from_group_stats boolean          NOT NULL DEFAULT false  -- e.g. true for 9FS
);

CREATE INDEX IF NOT EXISTS boom_geom_idx ON gws.boom USING gist (geom);
