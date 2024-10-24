from gdlib import *

# Create a true color image
im = imagecreatetruecolor(400, 300)

# Allocate some colors
black = imagecolorallocate(im, 0, 0, 0)
white = imagecolorallocate(im, 255, 255, 255)
red = imagecolorallocate(im, 255, 0, 0)

# Fill the background with white
imagefill(im, 0, 0, white)

# Draw a rectangle
imagerectangle(im, 50, 50, 350, 250, black)

# Draw a filled ellipse
imagefilledellipse(im, 200, 150, 100, 50, red)

# Apply a Gaussian blur filter
imagefilter(im, IMG_FILTER_GAUSSIAN_BLUR)

# Save the image as PNG
imagepng(im, 'output.png')

# Destroy the image resource
imagedestroy(im)
