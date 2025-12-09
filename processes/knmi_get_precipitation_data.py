import hydropandas as hpd

# RD New (EPSG:28992) coordinates
xy = (90600, 442800)

# daily precipitation from nearest KNMI station (RH → m/day)
prec = hpd.PrecipitationObs.from_knmi(
    xy=xy,
    start="2010-01-01",
    end="2010-12-31",
)

# get as pandas Series/DataFrame and convert to mm/day
s = prec.to_series()          # index = date, values = m/day
prec_mm = s * 1000.0  

