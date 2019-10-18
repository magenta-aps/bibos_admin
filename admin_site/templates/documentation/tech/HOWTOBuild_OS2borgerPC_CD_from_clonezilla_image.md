# HOWTO Build OS2borgerPC CD from a CloneZilla image


You need to install these Debian packages:

* squashfs-tools
* aufs-tools
* e2fslibs-dev
* genisomage

This will not work on top of an eCryptFS system (i.e., don't work in your
encrypted Ubuntu home dir).

## Check out the code

```sh
git clone https://github.com/magenta-aps/bibos_image.git
cd bibos_image
```

## Download a stable Clonezilla live archive

The download link is https://clonezilla.org/downloads/download.php?branch=stable. (These instructions have worked with versions 2.5.6-22 and 2.6.0-37.)

# Mount this ISO as a file system

```sh
cd ..
sudo ./mount_clonezilla.sh images/clonezilla-live.iso
```

# Copy overwrite files to the image (the exact path is output by the 
# mount_clonezilla script)

```sh
sudo ../scripts/do_overwrite_clonezilla.sh bibos-clonezilla.asIlGOYXbC/cd-unified
```

# Copy a OS2borgerPC hard disk image to the CloneZilla CD

```sh
sudo cp -r /sti/til/bibos/image/* bibos-clonezilla.asIlGOYXbC/cd-unified/bibos-images/bibos_default/
```

# Build a new ISO
```sh
sudo ./build_clonezilla_image.sh bibos-clonezilla.asIlGOYXbC/
```

The generated image is a new OS2borgerPC CD which will install the hard disk image you
copied. The changes to clonezilla are independent of architecture and should work
for 64 bit CloneZilla and Ubuntu alike.


