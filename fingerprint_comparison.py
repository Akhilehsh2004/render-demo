import cv2
from skimage.metrics import structural_similarity as compare_ssim

def preprocess_fingerprint(image_path):
    """
    Preprocess the fingerprint image for comparison.
    Converts the image to grayscale, applies Gaussian blur, and thresholds it.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Error: Unable to load the image at '{image_path}'. Check the file path.")

    image_blur = cv2.GaussianBlur(image, (5, 5), 0)
    _, image_thresh = cv2.threshold(image_blur, 127, 255, cv2.THRESH_BINARY_INV)
    return image_thresh

def compare_fingerprints(image1_path, image2_path):
    """
    Compare two fingerprint images and return the similarity score.
    Resizes images to a fixed size and calculates structural similarity.
    """
    img1 = preprocess_fingerprint(image1_path)
    img2 = preprocess_fingerprint(image2_path)

    img1 = cv2.resize(img1, (300, 300))
    img2 = cv2.resize(img2, (300, 300))

    score, _ = compare_ssim(img1, img2, full=True)
    return score, img1, img2
