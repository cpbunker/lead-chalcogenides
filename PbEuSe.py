'''
Created on Apr 2, 2020

@author: Christian

Runner file to find and plot energy levels of PbEuSe using the 
hamiltonian.py, EnergyLevels.py and GetEnergyLevels.py modules.

Most if not all experimentally measured params are taken from the paper:
"Magneto-optical properties of semimagnetic lead chalcogenides," Bauer, Zawadski et al 1992
'''

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

from Valleytronics import hamiltonian
from Valleytronics import EnergyLevels
from Valleytronics import GetEnergyLevels

################################################################################
# define the characteristics of PbEuSe that define the bulk hamiltonian
# this is a place where the user will want to make changes
# ie inputting the values of composition x, temperature T, B field, and matrix elements vl and vt

MATERIAL = "PbEuSe"; # global var to pass to plotting functions for titleing plots

# determine the energy gap according to x and T
def Eg_func( x, T):
    '''
    Band gap in eV is function of T, temperature in K, and x, Eu composition
    This function is obtained from  Kryzman et al SPIE 2019 where it applied to PbSnSe, doesn't necessarily apply here
    '''
    # return band gap in eV
    return (72 - 710*x + 2440*pow(x,2) - 4750*pow(x,3) - 22.5 + np.sqrt(506 + 0.1*pow(T - 4.2, 2) ) )/1000;

# input the temperature and Sn composition
# and thus get the gap
x = 0.1; # unitless
T = 10; # in K
Eg = Eg_func(x, T);

            
# other input params of the bulk hamiltonian
B_vec = np.zeros(3); # B field in T
vt = 4*pow(10,5); # transverse velocity matrix element
vl = 4*pow(10,5); # longitudinal velocity matrix element

# define bohr magneton, fundamental constant, only change if you're changing unit systems
mu_Bohr = 5.79e-5; # bohr magneton in eV/T

################################################################################
# define the inputs to the exchange matrix
# changing these parameters will change value of fixed params in plots or domains of plots

# define the phi values for differnt points in the Brillouin zone
# phi is the angle between applied field and chosen z hat direction 
# don't change these, they are built in to the geometry of the problem
phi_central = 0*np.pi/180; # gamma bar point aka central valley, in radians
phi_oblique = 70.5*np.pi/180; # m bar point aka oblique valley, in radians

# define the extra band gap shift of the longitudinal valley
# ie valence band moved further down, conduction band moved further up
# physically this can be produced by a small doping eg 1% Bi
# this is based on the results of Mandal, Springholz et al Nature 2017
long_gap_shift =  0.09; # ie 90 meV

# define exchange parameters according to Bauer's experimental results
# different sets of data according to Eu composition and temperature
# source: Bauer Zawadski 1992 

def GetExpData(data_i, scale_factor = 1):
    '''
    Simple function for selecting one of the experimental data sets from Bauer
    All data is from Bauer Table 3
    
    :param data_i: int, tells which data set to select
    :param scale_factor: double, multiplies all the experimental params by a scale factor, defaults to 1
    
    returns, all the exchange param values as a tuple (A, a1, a2, B, b1, b2)
    '''
    
    print("Bauer PbEuSe data set "+str(data_i)+" selected with scale factor "+str(scale_factor)+"." )

    if( data_i == 0):
    
        print("This data corresponds to x = 0.0142, T = 1.7 K.");
        A, a1, a2 = 0.032, 0.03, 0.03 - 0.032; # in eV
        B, b1, b2 = 0.0066, 0.0075, 0.0075 - 0.0066;
        
    elif( data_i == 1):
    
        print("This data corresponds to x = 0.024, T = 1.7 K.");
        A, a1, a2 = 0.0244, 0.02, 0.02 - 0.0244; # in eV
        B, b1, b2 = 0.006, 0.0025, 0.0025 - 0.006;    
    
    elif ( data_i == 2):
    
        print("This data corresponds to x = 0.024, T = 6 K.");
        A, a1, a2 = 0.024, 0.018,  0.018 - 0.024; # in eV
        B, b1, b2 = 0.0078, 0.0009, 0.0009 - 0.0078
          
    elif ( data_i == 3):
    
        print("This data corresponds to x = 0.024, T = 12 K.");
        #  x = 0.024, T = 12 K
        A, a1, a2 = 0.022, 0.0175,  0.0175 - 0.022; # in eV
        B, b1, b2 = 0.0097, 0.0022, 0.0022 - 0.0097;
        
    else: # should never get here unless data_i is wrong
        print("Error in GetExpData:")
        raise ValueError("Only 4 experimental datasets, data_i != 0, 1, 2, 3 unsupported.");
        
    # return tuple of all experimental params with the scale factor applied
    return A*scale_factor, a1*scale_factor, a2*scale_factor, B*scale_factor, b1*scale_factor, b2*scale_factor;


################################################################################
# define the benchmark hamiltonian
# this amounts to determing at what input values we want to call lower bands valence
# bands and higher bands conduction bands
# definitely something the user may want to change

# define the benchmark energy level
Eg_bench = 0.15; 

# define resst of bulk hamiltonian
H_bench_inputs = (Eg_bench, mu_Bohr, B_vec, vt, vl); #uses baseline vals, but user is free to redefine
H_bench = hamiltonian.Hamiltonian(*H_bench_inputs)


################################################################################
# make plots of the energy levels vs band gap
Temp = [1.7, 1.7, 6, 12 ];
# loop over all four data sets
for data_i in [0,1,2,3 ]:
    
    # loop through scaling
    for scale_factor in [1]: #, 10, 50, 100]:

        
        # get values for exchange params from Bauer data set
        #scale_factor = 50; # set a multiplicative factor to scale up exchange params if desired
        A, a1, a2, B, b1, b2 = GetExpData(data_i, scale_factor = scale_factor);
        
        # plot resulting levels for the central valley
        Eg_lim = -0.1, 0.1; # limits of the domain of the band gap
        E_inputs = (0, a1, a2, b1, b2, long_gap_shift ); # Exchange inputs for Eg sweep, phi is just a placeholder
        
        # function below plots energy levels against gap for both valleys
        # tell code we are not plotting against x with the fololowing tuple
        x_inputs = (False, False, False, False );
        
        # if both = true, will plot valleys on same axis, otherwise separates them
        GetEnergyLevels.EgSweepBothValleys(H_bench_inputs, E_inputs, Eg_lim, MATERIAL, Eg_bench, x_inputs, both = True);
        
        # run as above but with x as independent var
        # define input params for plotting against x instead of Eg
        vs_x = True; #tells to plot against x 
        x_lim = (0,0.5); # sets limits of x
        temperature = Temp[data_i] # temperature in K inherits from what we used above, or we can redefine
        Eg_of_x = Eg_func; # function to convert from x to gap
        x_inputs = (vs_x, x_lim, temperature, Eg_of_x ); 
        
        # find and plot levels
        GetEnergyLevels.EgSweepBothValleys(H_bench_inputs, E_inputs, Eg_lim, MATERIAL, Eg_bench, x_inputs, both = False);
    
    
        # plot transition energies for same data
        # see EgSweepTransition docstring for more info on what is meant by transition energies
        # plots for both valleys
        GetEnergyLevels.EgSweepTransition(H_bench_inputs, E_inputs, Eg_lim, MATERIAL, Eg_bench);

    








