# ImageProcessingScripts

## About

ImageProcessingScripts is a set of scripts designed to make processing of large datasets of images simpler, so that we can spend less time processing data and more time training diffusion models.

It is currently a very immature set of scripts but will be improved over time.

Before running, you'll need to install the dependencies:

```bash
cd scripts
pip install -r requirements.txt
```

## How to use

### cropandresize.py

This script basically does what it says on the tin. In order to get consistent buckets for training flux, it:

- Finds the focal point of each image
- Crops the image to a desirable aspect ratio (currently 1:1, 3:2 or 2:3)
- Resizes the images using a high quality resizing algo (LANCZOS4) to specific bucket sizes

To use this script, just download your images to the `raw` folder, and then:

```bash
cd scripts
python cropandresize.py
```

You should find the cropped and resized images in the `img` folder, ready for the next step.

### autocaption.py

This script uses a VLM to automatically caption the images. The chosen VLM is suitable for NSFW and SFW images, but it's far from perfect.

This step requires a 24GB GPU (minimum) to run.

Before use:

- Make sure your cropped & bucketed images are in the `img` directory (see previous script)
- Open up `autocaption.py` and modify `PROMPT` to be whatever you want it to be

Then run:

```bash
cd scripts
python autocaption.py
```

Note: if you need it to run on a specific GPU (assuming that you want to run on device 3):

```bash
cd scripts
CUDA_VISIBLE_DEVICES=3 python autocaption.py
```

Note: on first run, this script will download a ~20GB model from Huggingface to do the captioning.

When it's done, you will see your images + caption files in the `dataset` directory.

### captionui.py

The auto-captioning script is helpful, but far from flawless. To that end, I built a very basic UI to manually fix captions.

To use:

```bash
cd scripts
python captionui.py
```

Click on 'Load Directory', then choose the `dataset` directory populated by the prior step.

Navigate between images with up/down, edit the caption in the text box and choose 'Save Caption' to save the caption.

Note: DO NOT RE-RUN `autocaption.py` after starting this. It will overwrite your changes.

## To Do

- Pull the bucket sizes & prompt out into a config file to avoid modifying scripts
- Autosave captions when navigating (and possibly change the navigation hotkeys)
- Script to create Kohya dataset config from `dataset` folder
- Choosing VLM from various options in config including cloud options
