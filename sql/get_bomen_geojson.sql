-- Returns all trees with coordinates as a GeoJSON FeatureCollection.
-- Called by wps_get_bomen_locations at startup (no inputs).
-- Mirrors gws.get_locations_pfid_geojson().

CREATE OR REPLACE FUNCTION gws.get_bomen_geojson()
    RETURNS SETOF json
    LANGUAGE sql
    STABLE
    PARALLEL SAFE
AS $BODY$
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', COALESCE(
        json_agg(
            json_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(
                    ST_SetSRID(ST_MakePoint(b.longitude_wgs84, b.latitude_wgs84), 4326)
                )::json,
                'properties', json_build_object(
                    'boom_id',                  b.boom_id,
                    'boomcode',                 b.boomcode,
                    'boomnaam',                 b.boomnaam,
                    'soort_group',              b.soort_group,
                    'exclude_from_group_stats', b.exclude_from_group_stats
                )
            )
        ),
        '[]'::json
    )
)
FROM gws.boom b
WHERE b.longitude_wgs84 IS NOT NULL
  AND b.latitude_wgs84  IS NOT NULL;
$BODY$;

-- select * from gws.get_bomen_geojson();
