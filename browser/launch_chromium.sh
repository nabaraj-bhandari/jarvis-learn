#!/bin/bash
chromium \
    --remote-debugging-port=9222 \
    --user-data-dir="$HOME/.config/chromium-jarvis" \
    &
