#!/bin/bash
# Generate the requirements.txt file needed by readthedocs.io

# Unfortunately, we can't just rely on Poetry here.  Poetry wants to generate a
# file that includes our lowest compatible version of Python (v3.9 as of this
# writing), but readthedocs.io can only build with older versions (v3.7 as of
# this writing).  So, we need to modify the generated result to make
# readthedocs.io happy.  This is pulled out so that both the run script and
# the pre-commit hooks can use the same behavior.

poetry export --format=requirements.txt --without-hashes --with dev --output=docs/requirements.txt
if [ $? != 0 ]; then
   echo "*** Failed to export requirements.txt"
   exit 1
fi

sed --version 2>&1 | grep -iq "GNU sed"
if [ $? = 0 ]; then
   # GNU sed accepts a bare -i and assumes no backup file
   sed -i 's/python_version >= "3.9"/python_version >= "3.7"/g' docs/requirements.txt
else
   # BSD sed requires you to set an empty backup file extension
   sed -i "" 's/python_version >= "3.9"/python_version >= "3.7"/g' docs/requirements.txt
fi

poetry run python utils/dos2unix.py docs/requirements.txt
if [ $? != 0 ]; then
   echo "*** Failed to convert requirements.txt to UNIX line endings"
   exit 1
fi
