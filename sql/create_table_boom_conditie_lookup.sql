-- Reference table: Dutch condition label → numeric score 0..8.
-- NULL score means the condition could not be assessed at that inspection.
-- Source: bomendata.py (valtonum dict).

CREATE TABLE IF NOT EXISTS gws.boom_conditie_lookup (
    conditie_text  text     PRIMARY KEY,
    conditie_score smallint             -- nullable
);

INSERT INTO gws.boom_conditie_lookup (conditie_text, conditie_score) VALUES
    ('Goed',                                 8),
    ('goed',                                 8),
    ('Voldoende-goed',                       7),
    ('voldoende-goed',                       7),
    ('voldoende-Goed',                       7),
    ('Voldoende-Goed',                       7),
    ('Voldoende',                            6),
    ('Voldoende (?)',                         6),
    ('voldoende',                            6),
    ('Voldoende-matig',                      5),
    ('voldoende-matig',                      5),
    ('Matig',                                4),
    ('matig',                                4),
    ('Matig-slecht',                         3),
    ('matig-slecht',                         3),
    ('Slecht',                               2),
    ('Bijna dood',                           1),
    ('Dood',                                 0),
    ('Meegesleurd door vallende es',         0),
    ('c',                                    0),
    ('Nog niet voldoende zichtbaar',         NULL),
    ('Nog niet in monitoring',               NULL),
    ('Niet vast te stellen (te vroeg)',      NULL),
    ('Niet meer voldoende zichtbaar',        NULL)
ON CONFLICT (conditie_text) DO NOTHING;
