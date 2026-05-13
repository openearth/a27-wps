-- One row per (tree, inspection-date) — long format.
-- Mirrors gws.meting (peilfilter_id, datumtijd, gws_cm_nap).
-- Run after create_table_boom.sql.

CREATE TABLE IF NOT EXISTS gws.boom_meting (
    boom_id        integer   NOT NULL REFERENCES gws.boom(boom_id) ON DELETE CASCADE,
    datumtijd      timestamp WITHOUT TIME ZONE NOT NULL,
    conditie_text  text,      -- raw Dutch label, e.g. 'Voldoende-goed'
    conditie_score smallint,  -- numeric 0..8, NULL when not assessable
    PRIMARY KEY (boom_id, datumtijd)
);

CREATE INDEX IF NOT EXISTS boom_meting_boom_idx ON gws.boom_meting (boom_id);
CREATE INDEX IF NOT EXISTS boom_meting_dt_idx   ON gws.boom_meting (datumtijd);
