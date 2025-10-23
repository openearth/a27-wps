"""
# new version (24-06-2025) which reads data from a dedicated table with a list of filterid's as extra column
See create_table_locatie_agg.sql as sql that creates the data.
"""
CREATE OR REPLACE FUNCTION gws.get_locations_pfid_geojson()
    RETURNS SETOF json
    LANGUAGE 'sql'
    VOLATILE
    PARALLEL UNSAFE
    COST 100    ROWS 1000 
    
AS $BODY$
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(
        json_build_object(
            'type', 'Feature',
            'geometry', ST_AsGeoJSON(ST_SetSRID(ST_MakePoint(longitude_wgs84, latitude_wgs84), 4326))::json,
            'properties', json_build_object(
                'locatie_id', l.locatie_id,
                'peilfilter_ids', l.peilfilterids,
                'bron_id', l.bron_id,
                'dataleverancier', l.dataleverancier
            )
        )
    )
) AS feature_collection
FROM gws.locatie_agg l;
$BODY$;

'# deprecated function because it is required to get a list of filters for each tube'
CREATE OR REPLACE FUNCTION gws.get_locations_geojson() 
RETURNS SETOF json AS
$$
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(
        json_build_object(
            'type', 'Feature',
            'geometry', ST_AsGeoJSON(ST_SetSRID(ST_MakePoint(longitude_wgs84, latitude_wgs84), 4326))::json,
            'properties', json_build_object('locatie_id', locatie_id)
        )
    )
)
FROM gws.locatie
$$ LANGUAGE sql;

select * from gws.get_locations_geojson();