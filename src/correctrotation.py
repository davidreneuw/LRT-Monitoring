"""
This script is used to attempt to rotate lrt stations such that they are alligned
with and declared correct orientation. The inputed direction can be either a
declination & inclination pair or a group of X, Y, and Z measurments
"""
import argparse
import os.path
# Third party packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LogNorm

CURRENT_OFFSET = [17593.342, -4278.744, 50860.816]
USER = os.path.expanduser('~')

class DataAreNotSameLength(Exception):
    """ Custom Exception"""
    pass

#def intensity(reference, data):
def dec_inc_to_abs(dec_inc):
    """ Changes a declination inclination pair to a vector"""
    declination = dec_inc[0]
    inclination = dec_inc[1]

    x_axis = np.cos(inclination) * np.cos(declination)
    y_axis = np.cos(inclination) * np.sin(declination)
    z_axis = np.sin(inclination)

    return np.array([x_axis, y_axis, z_axis])

def create_rot_deg(dec, inc, anc=0):
    """ Creates a rotation matrix from a dec, inc pair"""

    rotate_dec = np.array([[np.cos(dec), -np.sin(dec), 0],
                           [np.sin(dec), np.cos(dec), 0],
                           [0, 0, 1]])

    rotate_inc = np.array([[np.cos(inc), 0, np.sin(inc)],
                           [0, 1, 0],
                           [-np.sin(inc), 0, np.cos(inc)]])

    rotate_anc = np.array([[1, 0, 0],
                           [0, np.cos(anc), -np.sin(anc)],
                           [0, np.sin(anc), np.cos(anc)]])

    rotate_tot = np.matmul(rotate_dec, rotate_inc)
    rotate_tot = np.matmul(rotate_tot, rotate_anc)
    return rotate_tot

def create_rot_matrix(desired, current):
    """ 
    Creates a rotation matrix from two vectors by using a skew symetric matrix and dot
    and cross product
    Read more here: https://en.wikipedia.org/wiki/Skew-symmetric_matrix#Infinitesimal_rotations
    
    :type desired: len(3) np.array
    :param desired: the orientation we would like to rotate to
    
    :type current: len(3) np.array
    :param current: the current vector that we would like to create a roation for
    """

    # Create unit vector
    desired = desired/np.linalg.norm(desired)
    current = current/np.linalg.norm(current)

    # Create needed terms
    cross = np.cross(desired, current)
    sin_phi = np.linalg.norm(cross)
    cos_phi = np.dot(desired, current)
    
    # Create skew-symmetric matrix
    scew_sym_matrix = np.array([
        [0, -cross[2], cross[1]],
        [cross[2], 0, -cross[0]],
        [-cross[1], cross[0], 0]])
    # Skew symmetric matrix squared
    scew_sym_matrix_sqr = np.linalg.matrix_power(scew_sym_matrix, 2)

    identity = np.array([[1, 0, 0],
                         [0, 1, 0],
                         [0, 0, 1]])

    # Create rotation matrix
    rot_matrix = (identity +
                  scew_sym_matrix +
                  scew_sym_matrix_sqr*(1-cos_phi)/(sin_phi)**2)

    return rot_matrix

def calc_accuracy(data1, data2):
    """ 
    Determines the accuracy of one plot to resemble another
    
    :type data1: len(3>) np.array)
    :param data1: data set 1 that will be compared
    
    :type data2: len(3>) np.array
    :param data2: data set 2 that will be compared
    """
    accuracy_here = np.array([0, 0, 0])
    for axis in range(3):
        temp = data2[axis] - data1[axis] 
        accuracy_here[axis] = np.abs(temp).mean() 
    return np.sqrt(accuracy_here[0]**2 +
                   accuracy_here[1]**2 +
                   accuracy_here[2]**2)

def calc_range_dif(data1, data2):
    """ 
    Given two data sets, subtracts them and returns the range of
    the subtraction
    
    :type data1: len(N) np.array
    :param data1: data set 1 to be compared
    
    :type data2: len(N) np.array
    :param data2: data set 2 to be compared
    >>> calc_range_dif(np.array([1,2,3]), np.array([1,0,3])
    >>> 1
    >>> calc_range_dif(np.array([5,2,7]), np.array([2,2,10])
    >>> 6
    """
    temp = data2-data1
    return (np.amax(temp) - np.amin(temp))

def rotate_to_abs(data1, data2, make_plot=False,
                  entire=False, dec=None, inc=None):
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
    
    # Create copy of data
    raw = np.copy(data1)
    if  dec:
        # Change from dec/inc to absolute
        dec_inc = dec_inc_to_abs([dec, inc])

    if not type(data1) is np.ndarray or not  len(data1) == 3:
        # Change to np array of 3 columns
        raw = np.array([raw[0], raw[1], raw[2]])
        data2 = np.array([data2[0], data2[1], data2[2]])

    if entire:
        '''
        If entire is true preform roation on each [x, y, z] triplet of data
        
        Data is given in the form [[x1... xn], [y1... yn], [z1... zn]]
        and we need the form of [[x1 y1 z1]... [xn yn zn]]
        so we transpose the data
        '''
        data1 = np.copy(raw).transpose()
        data2 = data2.transpose()

        if not len(data1) == len(data2):
            raise DataAreNotSameLength(('Length (%s)'%(len(data1)) +
                                        'does not match (%s)'%(len(data2))))
        for iterate in range(len(data1)):
            if dec:
                rot_matrix = create_rot_matrix(dec_inc,
                                               data1[iterate])
            else:
                rot_matrix = create_rot_matrix(data2[iterate],
                                               data1[iterate])

            data1[iterate] = np.matmul(data1[iterate], rot_matrix)

        # Return to original formatting
        data1 = data1.transpose()
        data2 = data2.transpose()

    else:
        # I.e. rotate using daily average
        if dec:
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
        """ This option is mostly for debugging to make sure
        that the data is being rotated correctly"""
        names = ['X-X Diff', 'Y-Y Diff', 'Z-Z Diff']
        x = np.arange(len(data1[0])) / 3600


        fig, ax = plt.subplots(3, figsize=(15, 45))
        for iterate in range(3):
            ax[iterate].plot(x, (data3[iterate]))
            ax[iterate].plot(x, (data2[iterate]))
        plt.show()

def rotate_by_deg(data1, dec, inc, anc=0, plot=False, ref_data=None,
                  iterate=None, axis_equality=False, search_best=False):
    """ 
    Rotates data1 by dec, inc, in radians. The param anc is a rotation about
    the x axis and was used mostly to see if it could provide an improved rotation
    for this reason it defaults to 0 and can almost always be ignored
    
    :type data1: len(3) np.array
    :param data1: data that will be rotated
    :type dec: float
    :param dec: angle in radians to rotate about z-axis
    :type inc: float
    :param inc: angle in radians to rotate about y-axis
    :type anc: float
    :params anc: angle in radians to rotate about x-axis"
    :type plot: Boolean
    :param plot: if true will output a plt.show() command
    :type ref_data: np.array
    :params ref_data: if given and the shape matches data1 it
                     can be used to compare with data1
    :type iterate: int
    :param iterate: used to determine accuracy when finding best rotation
    :type axis_equality: Boolean
    :param axis_eqaulity: if true then when finding accuracy each axis difference
                         will be normalized to 1. Not reccomened, bad results
    :type search_best: Boolean
    :param search_best: if true will attempt to find the best rotation"""

    if not type(data1) is np.ndarray or not  len(data1) == 3:
        # Change to np array of 3 columns
        data1 = np.array([data1[0], data1[1], data1[2]])

    raw = np.copy(data1)
    
    if iterate:
        # Creates the different rotations to be tested
        num_bins = iterate
        # These shapes are revered because imshow puts the bins starting in the
        # top left corner, so dec increases and inc decreases
        dec_rot = np.linspace(-dec, dec, num_bins)
        inc_rot = np.linspace(inc, -inc, num_bins)
        # Initiate the different arrays
        intensity = np.array([])
        intensity_here = [0, 0, 0]

        for rot_inc in inc_rot:
            for rot_dec in dec_rot:
                # Rotate data
                rot_matrix = create_rot_deg(rot_dec, rot_inc)
                data = np.matmul(raw.transpose(), rot_matrix).transpose()
                diff = np.copy(ref_data)

                accuracy = calc_accuracy(data, diff)
                intensity = np.append(intensity,
                                      accuracy,
                                      axis=0
                                     )

        # Reshape data to be in the correct bins
        intensity = np.absolute(intensity).reshape(num_bins, num_bins)

        if plot:
            plt.imshow(intensity, extent=(np.amin(dec_rot), np.amax(dec_rot),
                                          np.amin(inc_rot), np.amax(inc_rot)),
                       norm=LogNorm(), cmap=cm.jet)
            plt.xlabel('Declination(rad)')
            plt.ylabel('Inclination(rad)')
            plt.title('LRS plot accuracy')
            plt.colorbar()
            plt.scatter(0, 0, marker='+')
            plt.show()

    # Rotate and show the data
    else:
        rot_matrix = create_rot_deg(dec, inc, anc)
        data1 = np.matmul(data1.transpose(), rot_matrix).transpose()

        if plot:
            x = np.arange(len(data1[0])) / 3600
            
            fig, ax = plt.subplots(3, figsize=(15, 15))
            for iterate in range(3):
                ax[iterate].plot(x, (ref_data[iterate]-data1[iterate]),
                                 label='Diff', color='b')
                ax[iterate].legend(loc=1)
                ax[iterate].set_ylabel(axis[iterate])
            ax[2].set_xlabel('Time(h)')
            plt.show()
        else:
            return data1.transpose()

def find_best_tri_rot(data1, data2, inc_size, return_rotated=False):
    """
    Given two data sets it will return either best rotation to match
    the other data set or return the rotated data that best matches

    :type data1: numpy array
    :param data1: the data set that will be rotated
    :type data2: numpy array
    :param data2: the ideal data set we want to model
    :type inc_size: float
    :param inc_size: the inital increment size to rotate by. This is
                     halfed when an iteration does not improve
    :type return_rotated: Boolean
    :param return_rotated: returns rotated data if True
                           returns rotation if False
    """
    raw = np.copy(data1[:3]).transpose()
    # Declare inital conditions
    is_best_found = False
    current_accuracy = calc_accuracy(data1, data2)
    last_rotation = [0., 0., 0.]
    next_rotation = [0., 0., 0.]

    # Continue searching until best rotation is found
    # best is found when no improvement is made of n iterations
    while not is_best_found:
        for axis in range(3):

            # Try a positive rotation about the given axis
            add_rotation = list(next_rotation)
            add_rotation[axis] += inc_size

            # Try rotation and check accuracy
            rotation =  create_rot_deg(add_rotation[0],
                                       add_rotation[1],
                                       add_rotation[2])
            add_accuracy = calc_accuracy(np.matmul(raw, rotation).transpose(),
                                         data2)
            # Try a negative rotation about the given axis 
            neg_rotation = list(next_rotation)
            neg_rotation[axis] -= inc_size

            # Try rotation and check a c curacy
            rotation =  create_rot_deg(neg_rotation[0],
                                       neg_rotation[1],
                                       neg_rotation[2])
            neg_accuracy = calc_accuracy(np.matmul(raw, rotation).transpose(),
                                         data2)
            
            # See which rotation is best (previous, positive, negative)
            # If there is an improvement than that is the new default
            if (add_accuracy < current_accuracy and
                add_accuracy < neg_accuracy):
                next_rotation = list(add_rotation)
                current_accuracy = add_accuracy
            elif neg_accuracy < current_accuracy:
                next_rotation = list(neg_rotation)
                current_accuracy = neg_accuracy


        # If there was no improvement then divide the incrememt size by 2
        # Once the increment size is smaller than a limit return the
        # Current rotation as the best
        if last_rotation == next_rotation:
            inc_size = inc_size/2
            if inc_size < .0000001:
                best_rotation = next_rotation
                is_best_found = True
        last_rotation = list(next_rotation)

    if return_rotated:
        return rotate_by_deg(data1, best_rotation[0],
                                    best_rotation[1],
                                    best_rotation[2]).transpose()

    else: return best_rotation

def find_best_scalar(data1, data2, return_scaled=False):
    """
    Attempts to find the best scalar to multiply by the data1 to represent
    data2. Removes offset as the data was originally measured as only the offset
    so that is what we want to scale
    
    :type data1: nparray
    :param data1: data to be rescaled
    :type data2: nparray
    :param data2: data to be remodled as
    :type return_best: Boolean
    :param return_best: return the rescalled data if true
                        return the scallars if False    
    """
    raw = np.copy(data1[:3])
    best_scalar = [1, 1, 1]
    for axis in range(3):
        
        data1[axis] = data1[axis] - CURRENT_OFFSET[axis]
        data2[axis] = data2[axis] - CURRENT_OFFSET[axis]
        
        current_range = calc_range_dif(raw[axis], data2[axis]) 
        is_best_found = False
        increment = .001
        
        while not is_best_found:
            # Check positive scalar
            positive_scalar = best_scalar[axis] + increment
            positive_change = calc_range_dif(
                raw[axis]*(positive_scalar),
                data2[axis])
            # Check negative scalar
            negative_scalar = best_scalar[axis] - increment
            negative_change = calc_range_dif(
                raw[axis]*(negative_scalar),
                data2[axis])
            # Is either scalar better than the current
            if (positive_change < current_range and
                positive_change < negative_change):
                current_range = positive_change
                best_scalar[axis] = positive_scalar

            elif negative_change < current_range:
                current_range = negative_change
                best_scalar[axis] = negative_scalar
            # If not then the best scalar has been found
            else:
                is_best_found = True

    # Return either the scalar or the scaled data
    if return_scaled:
        for axis in range(3):
            data1[axis] = data1[axis]*best_scalar[axis] + CURRENT_OFFSET[axis]
        return data1[:3]
    else:
        return best_scalar



def main():
    """Main routine. Mostly used on a developer level. """

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
        '-m', '--mode',
        type=int, help='1-matrix, 2-dec/inc, 3-find best')
    parser.add_argument(
        '-N', '--numberbins',
        default=0,
        type=int,
        help='Number of bins to use in density plot')
    parser.add_argument(
        '-B', '--findbest',
        action='store_true', help='Find the optimal rotation')
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
        '-anc', '--anclination',
        type=float,
        default=0,
        help='Anclination to use if rotating by angles')
    parser.add_argument(
        '-f1', '--file1',
        nargs='+',
        help='Files to be parsed in dir1')
    parser.add_argument(
        '-f2', '--file2',
        nargs='+',
        help='Files to be parsed in dir2')
    parser.add_argument(
        '-dir1',
        default='/home/dcalp/lrt/LRS/RT1Hz/',
        help='Data to be rotated')
    parser.add_argument(
        '-dir2',
        default=(USER + '/cRio-data-reduction/ottSecData/2018/'),
        help='Data to be rotated to location')
    args = parser.parse_args()

    all_files1 = []
    all_files2 = []
    for file1, file2 in zip(args.file1, args.file2):
        all_files1.append(args.dir1+file1)
        all_files2.append(args.dir2+file2)

    df_from_each_file = (pd.read_fwf(
        f, names=['date', 'time', 'doy', 'x', 'y', 'z', 'f']) for f in all_files1)
    data1 = pd.concat(df_from_each_file, ignore_index=True)
    df_from_each_file = (pd.read_fwf(
        f, names=['loc', 'year', 'time', 'x', 'y', 'z', 'f']) for f in all_files2)
    data2 = pd.concat(df_from_each_file, ignore_index=True)
    data1 = [data1.x,
             data1.y,
             data1.z,
             data1.f]
    data2 = [data2.x,
             data2.y,
             data2.z,
             data2.f]

    if getattr(args, 'mode') == 0:
        rotate_to_abs(data1,
                      data2,
                      getattr(args, 'plot'),
                      getattr(args, 'entire'),
                      getattr(args, 'savematrix'),
                      getattr(args, 'declination'),
                      getattr(args, 'inclination'),
                     )

    elif getattr(args, 'mode') == 1:
        rotate_by_deg(data1,
                      getattr(args, 'declination'),
                      getattr(args, 'inclination'),
                      getattr(args, 'anclination'),
                      plot=True,
                      ref_data=data2,
                      iterate=getattr(args, 'numberbins'),
                      axis_equality=False,
                      search_best=getattr(args, 'findbest'))

    elif getattr(args, 'mode') == 2:
        find_best_tri_rot(data1,
                          data2,
                          .001)

if __name__ == '__main__':
    main()
