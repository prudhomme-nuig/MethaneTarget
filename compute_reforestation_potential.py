#! /bin/python

import xarray as xr
import numpy as np
import regionmask
import geopandas as gpd
import pandas as pd
from affine import Affine
from osgeo import gdal
#import matplotlib.pyplot as plt

# Load the shapefile
PATH_TO_SHAPEFILE = 'data/GLiPHAmaps/global/supplementary_data/adm_boundary/glbl0.shp'
country = gpd.read_file(PATH_TO_SHAPEFILE)
#Read raster file
d = xr.open_rasterio('data/NCS/NCS_Refor11_map.tif')
transform = Affine.from_gdal(*d.attrs['transform'])
nx, ny = d.sizes['x'], d.sizes['y']
x, y = np.meshgrid(np.arange(nx)+0.5, np.arange(ny)+0.5) * transform

#d = xr.open_mfdataset('data/NCS/NCS_Refor11_map.tif',combine='by_coords')
for country_name in ['Ireland','INDIA','Brazil','France','United States of America']:
    #Create the country mask
    name = 'country_mask'
    country_index=country.index[country['COUNTRY']==country_name][0]
    numbers = [country_index]
    names = {country_index:country_name}
    abbrevs = {country_index:country.loc[country_index,'ISO3']}
    poly = {country_index: country.loc[country_index,'geometry']}

    country_mask_poly = regionmask.Regions_cls(name, numbers, names, abbrevs, poly)
    lon_min=country_mask_poly.bounds[0][0]
    lon_max=country_mask_poly.bounds[0][2]
    lat_min=country_mask_poly.bounds[0][1]
    lat_max=country_mask_poly.bounds[0][3]
    ds = gdal.Open('data/NCS/NCS_Refor11_map.tif')
    ds = gdal.Translate('data/NCS/''_NCS.tif', ds, projWin = [lon_min, lat_min, lon_max, lat_max])

    mask = country_mask_poly.mask(d.sel(lat = slice(lat_min, lat_max), lon = slice(lon_min, lon_max)), lat_name='lat', lon_name='lon')

    #Create the extend for plotting
    lat=mask.lat.values
    lon=mask.lon.values
    sel_mask = mask.where(mask == country_index).values

    id_lon = lon[np.where(~np.all(np.isnan(sel_mask), axis=0))]
    id_lat = lat[np.where(~np.all(np.isnan(sel_mask), axis=1))]

    #Plot
    out_sel = d.sel(lat = slice(id_lat[0], id_lat[-1]), lon = slice(id_lon[0], id_lon[-1])).compute().where(mask == country_index)
    #plt.figure(figsize=(12,12))
    #out_sel.density_cattle.plot()
    #Save as raster
    #out_sel.to_netcdf(country_name+'_livestock_density.nc')
    density_dict[livestock_type][country_name[0].upper()+country_name[1:].lower()]=[np.mean(out_sel["density_"+livestock_type].data[out_sel["density_"+livestock_type].data>0])/100]
    density_pd=pd.DataFrame.from_dict(density_dict[livestock_type])
    density_pd.to_csv('output/density_'+livestock_type+'.csv')
