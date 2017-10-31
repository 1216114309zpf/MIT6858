#!/bin/sh

# At startup, ld.so loads /etc/ld.so.cache at the top of memory, and then
# proceeds to load shared libraries.  If other packages are installed that
# contain ANY libraries, /etc/ld.so.cache gets re-generated, and if it grows
# past a page boundary, ld.so will use one more page for it at startup, and
# all shared libraries will shift down by one page!

# Workaround: remove /etc/ld.so.cache before running anything so shared
# libraries are always at a consistent location in memory

if [ -f /etc/ld.so.cache ]; then
    echo "Found /etc/ld.so.cache; removing it so shared library load addresses are consistent"
    sudo rm /etc/ld.so.cache
fi

