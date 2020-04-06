# RTGradients
## Reactive Transport Gradients

A tool designed to take in arrays and calculate gradients and various other things related to trying to
use Reactive Transport Theories to quantify and navigate hydrothermal alteration systems

#### Basic outline of process plan April 2020
* Use EDS to determine reactive transport parameters and calculate Nprog (Reaction Progress Number) for the
 geochemical marker
* Create a 3D model of the Nprog distribution and export as equidimensional array. Currently designed to deal
 with inputs as simple ascii files exported from Leapfrog
* calculate the Nprog gradient in the 3D array (dx, dy, dz)
* calculate the 3D vector representation of the gradient by converting to spherical coords
* Calculate the distance to source for each point using Nprog and the gradient vector
* Calculate an estimated location for source for each point
* Output text files in a format suitable for visualisation