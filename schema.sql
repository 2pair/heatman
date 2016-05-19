drop table if exists GeoIPs;
create table GeoIPs (
    startIP text not null,
    endIP text not null,
    startIPnum text primary key not null,
    endIPnum text not null,
    countryCode text,
    regionCode text,
    cityName text,
    latitude float not null,
    longitude float not null,
    postalCode integer,
    metroCode integer,
    areaCode integer
);
