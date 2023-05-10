import cv2
from skimage import io
import scipy
from skimage import measure, exposure, morphology
from skimage.util import img_as_ubyte
from skimage.filters import sobel, threshold_minimum
from skimage.color import rgb2gray


def CountVeins(img_path):
    image = img_as_ubyte(io.imread(img_path))
    # image = cv2.fastNlMeansDenoising(image)

    sigmoid_correct = exposure.adjust_sigmoid(image, cutoff=0.45, gain=15, inv=True)

    image_prep = cv2.subtract(image, sigmoid_correct)

    gray = rgb2gray(image_prep)

    thresh = threshold_minimum(gray)
    binary = gray >= thresh

    edges = sobel(binary)

    cleaned = scipy.ndimage.binary_fill_holes(edges)

    cleaned = morphology.remove_small_objects(cleaned, min_size=128, connectivity=1)

    contours = measure.find_contours(cleaned, 0.8)

    print(len(contours))

    return len(contours)


CountVeins("test2.jpg")
