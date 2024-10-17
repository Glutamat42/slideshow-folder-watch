import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import cv2
import numpy as np
import screeninfo

config = {
    'screen_id': 1,  # ID of the screen to use
    'folder_path': 'C:/Users/Markus/privat/testbilder',  # Path to the folder containing images
    'display_duration': 2  # Time to display each image in seconds
}

class FileSystemImageWatcher(FileSystemEventHandler):
    """
    Handles file system events in the watched folder.
    """
    def __init__(self, image_queue):
        self.image_queue = image_queue

    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.event_type == 'deleted':
            if event.src_path in self.image_queue:
                self.image_queue.remove(event.src_path)
        if event.event_type == 'created' and event.src_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            if event.src_path not in self.image_queue:
                self.image_queue.append(event.src_path)

        self.image_queue.sort(key=os.path.getctime)


def load_and_resize_image(image_path, screen_id):
    """
    Loads an image from the given path and resizes it to fit the screen while maintaining aspect ratio.

    Args:
        image_path (str): The path to the image file.
        screen_id (int): The ID of the screen to use.

    Returns:
        numpy.ndarray: The resized image.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"Image at path {image_path} could not be loaded.")

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

def display_fullscreen_image(image, screen_id, paused=False):
    """
    Displays the given image in fullscreen mode on the specified screen.
    Optionally displays a pause symbol if paused is True.

    Args:
        image (numpy.ndarray): The image to display.
        screen_id (int): The ID of the screen to use.
        paused (bool, optional): Whether to display the pause symbol. Defaults to False.
    """
    screen = screeninfo.get_monitors()[screen_id]
    screen_width, screen_height = screen.width, screen.height

    padded_image = np.full((screen_height, screen_width, 3), (0, 0, 0), dtype=np.uint8)
    y_offset = (screen_height - image.shape[0]) // 2
    x_offset = (screen_width - image.shape[1]) // 2
    padded_image[y_offset:y_offset + image.shape[0], x_offset:x_offset + image.shape[1]] = image

    if paused:
        # Draw a simple pause symbol (two vertical bars)
        bar_width = 20
        bar_height = 100
        bar_spacing = 30
        bar_x = 10
        bar_y = 10
        cv2.rectangle(padded_image, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), -1)
        cv2.rectangle(padded_image, (bar_x + bar_width + bar_spacing, bar_y),
                      (bar_x + bar_width * 2 + bar_spacing, bar_y + bar_height), (255, 255, 255), -1)

    window_name = 'projector'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, padded_image)
    cv2.waitKey(5)  # Add this line back, but with a short delay

def handle_user_input(current_image_index, paused, iteration_count):
    """
    Handles user input for pausing, quitting, and navigating images.

    Args:
        current_image_index (int): The index of the current image.
        paused (bool): Whether the slideshow is paused.
        iteration_count (int): The current iteration count.

    Returns:
        tuple: Updated values for current_image_index, paused, iteration_count, and user_image_change.
    """
    key = cv2.waitKeyEx(5)
    user_image_change = False  # Initialize the flag here
    if key == ord(' '):
        paused = not paused
        iteration_count = 0
    elif key == 27 or key == ord('q'):
        cv2.destroyAllWindows()
        exit()
    elif key == 2424832:  # Left arrow key
        current_image_index = (current_image_index - 1) % len(image_queue)
        iteration_count = 0
        user_image_change = True
    elif key == 2555904:  # Right arrow key
        current_image_index = (current_image_index + 1) % len(image_queue)
        iteration_count = 0
        user_image_change = True

    return current_image_index, paused, iteration_count, user_image_change  # Return the flag


if __name__ == '__main__':
    image_queue = []
    # Add initial files to the queue
    for filename in os.listdir(config['folder_path']):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_queue.append(os.path.join(config['folder_path'], filename))
    image_queue.sort(key=os.path.getctime)

    event_handler = FileSystemImageWatcher(image_queue)
    observer = Observer()
    observer.schedule(event_handler, config['folder_path'], recursive=False)
    observer.start()

    current_image_index = 0
    paused = False
    iteration_count = 0

    try:
        while True:
            # Handle key presses and image switching
            current_image_index, paused, iteration_count, user_image_change = handle_user_input(
                current_image_index, paused, iteration_count
            )

            if paused:
                display_fullscreen_image(resized_image, config['screen_id'], paused=True)
            else:
                if iteration_count == 0:
                    image_path = image_queue[current_image_index]
                    resized_image = load_and_resize_image(image_path, config['screen_id'])
                    display_fullscreen_image(resized_image, config['screen_id'])
                    # Only automatically advance if the user didn't manually change the image
                    if not user_image_change:
                        current_image_index = (current_image_index + 1) % len(image_queue)

                iteration_count += 1
                if iteration_count >= config['display_duration'] * 10:
                    iteration_count = 0

            time.sleep(0.1)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()