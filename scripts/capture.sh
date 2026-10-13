#!/usr/bin/env bash
# Capture the current screen of a booted iOS simulator or attached Android
# device. Source captures do not need to match the store's output size — the
# composer scales them into a device frame.
set -euo pipefail

platform="${1:-}"
out="${2:-}"

if [[ -z "$platform" || -z "$out" ]]; then
  cat >&2 <<'USAGE'
usage: capture.sh <ios|android> <output.png>

  ios      captures the currently booted iOS simulator
  android  captures the first attached device or running emulator

Boot the device and navigate to the screen you want before calling this.
USAGE
  exit 64
fi

mkdir -p "$(dirname "$out")"

case "$platform" in
  ios)
    if ! xcrun simctl list devices booted | grep -q "Booted"; then
      echo "No booted iOS simulator. Start one with: xcrun simctl boot '<device name>'" >&2
      exit 1
    fi
    xcrun simctl io booted screenshot "$out"
    ;;
  android)
    if ! adb get-state >/dev/null 2>&1; then
      echo "No attached Android device or running emulator (checked 'adb get-state')." >&2
      exit 1
    fi
    adb exec-out screencap -p > "$out"
    ;;
  *)
    echo "Unknown platform '$platform' (expected 'ios' or 'android')." >&2
    exit 64
    ;;
esac

# sips ships with macOS; on other platforms the dimensions are simply not echoed.
if command -v sips >/dev/null 2>&1; then
  read -r w h < <(sips -g pixelWidth -g pixelHeight "$out" | awk '/pixel(Width|Height)/ {printf "%s ", $2}')
  echo "captured $out (${w}x${h})"
else
  echo "captured $out"
fi
