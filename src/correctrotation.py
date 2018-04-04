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
import matplotlib.cm as cm
from matplotlib.colors import LogNorm

class DataAreNotSameLength(Exception):
    """ Custom Exception"""
    pass

def dec_inc_to_abs(dec_inc):
    """ Changes a declination inclination pair to a vector"""
    declination = dec_inc[0]
    inclination = dec_inc[1]

    x_axis = np.cos(inclination) * np.cos(declination)
    y_axis = np.cos(inclination) * np.sin(declination)
    z_axis = np.sin(inclination)

    return np.array([x_axis, y_axis, z_axis])

def create_rot_deg(dec, inc):
    """ Creates a rotation matrix from a dec, inc pair"""

    rotate_dec = np.array([[np.cos(dec), -np.sin(dec), 0],
                           [np.sin(dec), np.cos(dec), 0],
                           [0, 0, 1]])

    rotate_inc = np.array([[np.cos(inc), 0 , np.sin(inc)],
                           [0, 1, 0],
                           [-np.sin(inc), 0, np.cos(inc)]])

    rotate_tot = np.matmul(rotate_dec, rotate_inc)
    return rotate_tot

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

def rotate_to_abs(data1, data2, make_plot=False, 
                  entire=False, save_matrix=False, dec_inc=None):
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
    raw = np.copy(data1)
    if  dec_inc:
        # Change from dec/inc to absolute
        dec_inc = dec_inc_to_abs(dec_inc)

    if len(data2) == 4:
        data2[3] = np.sqrt(data2[0]**2 + data2[1]**2 + data2[2]**2)
        old_f_true = data2[3]

    if not type(data1) is np.ndarray or not  len(data1) == 3:
        # Change to np array of 3 columns
        raw = np.array([raw[0], raw[1], raw[2]])
        data2 = np.array([data2[0], data2[1], data2[2]])

    if entire:
        '''
        Data is given in the form [[x1... xn], [y1... yn], [z1... zn]]
        and we need the form of [[x1 y1 z1]... [xn yn zn]]
        so we transpose the data
        '''
        data1 = np.copy(raw).transpose()
        data2 = data2.transpose()

        if not len(data1) == len(data2):
            raise DataAreNotSameLength(('Length (%s)'%(len(data1)) +
                                        'does not match (%s)'%(len(data2))))
        if save_matrix:        
            with open('savevars.txt', 'w') as db:
                for iterate in range(len(data1)):
                    if dec_inc:
                        rot_matrix = create_rot_matrix(dec_inc, 
                                                       data1[iterate])
                    else:
                        rot_matrix = create_rot_matrix(data2[iterate], 
                                                       data1[iterate])

                    data1[iterate] = np.matmul(data1[iterate], rot_matrix)
                    db.write('{:.5f} {:.5f} {:.5f}\n'.format(rot_matrix[0,1], 
                                                             rot_matrix[0,2],
                                                             rot_matrix[1,2]))
        else:
            for iterate in range(len(data1)):
                if dec_inc:
                    rot_matrix = create_rot_matrix(dec_inc, 
                                                   data1[iterate])
                else:
                    rot_matrix = create_rot_matrix(data2[iterate], 
                                                       data1[iterate])
                data1[iterate] = np.matmul(data1[iterate], rot_matrix)

        # Return to original formatting
        data1 = data1.transpose()
        data2 = data2.transpose()

    if True:
        # I.e. rotate using daily average
        if dec_inc:
            rot_matrix = create_rot_matrix(dec_inc, 
                                           np.array([raw[0].mean(),
                                                     raw[1].mean(),
                                                     raw[2].mean()]))
        else:
            rot_matrix = create_rot_matrix(
                np.array([data2[0].mean(),
                          data2[1].mean(),
                          data2[2].mean()]),
                np.array([raw[0].mean(),
                          raw[1].mean(),
                          raw[2].mean()])
                )

        data3 = np.matmul(raw.transpose(), rot_matrix).transpose()

    if make_plot:
        names = ['X-X Diff', 'Y-Y Diff', 'Z-Z Diff']
        x = np.arange(len(data1[0])) / 3600


        fig, ax = plt.subplots(3, figsize=(15, 45))
        for iterate in range(3):
            ax[iterate].plot(x, (data2[iterate] - data1[iterate]) +
                                 data3[iterate] - data2[iterate],
                             label='final change')
        plt.show()

def rotate_by_deg(data1, dec, inc, plot=False, ref_data=None, 
                  iterate=None, axis_equality=False):
    """ Rotates data1 by dec, inc, in radians"""
   
    if not type(data1) is np.ndarray or not  len(data1) == 3:
        # Change to np array of 3 columns
        data1 = np.array([data1[0], data1[1], data1[2]])

    raw = np.copy(data1)
    if iterate:
        num_bins = iterate
        dec_rot = np.linspace(dec, -dec, num_bins)
        inc_rot = np.linspace(inc, -inc, num_bins)
        intensity = np.array([[], [], []])
        intensity_here = [0, 0, 0]

        for rot_inc in inc_rot:
            for rot_dec in dec_rot:
                rot_matrix = create_rot_deg(rot_dec, 0)
                data = np.matmul(raw.transpose(), rot_matrix).transpose()
                rot_matrix = create_rot_deg(0, rot_inc)
                data = np.matmul(data.transpose(), rot_matrix).transpose()

                diff = np.copy(ref_data)

                for axis in range(3):
                    diff[axis] = diff[axis] - data[axis]
                    intensity_here[axis] = diff[axis].mean()

                intensity = np.append(intensity, 
                                      [[intensity_here[0]],
                                       [intensity_here[1]],
                                       [intensity_here[2]]],
                                      axis=1
                                       )
        if axis_equality:
            for i in range(3):
                intensity[i] = intensity[i]/np.max(np.abs(intensity[i]))
            intensity = np.sqrt(intensity[0]**2 +
                                intensity[1]**2 +
                                intensity[2]**2)
            intensity = intensity/np.max(np.abs(intensity))

        else:
            print(intensity)
            intensity = np.sqrt(intensity[0]**2 +
                                intensity[1]**2 +
                                intensity[2]**2)
        intensity = np.absolute(intensity).reshape(num_bins, num_bins)

        plt.imshow(intensity, extent=(np.amin(dec_rot), np.amax(dec_rot),
                                      np.amin(inc_rot), np.amax(inc_rot)),
                   norm=LogNorm(), cmap=cm.jet)
        plt.colorbar()
        plt.scatter(0, 0, marker='+')
        plt.show()
                    


    else:
        rot_matrix = create_rot_deg(dec, inc)
        data1 = np.matmul(data1.transpose(), rot_matrix).transpose()

        if plot:
            x = np.arange(len(data1[0])) / 3600
            fig, ax = plt.subplots(3, figsize=(15, 45))
            plt.title(str(dec)+str(inc))
            mean1=0
            mean2=0
            for iterate in range(3):
                ax[iterate].plot(x, data1[iterate], label='rotated')
                ax[iterate].plot(x, raw[iterate], label='raw')
                ax[iterate].plot(x, ref_data[iterate], label='ott')
                ax[iterate].legend()
                mean1 +=((data1[iterate]-ref_data[iterate]).mean())
                mean2 +=((raw[iterate]-ref_data[iterate]).mean())
            print(mean1)
            print(mean2)
            plt.show()


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
        '-s', '--savematrix',
        action='store_true', help='Save each matrix created variables')
    parser.add_argument(
        '-N', '--numberbins',
        default=0,
        type=int,
        help='Number of bins to use in density plot')
    parser.add_argument(
        '-dec', '--declination',
        type=float,
        default=None,
        help='Declination to use if rotating by angles')
    parser.add_argument(
        '-inc', '--inclination',
        type=float,
        default=None,
        help='Inclination to use if rotating by angles')
    parser.add_argument(
        '-d', '--day') 
    # TODO: add day commands
    parser.add_argument(
        '-dir1',
        default='/home/dcalp/lrt/LRE/RT1Hz/',
        help='Data to be rotated')
    parser.add_argument(
        '-dir2',
        default='/home/akovachi/lrt_data/ottSecData/2018/',
        help='Data to be rotated to location')
    args = parser.parse_args()

    allFiles1 = []
    allFiles2 = []
    for day, doy in zip(['19'],['078']):
        allFiles1.append(args.dir1+'LRE201803%svsec.sec'%(day))
        allFiles2.append(args.dir2+'OTT2018%s.sec'%(doy))
    
    df_from_each_file = (pd.read_fwf(
        f, names=['date', 'time', 'doy','x', 'y', 'z', 'f']) for f in allFiles1)
    data1 = pd.concat(df_from_each_file, ignore_index=True)
    df_from_each_file = (pd.read_fwf(
        f, names=['loc', 'year', 'time' ,'x', 'y', 'z', 'f']) for f in allFiles2)
    data2 = pd.concat(df_from_each_file, ignore_index=True)
    data1 = [data1.x,
             data1.y,
             data1.z,
             data1.f]
    data2 = [data2.x,
             data2.y,
             data2.z,
             data2.f]

    rotate_by_deg(data1,
                  dec=getattr(args,'declination'),
                  inc=getattr(args,'inclination'), 
                  plot=True,
                  ref_data=data2,
                  iterate=getattr(args, 'numberbins'),
                  axis_equality=False) 
    #rotate(data1,
    #       data2, 
    #       getattr(args, 'plot'), 
    #       getattr(args, 'entire'),
    #       getattr(args, 'savematrix'),
    #       None)


if __name__ == '__main__':
    main()
