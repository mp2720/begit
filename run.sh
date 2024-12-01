#!/bin/sh

~/Android/Sdk/platform-tools/adb install pacer.apk

echo continue?
read

./begit.py < $1
