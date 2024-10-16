import numpy as np
import cv2
import screeninfo
import time

def load_and_resize_image(image_path):
    """
    Loads an image from the given path and resizes it to fit the screen while maintaining aspect ratio.

    Args:
        image_path (str): The path to the image file.

    Returns:
        numpy.ndarray: The resized image.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Image at path {image_path} could not be loaded.")

    screen_id = 1
    screen = screeninfo.get_monitors()[screen_id]
    screen_width, screen_height = screen.width, screen.height

    img_height, img_width = image.shape[:2]
    screen_aspect = screen_width / screen_height
    img_aspect = img_width / img_height

    if screen_aspect > img_aspect:
        new_height = screen_height
        new_width = int(new_height * img_aspect)
    else:
        new_width = screen_width
        new_height = int(new_width / img_aspect)

    resized_image = cv2.resize(image, (new_width, new_height))
    return resized_image

def display_fullscreen_image(image, screen_id=1):
    """
    Displays the given image in fullscreen mode on the specified screen.

    Args:
        image (numpy.ndarray): The image to display.
        screen_id (int, optional): The ID of the screen to display the image on. Defaults to 0.
    """
    screen = screeninfo.get_monitors()[screen_id]
    screen_width, screen_height = screen.width, screen.height

    padded_image = np.full((screen_height, screen_width, 3), (0, 0, 0), dtype=np.uint8)
    y_offset = (screen_height - image.shape[0]) // 2
    x_offset = (screen_width - image.shape[1]) // 2
    padded_image[y_offset:y_offset + image.shape[0], x_offset:x_offset + image.shape[1]] = image

    window_name = 'projector'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, padded_image)
    cv2.waitKey(1)  # Display the image for a short time to update the window

if __name__ == '__main__':
    image_paths = [
        'C:/Users/Markus/privat/testbilder/WIN_20241015_16_09_56_Pro.jpg',
        'C:/Users/Markus/privat/testbilder/WIN_20241016_23_47_36_Pro.jpg'
    ]

    while True:
        for image_path in image_paths:
            resized_image = load_and_resize_image(image_path)
            display_fullscreen_image(resized_image)
            time.sleep(3)