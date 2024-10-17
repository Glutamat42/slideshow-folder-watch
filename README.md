# Diashow Script

## Overview
This script is designed to create a slideshow of images from a specified folder, displaying them in fullscreen mode on a selected screen. It automatically updates the slideshow when new images are added or removed from the folder.

## Requirements
Install the required packages using:
```sh
pip install -r requirements.txt
```


## Configuration
The script uses a configuration dictionary to set the following parameters:
- `screen_id`: The ID of the screen to use for displaying images.
- `folder_path`: The path to the folder containing images.
- `display_duration`: The time to display each image in seconds.

## Usage
1. **Set Configuration**: Update the `config` dictionary in `main.py` with the appropriate values for your setup.
2. **Run the Script**: Execute `main.py` to start the slideshow.

## User Inputs
- **Spacebar**: Pause/Resume the slideshow.
- **Esc or q**: Quit the slideshow.
- **Left Arrow**: Display the previous image.
- **Right Arrow**: Display the next image.