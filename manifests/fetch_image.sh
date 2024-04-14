#!/bin/bash

# Read the background image URI from the ConfigMap
BACKGROUND_IMAGE=$(cat /etc/config/BACKGROUND_IMAGE)

# Use the background image URI to fetch the image
aws s3 cp "$BACKGROUND_IMAGE" /usr/src/app/static/background_image.png

