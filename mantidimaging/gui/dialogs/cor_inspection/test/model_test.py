import unittest

import numpy.testing as npt

from mantidimaging.core.utility.data_containers import ScalarCoR, ReconstructionParameters
from mantidimaging.gui.dialogs.cor_inspection import CORInspectionDialogModel
from mantidimaging.gui.dialogs.cor_inspection.types import ImageType
from mantidimaging.test_helpers.unit_test_helper import generate_images


class CORInspectionDialogModelTest(unittest.TestCase):
    def test_construct(self):
        images = generate_images()
        m = CORInspectionDialogModel(images, 5, ScalarCoR(20), ReconstructionParameters('FBP_CUDA', 'ram-lak'))
        npt.assert_equal(m.sino, images.sino(5))
        self.assertEqual(m.cor_extents, (0, 9))
        self.assertEqual(m.proj_angles.value.shape, (10, ))

    def test_current_cor(self):
        images = generate_images()
        m = CORInspectionDialogModel(images, 5, ScalarCoR(20), ReconstructionParameters('FBP_CUDA', 'ram-lak'))
        m.centre_cor = 5
        m.cor_step = 1
        self.assertEqual(m.cor(ImageType.LESS), 4)
        self.assertEqual(m.cor(ImageType.CURRENT), 5)
        self.assertEqual(m.cor(ImageType.MORE), 6)

    def test_adjust_cor(self):
        images = generate_images()
        m = CORInspectionDialogModel(images, 5, ScalarCoR(20), ReconstructionParameters('FBP_CUDA', 'ram-lak'))
        m.centre_cor = 5
        m.cor_step = 1

        m.adjust_cor(ImageType.CURRENT)
        self.assertEqual(m.centre_cor, 5)
        self.assertEqual(m.cor_step, 0.5)

        m.adjust_cor(ImageType.LESS)
        self.assertEqual(m.centre_cor, 4.5)
        self.assertEqual(m.cor_step, 0.5)

        m.adjust_cor(ImageType.CURRENT)
        self.assertEqual(m.centre_cor, 4.5)
        self.assertEqual(m.cor_step, 0.25)

        m.adjust_cor(ImageType.MORE)
        self.assertEqual(m.centre_cor, 4.75)
        self.assertEqual(m.cor_step, 0.25)

        m.adjust_cor(ImageType.CURRENT)
        self.assertEqual(m.centre_cor, 4.75)
        self.assertEqual(m.cor_step, 0.125)
