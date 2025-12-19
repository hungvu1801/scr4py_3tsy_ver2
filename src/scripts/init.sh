#!/bin/bash

CHROME=/opt/google/chrome/google-chrome
PROFILE=/home/mickeyvu0811/.config/google-chrome/2

nohup "$CHROME" \
    --remote-debugging-port=9222 \
    --user-data-dir="$PROFILE" \
    --no-first-run \
    --no-default-browser-check \
    >/dev/null 2>&1 &