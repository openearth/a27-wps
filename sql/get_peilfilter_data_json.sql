"""
# new version (24-06-2025) which reads data from a dedicated table with a list of filterid's as extra column
See create_table_locatie_agg.sql as sql that creates the data.
"""
-- FUNCTION: gws.get_peilfilter_data_json(integer, timestamp without time zone, timestamp without time zone)

-- DROP FUNCTION IF EXISTS gws.get_peilfilter_data_json(integer, timestamp without time zone, timestamp without time zone);

CREATE OR REPLACE FUNCTION gws.get_peilfilter_data_json(
	peilfilterid integer,
	start_time timestamp without time zone DEFAULT NULL::timestamp without time zone,
	end_time timestamp without time zone DEFAULT NULL::timestamp without time zone)
    RETURNS SETOF json 
    LANGUAGE 'sql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
SELECT json_build_object(
    'locationproperties',json_build_object(
						'locatie id', pf.locatie_id,
	   					'locatie naam',l.locatienaam_master,
	   					'maaiveld hoogte',l.maaiveldhoogte_cm_nap,
       					'peilfilter naam', pf.peilfilternaam,
	   					'peilfilter id', pfd.peilfilter_id, 
	   					'bovenkantpeil buis',pfd.bovenkant_peilbuis_meetpunt_cm_nap, 
	   					'bovenkant filter',pfd.bovenkant_filter_cm_nap, 
	   					'onderkant filter',pfd.onderkant_filter_cm_nap
	                                      ),
	'timeseries',json_agg(json_build_object(
 						'datetime',m.datumtijd,
						'head',m.gws_cm_nap
											)
						 )
    )
FROM gws.peilfilter_data pfd
join gws.peilfilter pf on pf.peilfilter_id = pfd.peilfilter_id
join gws.locatie l on l.locatie_id = pf.locatie_id
join gws.meting m on m.peilfilter_id = pfd.peilfilter_id
where pfd.peilfilter_id = peilfilterid 
and m.datumtijd >= coalesce(start_time,m.datumtijd - interval '100 year') 
and (end_time is NULL or m.datumtijd <= end_time)
group by pf.locatie_id,
		 l.locatienaam_master,
		 l.maaiveldhoogte_cm_nap, 
		 pf.peilfilternaam,
		 pfd.peilfilter_id,
		 pfd.bovenkant_peilbuis_meetpunt_cm_nap,
		 pfd.bovenkant_filter_cm_nap,
		 pfd.onderkant_filter_cm_nap
$BODY$;

ALTER FUNCTION gws.get_peilfilter_data_json(integer, timestamp without time zone, timestamp without time zone)
    OWNER TO hendrik_gt;
