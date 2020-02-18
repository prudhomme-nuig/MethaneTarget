#! /bin/python

import xarray as xr
import numpy as np
import regionmask
import geopandas as gpd
import pandas as pd
import argparse

parser = argparse.ArgumentParser('Compute livestock density based on GLiPHmaps or FAOSTAT')
parser.add_argument('--import-density-from-GLiPHmaps', action='store_true', help='Use GLiPHmaps or FAOSTAT')

args = parser.parse_args()

if args.import_density_from_GLiPHmaps:
    # Load the shapefile
    PATH_TO_SHAPEFILE = 'data/GLiPHAmaps/global/supplementary_data/adm_boundary/glbl0.shp'
    country = gpd.read_file(PATH_TO_SHAPEFILE)
    density_dict={}
    for livestock_type in ['cattle','buffaloes','smallrum']:
        density_dict[livestock_type]={}
        #Read raster file
        d = xr.open_mfdataset('data/GLiPHAmaps/results/livestock_density_'+livestock_type+'_25cor.nc',combine='by_coords')

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
else:
    country_list=["Ireland","France","India","Brazil","Netherlands"]
    grassland_list=["Land under temp. meadows and pastures","Land with temporary fallow","Land under perm. meadows and pastures"]
    item_dict={"cattle":"Cattle","Sheep and Goats":"Sheep and Goats"}
    #Use area of the reference year to rescale density
    grassland_df=pd.read_csv("data/FAOSTAT_areas.csv")
    production_livestock_df=pd.read_csv("data/FAOSTAT_enteric_fermentation.csv")
    production_livestock_df=production_livestock_df[production_livestock_df["Element"]=="Stocks"]
    grassland_area_dict={}
    density_pd=pd.DataFrame(columns=country_list)
    for country in country_list:
        grassland_area_dict[country]=0
        for element in grassland_list:
            grassland_area_dict[country]+=grassland_df["Value"][(grassland_df["Item"]==element) & (grassland_df["Area"]==country)].values[0]*1000
        for item in item_dict.keys():
            density_pd.loc[item_dict[item],country]=production_livestock_df[(production_livestock_df["Item"]==item_dict[item]) & (production_livestock_df["Area"]==country)]["Value"].values[0]/grassland_area_dict[country]
            item_name=item.lower().replace(' ','_')
    density_pd.to_csv('output/density_livestock.csv')
    for key in grassland_area_dict.keys():
        grassland_area_dict[key]=[grassland_area_dict[key]]
    grassland_area_df=pd.DataFrame.from_dict(grassland_area_dict)
    grassland_area_df.to_csv('output/grassland_area.csv')
