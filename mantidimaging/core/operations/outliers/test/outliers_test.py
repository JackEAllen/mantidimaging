import unittest
from unittest import mock

import numpy as np

import mantidimaging.test_helpers.unit_test_helper as th
from mantidimaging.core.operations.outliers import OutliersFilter
from mantidimaging.core.operations.outliers.outliers import OUTLIERS_BRIGHT, DIM_2D


class OutliersTest(unittest.TestCase):
    """
    Test outliers filter.

    Tests return value only.
    """
    def __init__(self, *args, **kwargs):
        super(OutliersTest, self).__init__(*args, **kwargs)

    def test_executed(self):
        images = th.generate_images()

        radius = 8
        threshold = 0.1

        sample = np.copy(images.data)
        result = OutliersFilter.filter_func(images, threshold, radius, cores=1)

        th.assert_not_equals(result.data, sample)

    def test_execute_wrapper_return_is_runnable(self):
        """
        Test that the partial returned by execute_wrapper can be executed (kwargs are named correctly)
        """
        diff_field = mock.Mock()
        diff_field.value = mock.Mock(return_value=0)
        size_field = mock.Mock()
        size_field.value = mock.Mock(return_value=0)
        mode_field = mock.Mock()
        mode_field.currentText = mock.Mock(return_value=OUTLIERS_BRIGHT)
        apply_to_field = mock.Mock()
        apply_to_field.currentText = mock.Mock(return_value="Projections")
        median_filter_field = mock.Mock()
        median_filter_field.currentText = mock.Mock(return_value=DIM_2D)
        execute_func = OutliersFilter.execute_wrapper(diff_field, size_field, mode_field, apply_to_field,
                                                      median_filter_field)

        images = th.generate_images()
        execute_func(images)

        self.assertEqual(diff_field.value.call_count, 1)
        self.assertEqual(size_field.value.call_count, 1)
        self.assertEqual(mode_field.currentText.call_count, 1)
        self.assertEqual(apply_to_field.currentText.call_count, 1)
        self.assertEqual(median_filter_field.currentText.call_count, 1)


if __name__ == '__main__':
    unittest.main()
