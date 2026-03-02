CREATE OR REPLACE FUNCTION gws.get_depth_info_json(peilfilter_ids integer[])
RETURNS json
LANGUAGE sql
STABLE
AS $BODY$
  WITH peilbuis AS (
    SELECT
      ROUND(bovenkant_peilbuis_meetpunt_cm_nap / 100.0, 2) AS peilbuis_top,
      ROUND((bovenkant_peilbuis_meetpunt_cm_nap - lengte_peilbuis) / 100.0, 2) AS peilbuis_bottom
    FROM gws.peilfilter_data
    WHERE peilfilter_id = ANY(peilfilter_ids)
    ORDER BY peilfilter_id
    LIMIT 1
  ),
  filters AS (
    SELECT
      peilfilter_id,
      ROUND(bovenkant_filter_cm_nap / 100.0, 2) AS filter_top,
      ROUND(onderkant_filter_cm_nap / 100.0, 2) AS filter_bottom
    FROM gws.peilfilter_data
    WHERE peilfilter_id = ANY(peilfilter_ids)
  )
  SELECT json_build_object(
    'peilbuis_top', (SELECT peilbuis_top FROM peilbuis),
    'peilbuis_bottom', (SELECT peilbuis_bottom FROM peilbuis),
    'filters', COALESCE((SELECT json_agg(json_build_object(
      'peilfilter_id', peilfilter_id,
      'filter_top', filter_top,
      'filter_bottom', filter_bottom
    ) ORDER BY peilfilter_id) FROM filters), '[]'::json)
  );
$BODY$;

--select gws.get_depth_info_json(array[2001, 2000])