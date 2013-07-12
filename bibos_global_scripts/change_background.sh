#!/usr/bin/env bash

# This script is intended to be run from the BibOS admin.
# It will change the user's background image in a standard 
# BibOS installation.
# 
# Feel free to modify it as you need, but as is it can't be expected
# to work on non-BibOS setups.
#
# The script takes ONE parameter, a valid path to the image to be used
# as background.

if [ $# -ne 1 ]
then
    echo "Usage: $(basename $0) {filename} "
    echo ""
    exit -1
fi

# We have one and only one argument, the background image's file path.

IMAGE_FILE=$1
AS_USER=user

if [ ! -f $IMAGE_FILE ]
then
    echo "No such file: $IMAGE_FILE"
    echo "Please supply a path to an existing image file"
    exit -1
fi

# Do not check it's an image, the user can shoot self in foot if (s)he likes.

IMAGES_HOME=/usr/share/bibos/images/backgrounds
HIDDEN_DIR=/home/.skjult

mkdir -p $IMAGES_HOME
mkdir -p $HIDDEN_DIR/.config/dconf

IMAGE_FULL_PATH="$IMAGES_HOME"/"$(basename "$IMAGE_FILE")"

cp "$IMAGE_FILE"  "$IMAGE_FULL_PATH"

export DISPLAY=:0.0
export XAUTHORITY=/home/$AS_USER/.Xauthority

sudo -u $AS_USER /usr/bin/gsettings set org.gnome.desktop.background picture-uri file://"$IMAGE_FULL_PATH" 2>/dev/null

cp /home/$AS_USER/.config/dconf/user $HIDDEN_DIR/.config/dconf/
exit 0

