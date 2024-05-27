# Chromium build container

Building the Chromium:

1. Run the `prepare-container.sh` script to create the container with built Chromium.

Debugging:

1. `gdb --args /home/chrome/chromium/src/out/x64.debug/d8 --shell /home/chrome/exploit/pwn.js --allow-natives-syntax --print-code`
