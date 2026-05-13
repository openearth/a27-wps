-- Returns the tree-health graph payload for the requested boomcodes/boomnaams.
-- Pass NULL to return all trees and all group averages.
-- For a map click, pass one tree (for example array['4FS']); the response then
-- contains only that selected tree plus the average line for the group it belongs to.

CREATE OR REPLACE FUNCTION gws.get_boom_data_json(p_boomnaams text[])
    RETURNS json
    LANGUAGE sql
    STABLE
AS $BODY$
WITH requested_trees AS (
    SELECT b.*
    FROM gws.boom b
    WHERE (
        p_boomnaams IS NULL
        OR EXISTS (
            SELECT 1
            FROM unnest(p_boomnaams) AS requested(requested_name)
            WHERE lower(b.boomcode) = lower(requested_name)
               OR lower(b.boomnaam) = lower(requested_name)
        )
    )
),
requested_groups AS (
    SELECT DISTINCT soort_group
    FROM requested_trees
),
tree_rows AS (
    SELECT
        b.boomcode,
        b.boomnaam,
        b.soort_group,
        json_agg(
            json_build_object(
                'date',         m.datumtijd,
                'health_value', m.conditie_score,
                'health_label', m.conditie_text
            )
            ORDER BY m.datumtijd
        ) AS timeseries
    FROM requested_trees b
    JOIN gws.boom_meting m ON m.boom_id = b.boom_id
    GROUP BY b.boomcode, b.boomnaam, b.soort_group
),
group_average_points AS (
    SELECT
        b.soort_group,
        m.datumtijd,
        ROUND(AVG(m.conditie_score)::numeric, 2) AS health_value
    FROM gws.boom b
    JOIN gws.boom_meting m ON m.boom_id = b.boom_id
    WHERE b.soort_group IN (SELECT soort_group FROM requested_groups)
      AND b.exclude_from_group_stats = false
      AND m.conditie_score IS NOT NULL
    GROUP BY b.soort_group, m.datumtijd
),
group_average_rows AS (
    SELECT
        soort_group,
        json_agg(
            json_build_object(
                'date',         datumtijd,
                'health_value', health_value
            )
            ORDER BY datumtijd
        ) AS timeseries
    FROM group_average_points
    GROUP BY soort_group
)
SELECT json_build_object(
    'selected_tree',
        CASE
            WHEN p_boomnaams IS NULL THEN NULL
            ELSE p_boomnaams[1]
        END,
    'y_axis',
        json_build_object(
            'min', 0,
            'max', 8,
            'labels', json_build_array(
                'Dood',
                'Bijna dood',
                'Slecht',
                'Matig-slecht',
                'Matig',
                'Voldoende-matig',
                'Voldoende',
                'Voldoende-goed',
                'Goed'
            )
        ),
    'group_averages',
        COALESCE(
            (
                SELECT json_agg(
                    json_build_object(
                        'group',              gar.soort_group,
                        'visible_by_default', true,
                        'timeseries',         gar.timeseries
                    )
                    ORDER BY gar.soort_group
                )
                FROM group_average_rows gar
            ),
            '[]'::json
        ),
    'trees',
        COALESCE(
            (
                SELECT json_agg(
                    json_build_object(
                        'tree',                tr.boomcode,
                        'tree_name',           tr.boomnaam,
                        'group_that_belongs',  tr.soort_group,
                        'visible_by_default',  true,
                        'timeseries',          tr.timeseries
                    )
                    ORDER BY tr.boomcode
                )
                FROM tree_rows tr
            ),
            '[]'::json
        )
);
$BODY$;

-- select gws.get_boom_data_json(array['1FS','9FS']);
-- select gws.get_boom_data_json(NULL);  -- all trees
