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