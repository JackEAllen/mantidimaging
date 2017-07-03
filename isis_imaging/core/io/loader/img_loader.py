from __future__ import absolute_import, division, print_function

import numpy as np

from isis_imaging import helper as h
from isis_imaging.core.parallel import two_shared_mem as ptsm
from isis_imaging.core.parallel import utility as pu

from isis_imaging.core.io.utility import get_file_names

"""
This module handles the loading of FIT, FITS, TIF, TIFF
"""


def execute(load_func, input_file_names, input_path_flat, input_path_dark,
            img_format, data_dtype, cores, chunksize, parallel_load, indices):
    """
    Reads a stack of images into memory, assuming dark and flat images
    are in separate directories.

    If several files are found in the same directory (for example you
    give image0001.fits and there's also image0002.fits,
    image0003.fits) these will also be loaded as the usual convention
    in ImageJ and related imaging tools, using the last digits to sort
    the images in the stack.

    Usual type in fits is 16-bit pixel depth, data type is denoted with:
        '>i2' - uint16
        '>f2' - float16
        '>f4' - float32

    :param load_func: function to be used to load the files

    :param input_file_names: path to sample images. Can be a file or directory

    :param input_path_flat: (optional) path to open beam / flat image(s).
                            Can be a file or directory

    :param input_path_dark: (optional) path to dark field image(s).
                            Can be a file or directory

    :param img_format: file extension (supported tiff, tif, fits, or fit)

    :param data_dtype: Recommended: float32. The data type in which
                       the data will be convert to after loading

    :param cores: Cores to be used for parallel loading

    :param chunksize: Chunk of work that each worker will receive

    :param parallel_load: Do the loading with parallel processes.

    :param indices: Which files will be loaded

    :return: sample, average flat image, average dark image
    """

    # Assumed that all images have the same size and properties as the first.
    first_sample_img = load_func(input_file_names[0])

    if indices:
        input_file_names = input_file_names[indices[0]:indices[1]:indices[2]]

    # get the shape of all images
    img_shape = first_sample_img.shape

    # forward all arguments to internal class
    l = ImageLoader(load_func, input_file_names, input_path_flat, input_path_dark,
                    img_format, img_shape, data_dtype, cores, chunksize, parallel_load, indices)
    # we load the flat and dark first, because if they fail we don't want to
    # fail after we've loaded a big stack into memory
    # this removes the image number dimension, if we loaded a stack of images

    flat_avg = l.load_and_avg_data(input_path_flat, "Flat")

    dark_avg = l.load_and_avg_data(input_path_dark, "Dark")

    sample_data = l.load_sample_data(input_file_names)

    return sample_data, flat_avg, dark_avg


class ImageLoader(object):
    def __init__(self, load_func, input_file_names, input_path_flat, input_path_dark,
                 img_format, img_shape, data_dtype, cores, chunksize, parallel_load, indices):
        self.load_func = load_func
        self.input_file_names = input_file_names
        self.input_path_flat = input_path_flat
        self.input_path_dark = input_path_dark
        self.img_format = img_format
        self.img_shape = img_shape
        self.data_dtype = data_dtype
        self.cores = cores
        self.chunksize = chunksize
        self.parallel_load = parallel_load
        self.indices = indices

    def load_sample_data(self, input_file_names):
        # determine what the loaded data was
        if len(self.img_shape) == 2:  # the loaded file was a single image
            sample_data = self.load_files(input_file_names, "Sample")
        elif len(self.img_shape) == 3:  # the loaded file was a file containing a stack of images
            from isis_imaging.core.io import stack_loader
            sample_data = stack_loader.execute(input_file_names[0], "Sample")
        else:
            raise ValueError(
                "Data loaded has invalid shape: {0}", self.img_shape)

        return sample_data

    def load_and_avg_data(self, file_path, prog_prefix=None):
        if file_path:
            file_names = get_file_names(file_path, self.img_format)

            data = self.load_files(file_names, prog_prefix)
            return _get_data_average(data)

    def _do_files_load_seq(self, data, files, name):
        h.prog_init(len(files), desc=name)
        for idx, in_file in enumerate(files):
            try:
                data[idx, :, :] = self.load_func(in_file)[:]
                h.prog_update()
            except ValueError as exc:
                raise ValueError(
                    "An image has different width and/or height dimensions! "
                    "All images must have the same dimensions. "
                    "Expected dimensions: {0} Error message: {1}".format(self.img_shape, exc))
            except IOError as exc:
                raise RuntimeError("Could not load file {0}. Error details: {1}".
                                   format(in_file, exc))
        h.prog_close()

        return data

    def _do_files_load_par(self, data, files, name):
        f = ptsm.create_partial(
            _par_inplace_load_fwd_func, ptsm.inplace, load_func=self.load_func)
        ptsm.execute(data, files, f, self.cores, self.chunksize, name)
        return data

    def load_files(self, files, name=None):
        # Zeroing here to make sure that we can allocate the memory.
        # If it's not possible better crash here than later.
        data = pu.create_shared_array(
            (len(files), self.img_shape[0], self.img_shape[1]), dtype=self.data_dtype)

        if self.parallel_load:
            return self._do_files_load_par(data, files, name)
        else:
            return self._do_files_load_seq(data, files, name)


def _par_inplace_load_fwd_func(data, filename, load_func=None):
    data[:] = load_func(filename)


def _get_data_average(data):
    return np.mean(data, axis=0)
