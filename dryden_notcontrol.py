import geopandas as gpd
import pandas as pd

import matplotlib.pyplot as plt

import numpy as np
from shapely.geometry import Point
from shapely.ops import cascaded_union, unary_union

import random


#Pull in shapefile
def read_data(fp):

    df = gpd.read_file(fp)
    return df

#Make the buffer around the site
#Cut the buffer based on the polygon and the 45 m buffer around edge
#Make points inside buffer every 10 m
#List the points
#Generate a random number

def gen_rand(base,top):
    random.seed(42)
    x = random.randint(base,top)
    return x 
#Select a point
#Buffer around selected point (90m) and delete points in list inside the buffer
#Make another random number and select a new site
#Repeat deletion of points
#Repeat 2 more times.


        
if __name__ == "__main__":
    #Read polygons
    #df_underlying = read_data('dissolved.shp')
    df_underlying = read_data('dryden_underlying.shp')
    #print(df_underlying)

    #Read csv of sites and filter
    df_sites = pd.read_csv('sites.csv', encoding= 'unicode_escape')
    #print(df_sites)
    df_sites = df_sites[df_sites['Project'] == 'JPBW']
    df_sites = df_sites[df_sites['Description'] != 'Control'] #!=
    #df_sites = df_sites[df_sites['Note'] != "Matt's"]
    df_sites = df_sites[df_sites['Name'] != "2020_Site3"]
    #df_sites = df_sites[df_sites['Name'].isin(["F15","ElvaLake","SilverDollar"])]
    df_sites_geom= gpd.GeoDataFrame(df_sites, geometry=
                                    gpd.points_from_xy(df_sites['Longitude'],
                                                    df_sites['Latitude']),crs='EPSG:4326')
    #print(df_sites_geom)

    #Make the buffer
    df_sites_proj = df_sites_geom.to_crs('ESRI:102001')
    #print(df_sites_proj)
    
    df_sites_buffer = df_sites_proj.buffer(500).to_crs('EPSG:4326')
    #print(df_sites_buffer)
    fig, ax = plt.subplots(1,1)
    df_sites_buffer.plot(ax=ax)
    plt.show()

    #Clip buffer with constraints

##    df_clip = df_sites_buffer.clip(df_underlying)
##    print(len(df_clip))
##    print(df_clip)
##    if len(df_clip) == 0:
    df_clip=df_sites_buffer
    fig, ax = plt.subplots(1,1)
    df_clip.plot(ax=ax)
    plt.show()

    #Make the point grid
    df_explode = df_clip.to_crs('ESRI:102001') #.explode()
    df_explode = gpd.GeoDataFrame(df_sites_proj,geometry=df_explode,crs='ESRI:102001') 

    df_45 = read_data('dryden_45m_buff.shp')
    #df_45 = read_data('control_45m_buff.shp')
    df_clip = df_sites_buffer.clip(df_underlying)
    df_clip_proj = df_clip.to_crs('ESRI:102001')
    
    counts = []
    lats = []
    lons = []
    names = [] 
    count = 0 
    for n,polygon in zip(df_explode['Name'],list(df_explode['geometry'])):
        count +=1
        print(n)
        print(polygon)
        if n != 'None': 
            fig, ax = plt.subplots(1,1)
            gpd.GeoDataFrame(geometry=[polygon]).plot(ax=ax)
            plt.show()
            spacing = 5

            xmax = polygon.bounds[0]
            xmin = polygon.bounds[2]

            ymax = polygon.bounds[3]
            ymin = polygon.bounds[1]
            num_col = int(abs(xmax - xmin) / spacing)

            num_row = int(abs(ymax - ymin) / spacing)


            Yi = np.linspace(ymin,ymax,num_row+1)
            Xi = np.linspace(xmin,xmax,num_col+1)
            Xi,Yi = np.meshgrid(Xi,Yi)

            points = [Point(x) for x in zip(Xi.flatten(),Yi.flatten())]
            points = gpd.GeoDataFrame(geometry=gpd.GeoSeries(points),crs='ESRI:102001')
            points = gpd.overlay(points, df_45, how='difference')
            
            points2 = points.clip(gpd.GeoDataFrame(geometry=df_clip_proj,crs='ESRI:102001'))

            polygon0 = polygon
            print(polygon0)
            polygon1 = polygon0.difference(df_45['geometry'].unary_union)
            fig, ax = plt.subplots(1,1)
            gpd.GeoDataFrame(geometry=[polygon1]).plot(ax=ax)
            plt.show()
            print(polygon1)
            #polygon2 = gpd.GeoSeries(polygon1,crs='ESRI:102001').difference(df_affected['geometry'])
            #polygon2 = gpd.GeoDataFrame(geometry=[polygon1],crs='ESRI:102001')
            if len(points2) > 0:
                fig, ax = plt.subplots(1,1)
                gpd.GeoDataFrame(geometry=df_clip_proj,crs='ESRI:102001').plot(ax=ax)
                plt.show()
                polygon3 = gpd.GeoDataFrame(geometry=[polygon1],crs='ESRI:102001').clip(gpd.GeoDataFrame(geometry=df_clip_proj,crs='ESRI:102001'),keep_geom_type=True)
                print(polygon3)
                fig, ax = plt.subplots(1,1)
                polygon3.plot(ax=ax)
                plt.show()
                #polygon5 = polygon3.difference(df_affected['geometry'])
                #print(polygon5)
                polygon3.to_file(driver = 'ESRI Shapefile', filename= "poly_dryden_"+str(n)+".shp")
            else:
                polygon6 = gpd.GeoDataFrame(geometry=[polygon],crs='ESRI:102001')
                polygon6.to_file(driver = 'ESRI Shapefile', filename= "poly_dryden_"+str(n)+".shp")
            if len(points2) > 0:
                points = points2
##            if len(points) <= 500:
##                spacing = 1
##                num_col = int(abs(xmax - xmin) / spacing)
##
##                num_row = int(abs(ymax - ymin) / spacing)
##
##
##                Yi = np.linspace(ymin,ymax,num_row+1)
##                Xi = np.linspace(xmin,xmax,num_col+1)
##                Xi,Yi = np.meshgrid(Xi,Yi)
##                points = [Point(x) for x in zip(Xi.flatten(),Yi.flatten())]
##                points = gpd.GeoDataFrame(geometry=points,crs='ESRI:102001')
##                points = gpd.overlay(points, df_45, how='difference')
##                if len(df_clip_proj) > 0: 
##                    points = points.clip(gpd.GeoDataFrame(geometry=df_clip_proj,crs='ESRI:102001'))
            fig, ax = plt.subplots(1,1)
            #points = gpd.GeoDataFrame(geometry=points,crs='ESRI:102001')
            points.plot(ax=ax)
            plt.show()
            
            
            plot1_id= gen_rand(0,len(points))
            plot1 = list(points['geometry'])[plot1_id]

            try: 


                buff = plot1.buffer(90)
                new_points2 = gpd.overlay(points,gpd.GeoDataFrame(geometry=[buff],crs='ESRI:102001'), how='difference')
                
                plot2_id= gen_rand(0,len(new_points2))
                
                plot2 = list(new_points2['geometry'])[plot2_id]

                
                buff = plot2.buffer(90)
                new_points3 = gpd.overlay(new_points2,gpd.GeoDataFrame(geometry=[buff],crs='ESRI:102001'), how='difference')
                
                plot3_id= gen_rand(0,len(new_points3))
                plot3 = list(new_points3['geometry'])[plot3_id]           

                
                buff = plot3.buffer(90)
                new_points4 = gpd.overlay(new_points3,gpd.GeoDataFrame(geometry=[buff],crs='ESRI:102001'), how='difference')
                
                plot4_id= gen_rand(0,len(new_points4))
                plot4 = list(new_points4['geometry'])[plot4_id]
                dist = plot4.distance(df_underlying.unary_union)
                lons.append([plot1.x,plot2.x,plot3.x,plot4.x])
                lats.append([plot1.y,plot2.y,plot3.y,plot4.y])
                counts.append([count]*4)
                names.append([n]*4) 
                print(lons)

            except: 

                lons.append([np.nan,np.nan,np.nan,np.nan])
                lats.append([np.nan,np.nan,np.nan,np.nan])
                counts.append([count]*4)
                names.append([n]*4) 

    a = pd.DataFrame()
    a['Longitude'] = [j for i in lons for j in i]
    a['Latitude'] = [j for i in lats for j in i]
    a['ID'] = [j for i in counts for j in i]
    a['Name'] = [j for i in names for j in i]
    b = gpd.GeoDataFrame(a,geometry=gpd.points_from_xy(a['Longitude'],
                                                    a['Latitude']),crs='ESRI:102001').to_crs('EPSG:4326')
    a['Lon_Proj'] = list(b['geometry'].x)
    a['Lat_Proj'] = list(b['geometry'].y)
    #a.to_csv('dryden_500_nocontrol_1m_redo2_2020_Site3.csv', index=False)
    
    
    
