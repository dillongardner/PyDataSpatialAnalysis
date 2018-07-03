import pandas as pd
import geopandas as gpd
import os
from rasterio.mask import mask
import rasterio
from shapely import geometry
import numpy as np

# Note: The DHS dataset is available here: https://www.dhsprogram.com/Data/
# To use requires registering, so I have not included it in the data download
DATA_PATH = '/data/PyDataSpatialAnalysis/data'
DHS_HOUSEHOLD_PATH = os.path.join(DATA_PATH, 'DHS/NG_2013_DHS_08212017_1132_110001/nghr6adt/NGHR6AFL.DTA')
DHS_GEO_PATH = os.path.join(DATA_PATH, 'DHS/NG_2013_DHS_08212017_1132_110001/ngge6afl/')


def get_cluster(hhid):
    return float(hhid[:-3])


def geom_to_mean_value(geom, raster):
    try:
        out_image, out_transform = mask(raster, [geometry.mapping(geom)], crop=True)
        res = out_image.mean()
    except ValueError:
        res = -1
    return res


def process_dhs_data():
    print('Reading Survey Data...')
    df = pd.read_stata(DHS_HOUSEHOLD_PATH)
    columns_of_interest = ['hhid', 'hv271']
    df = df[columns_of_interest]
    df['cluster'] = df.hhid.map(get_cluster)
    df = df.drop('hhid', axis=1)
    df.columns = ['assets', 'cluster']
    print('Reading Location...')
    geo_columns = ['DHSCLUST', 'geometry']
    gdf = gpd.read_file(DHS_GEO_PATH)
    gdf = gdf[geo_columns]
    gdf.columns = ['cluster', 'geometry']
    res = gdf.set_index('cluster').join(df.set_index('cluster'), how='left').reset_index()
    # Clusters that have 0,0 listed as location
    clusters_without_location = {302, 373, 422, 514, 557, 569, 639}
    return res[res.cluster.map(lambda x: x not in clusters_without_location)]


def make_fake_points_in_nigeria(num_points=890):
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    nigeria = world.loc[world.name == 'Nigeria', 'geometry'].values[0]
    x_scale = nigeria.bounds[2] - nigeria.bounds[0]
    y_scale = nigeria.bounds[3] - nigeria.bounds[1]
    scale = np.array([x_scale, y_scale])
    intercept = np.array([nigeria.bounds[0], nigeria.bounds[1]])

    def single_point():
        pt_to_try = geometry.Point(np.random.rand(2) * scale + intercept)
        if nigeria.intersects(pt_to_try):
            return pt_to_try
        else:
            return single_point()

    return [single_point() for _ in range(num_points)]


def make_fake_data(num_clusters):
    nigeria_samples = make_fake_points_in_nigeria(num_clusters)
    cluster_count = np.random.randint(17, 45, num_clusters)
    household_assets = np.random.normal(0, 1000, cluster_count.sum())
    cluster = np.hstack([np.repeat(i, c) for i, c in enumerate(cluster_count)])
    geoms_ = [[g] * c for g, c in zip(nigeria_samples, cluster_count)]
    geoms = [g for l in geoms_ for g in l]
    gs = gpd.GeoSeries(geoms)
    gs.crs = {'init': 'epsg:4326'}
    return gpd.GeoDataFrame({'cluster': cluster, 'assets': household_assets},
                            geometry=gs,
                            crs=gs.crs)


if __name__ == '__main__':
    if os.path.isfile(DHS_HOUSEHOLD_PATH) and os.path.isdir(DHS_GEO_PATH):
        res = process_dhs_data()
    else:
        print('DHS data are not in {}'.format(DATA_PATH))
        print('Creating synthetic data')
        res = make_fake_data(890)
    os.makedirs(os.path.join(DATA_PATH, 'formatted_dhs'), exist_ok=True)
    res.to_file(os.path.join(DATA_PATH, 'formatted_dhs', 'formatted_dhs_data.shp'))
