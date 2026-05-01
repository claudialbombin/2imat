import numpy as np
import math
 

def haversine(lat1: np.float64, lon1:np.float64, lat2:np.float64, lon2:np.float64) -> np.float64:
    """
        Method to compute the haversite distance between 2 pair of coordinates

        :param lat1: first latitude
        :param lon1: first longitude
        :param lat2: second latitude
        :param lon2: second longitude
    """
    dLat = (lat2 - lat1) * np.pi / 180.0
    dLon = (lon2 - lon1) * np.pi / 180.0
 
    # convert to radians
    lat1 = (lat1) * np.pi / 180.0
    lat2 = (lat2) * np.pi / 180.0
 
    # apply formulae
    a = (pow(np.sin(dLat / 2), 2) +
         pow(np.sin(dLon / 2), 2) *
             np.cos(lat1) * np.cos(lat2));
    rad = 6371
    c = 2 * np.arcsin(np.sqrt(a))

    # return the distance in km
    return rad * c
 
# Driver code
if __name__ == "__main__":
    pass