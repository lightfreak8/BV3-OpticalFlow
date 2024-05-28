"""
get your GPS data from your gpx File plotted 

"""

gpx_file_path = "C:/Users/rapha/switchdrive/PHO_Studium/Bildverarbeitung 3/SEMESTERPROJEKT/Aufnahmen_09.05.2024/gpsFlowTrack.gpx"


import gpxpy
import matplotlib.pyplot as plt
import utm

#convert geographic coordinates (latitude and longitude) to UTM coordinates (eastings and northings)
def convert_to_meters(lat, lon, start_lat, start_lon):
    # Convert the given latitude and longitude to UTM coordinates
    utm_coords = utm.from_latlon(lat, lon)
    # Convert the start latitude and longitude to UTM coordinates
    start_utm_coords = utm.from_latlon(start_lat, start_lon)
    # Calculate the difference in eastings and northings
    return utm_coords[0] - start_utm_coords[0], utm_coords[1] - start_utm_coords[1]

def plot_gpx(gpx_file):
    # load gpx file
    with open(gpx_file, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # extract gps data and converts in meters
    latitudes = []
    longitudes = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                latitudes.append(point.latitude)
                longitudes.append(point.longitude)

    start_lat, start_lon = latitudes[0], longitudes[0]
    latitudes.reverse()
    longitudes.reverse()
    latitudes_meters = []
    longitudes_meters = []

    for lat, lon in zip(latitudes, longitudes):
        x, y = convert_to_meters(lat, lon, start_lat, start_lon)
        latitudes_meters.append(x)
        longitudes_meters.append(y)

    # plot
    plt.figure(figsize=(10, 6))
    plt.plot(longitudes_meters, [-y for y in latitudes_meters], color='blue', linewidth=2, label='GPS Track')
    plt.xlabel('X [m]')
    plt.ylabel('Y [m]')
    plt.title('GPX Track Plot')
    plt.grid(True)
    plt.axis('equal')  # ensures the axis ratio
    plt.legend()
    plt.show()

if __name__ == "__main__":
    plot_gpx(gpx_file_path) #path of gpx file
