"""
This script is used to attempt to rotate lrt stations such that they are alligned
with and declared correct orientation. The inputed direction can be either a 
declination & inclination pair or a group of X, Y, and Z measurments
"""
import argparse
import logging
# Third party packages
import numpy as np
import pandas as pd

def rotate(data1, data2, make_plot=False, entire=False):
    '''
    Rotates data1 to be in the same orientation of data2

    :type data1: List of [np.array, np.array, np.array]
    :param data1: data to be rotated

    :type data2: Either like data1 or list of [declination, inclination]
    :param data2: reference point assumed to be correct orientaion

    :type make_plot: Boolean
    :param make_plot: Show plot of data at completion

    :type entire: Boolean
    :param entire: Rotate each point individualy
    '''
    
    pass

def create_rot_matrix(desired, current)

    cross = np.cross(desired, current)

    sin_phi = np.linalg.norm(cross)
    cos_phi = np.dot(desired, current)

    scew_sym_matrix = np.array([
        [0, -cross[2], cross[1]],
        [ cross[2], 0, cross[0]],
        [-cross[1], cross[0], 0]])

    scew_sym_matrix_sqr = np.linalg.matrix_power(cew_sym_matrix, 2)

    I = np.array([
       [1, 0, 0],
       [0, 1, 0],
       [0, 0, 1]])

    R = I + 
        scew_sym_matrix + 
        scew_sym_matrix_sqr*(1-cos_phi)/(sin_phi)**2

        

def main():
    '''Main routine'''
    
    parser = argparse.ArgumentParser(
        description="Rotate lrt site to desired format")
    parser.add_argument(
        '-e', '--entire',
        action='store_true', help='Rotate each point individualy')
    parser.add_argument(
        '-p', '--plot',
        action='store_true', help='Display plot')
    parser.add_argument(
        '-d',
        help='Data to be rotated location')
    parser.add_argument(
        '-dd',
        help='Data to be rotated to location')
    args = parser.parse_args()

    data1 = pd.read_fwf(args.d, header=None,
                        names=['year', 'time', 'doy', 
                               'x', 'y', 'z', 'f*', 'f'])
    data2 = pd.read_fwf(args.dd, header=None,
                        names=['loc', 'year', 'time', 
                               'x', 'y', 'z', 'f']) 

    data1 = [data1.x,
             data1.y,
             data1.z,
             data1.f]
    data2 = [data2.x,
             data2.y,
             data2.z,
             data2.f]

    rotate(data1, data2, getattr(args, 'plot'), getattr(args, 'entire'))

if __name__ == '__main__':
    main()
