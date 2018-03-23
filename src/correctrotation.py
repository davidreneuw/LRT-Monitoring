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
import matplotlib.pyplot as plt

class DataAreNotSameLength(Exception):
    """ Custom Exception"""
    pass


def rotate(data1, data2, make_plot=False, entire=False):
    """
    Rotates data1 to be in the same orientation of data2

    :type data1: List of [np.array, np.array, np.array]
    :param data1: data to be rotated

    :type data2: Either like data1 or list of [declination, inclination]
    :param data2: reference point assumed to be correct orientaion

    :type make_plot: Boolean
    :param make_plot: Show plot of data at completion

    :type entire: Boolean
    :param entire: Rotate each point individualy
    """
    raw = data1
    if len(data2) == 2:
        # Change from dec/inc to absolute
        data2 = dec_inc_to_abs(data2)

    if not type(data1) is np.ndarray or not len(data1) == 3:
        # Change to np array of 3 columns
        data1 = np.array([data1[0], data1[1], data1[2]])
        data2 = np.array([data2[0], data2[1], data2[2]])

    if entire:
        '''
        Data is given in the form [[x1... xn], [y1... yn], [z1... zn]]
        and we need the form of [[x1 y1 z1]... [xn yn zn]]
        so we transpose the data
        '''
        data1 = data1.transpose()
        data2 = data2.transpose()

        if not len(data1) == len(data2):
            raise DataAreNotSameLength(('Length (%s)'%(len(data1)) +
                                        'does not match (%s)'%(len(data2))))

        for iterate in range(len(data1)):
            rot_matrix = create_rot_matrix(data2[iterate], data1[iterate])
            data1[iterate] = np.matmul(data1[iterate], rot_matrix)

        # Return to original formatting
        data1 = data1.transpose()
        data2 = data2.transpose()

    else:
        # I.e. rotate using daily average
        rot_matrix = create_rot_matrix(
            np.array([data2[0].mean(),
                      data2[1].mean(),
                      data2[2].mean()]),
            np.array([data1[0].mean(),
                      data1[1].mean(),
                      data1[2].mean()])
            )

        data1 = np.matmul(data1.transpose(), rot_matrix).transpose()

    if make_plot:
        for iterate in range(len(data1)):
            plt.plot(raw[iterate])
            plt.plot(data1[iterate])
            plt.plot(data2[iterate])
            plt.show()
    print(data1)

def dec_inc_to_abs(dec_inc):
    """ Changes a declination inclination pair to a vector"""
    declination = dec_inc[0]
    inclination = dec_inc[1]

    x_axis = np.cos(inclination) * np.cos(declination)
    y_axis = np.cos(inclination) * np.sin(declination)
    z_axis = np.sin(inclination)

    return np.array([x_axis, y_axis, z_axis])

def create_rot_matrix(desired, current):
    """ Creates a rotation matrix from two vectors"""

    # Create unit vector
    desired = desired/np.linalg.norm(desired)
    current = current/np.linalg.norm(current)

    # Create needed terms
    cross = np.cross(desired, current)

    sin_phi = np.linalg.norm(cross)
    cos_phi = np.dot(desired, current)

    scew_sym_matrix = np.array([
        [0, -cross[2], cross[1]],
        [cross[2], 0, -cross[0]],
        [-cross[1], cross[0], 0]])

    scew_sym_matrix_sqr = np.linalg.matrix_power(scew_sym_matrix, 2)

    identity = np.array([[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]])

    # Create rotation matrix
    rot_matrix = (identity +
                  scew_sym_matrix +
                  scew_sym_matrix_sqr*(1-cos_phi)/(sin_phi)**2)

    return rot_matrix

def main():
    """Main routine"""

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
