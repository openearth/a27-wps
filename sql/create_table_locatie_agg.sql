'-- following query creates lon, lat, locatie_id, list of peilfilters per locatie_id, bron_id and dataleverancier'
'-- this will further be used in the function that calls the tube and tubefilters'

drop table if exists gws.locatie_agg;
create table gws.locatie_agg as
select st_x(st_transform(l.geom,4326)) as longitude_wgs84, st_y(st_transform(l.geom,4326)) as latitude_wgs84, l.locatie_id, l.locatienaam_master,string_agg(p.peilfilter_id::text, ',') as peilfilterids, l.bron_id, b.dataleverancier
from gws.locatie l 
join gws.peilfilter p on p.locatie_id = l.locatie_id
join gws.bron b on b.bron_id = l.bron_id
group by l.locatie_id, l.bron_id, b.dataleverancier;