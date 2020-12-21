## Project Description

In this project, I first gathered GPX (GPS XML) data with my smartphone and then built an automated pipeline in Python that smoothed out the GPS data with a Kalman Filter. My goal was to get an accurate estimate of how far I travelled in meters only using the GPS data.

## Project Assumptions

1) Around Vancouver, one degree of latitude or longitude is about 10^5 meters. 
2) While GPS can be accurate to about 5 metres, the reality seems to be several times that: maybe 15 or 20 metres with my phone.
3) Without any other knowledge of what direction I was walking, we must assume that my current position will be the same as my previous position.
4) I usually walk something like 1 m/s and the data contains an observation about every 10 s.

## Steps Taken

1) Read in GPX (XML GPS) data from directory.
2) Clean data and feed it into the Kalman Filter.
3) After having obtained smoothed out GPX data, calculated the distance travelled using the Haversine Formula.
4) Output smoothed GPX data and distance travelled

## How to Build The Project

1) Ensure the GPX based data file is in the same directory as script. Let's call it `walk1.gpx`.
2) Run the following command: `python3 calc_distance.py walk1.gpx`.
3) The smoothed out GPX file comes out a`out.GPX` and the approximated distance travelled is in the file `calc_distance.txt`.

## Example Output

**Walk 1 Raw GPX**

![](/Plots/Walk%201%20Unsmoothed.png)


**Walk 1 Smoothed GPX**

![](/Plots/Walk%201%20Smoothed.png)


