import pandas as pd
from datetime import datetime
import numpy as np
from pykalman import KalmanFilter
import sys
from xml.dom import minidom
import math


################# FUNCTIONS #################


def output_gpx(points, output_filename):
    """
    Output a GPX file with latitude and longitude from the points DataFrame.
    """
    from xml.dom.minidom import getDOMImplementation
    def append_trkpt(pt, trkseg, doc):
        trkpt = doc.createElement('trkpt')
        trkpt.setAttribute('lat', '%.8f' % (pt['lat']))
        trkpt.setAttribute('lon', '%.8f' % (pt['lon']))
        trkseg.appendChild(trkpt)
    
    doc = getDOMImplementation().createDocument(None, 'gpx', None)
    trk = doc.createElement('trk')
    doc.documentElement.appendChild(trk)
    trkseg = doc.createElement('trkseg')
    trk.appendChild(trkseg)
    
    points.apply(append_trkpt, axis=1, trkseg=trkseg, doc=doc)
    
    with open(output_filename, 'w') as fh:
        doc.writexml(fh, indent=' ')

# Get the XML/GPX data        
def get_data(filename):

    # Read in the gpx file
    xml_file = minidom.parse(filename)
    trkpts = xml_file.getElementsByTagName('trkpt')

    # Create the dataframe
    points_df = pd.DataFrame(columns=['lat','lon'])

    # iterate
    for item in trkpts:
        lat_temp = float(item.attributes['lat'].value)
        lon_temp = float(item.attributes['lon'].value)
        df_temp = {'lat': lat_temp, 'lon': lon_temp}
        points_df = points_df.append(df_temp, ignore_index=True)  
    
    return(points_df)

# Helper Function for distance. PLEASE NOTE: the calculations of this function were sourced from the following link:
    # https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula/21623206
def calc_distance(df_row):
    # Create some local variabels to make our lives easier a little later
    lat1 = df_row['lat']
    lat2 = df_row['lat_next']
    lon1 = df_row['lon']
    lon2 = df_row['lon_next']   
    
    # Lon/Lat --> Radians
    dLat = np.deg2rad(lat2 - lat1)
    dLon = np.deg2rad(lon2 - lon1)
    
    # Some Math Taken from the link above
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(np.deg2rad(lat1)) * math.cos(np.deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = 6371 * c
    
    return d * 1000


# Calculate the total distance from the lon/lat data
def distance(points):
    
    # Create a copy
    points_df = points.copy()
    
    # Shift the data over for the correct formatting
    points_df['lat_next'] = points_df['lat'].shift(periods=-1)
    points_df['lon_next'] = points_df['lon'].shift(periods=-1)
    
    # Calculate distances between the individual points
    points_df['distance'] = points_df[:-1].apply(calc_distance, axis = 1)
    return(points_df['distance'].sum().round(2))


# Smooth the data out with the Kalman Filter and the provided information
def smooth(points):
    
    # Set the initial state of the filter
    initial_state = points.iloc[0]
    
    # How much confidence do we have in our data ([15/(10^5))
    obs_var = 1 
    observation_covariance = np.diag([obs_var, obs_var]) ** 2
    
    # How much confidence do we have in our predictions
    transition_covariance = np.diag([0.55,0.55]) ** 2
    
    # Create the transition matrix
    transition = [[1,0], [0,1] ] 
    
    # Create the Kalman Filter
    kf = KalmanFilter(
        initial_state_mean=initial_state,
        observation_covariance=observation_covariance,
        transition_covariance=transition_covariance,
        transition_matrices=transition
    )    
    
    kalman_smoothed, state_cov = kf.smooth(points)
    
    df_ret = pd.DataFrame()
    df_ret['lat'] = kalman_smoothed[:, 0]
    df_ret['lon'] = kalman_smoothed[:, 1]    
    
    return(df_ret)
    
    
    
    

################# MAIN #################

def main():
    points = get_data(sys.argv[1])
    print('Unfiltered distance: %0.2f' % (distance(points),))
    
    smoothed_points = smooth(points)
    
    print('Filtered distance: %0.2f' % (distance(smoothed_points),))
    output_gpx(smoothed_points, 'out.gpx')


if __name__ == '__main__':
    main()