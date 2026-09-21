#!/bin/sh
set -eu
token="${NAPMS_RUNTIME_ACCESS_TOKEN:-}"
escaped="$(printf '%s' "$token" | sed 's/\\/\\\\/g; s/"/\\"/g')"
printf 'if (window.__NAPMS_RUNTIME_ACCESS_TOKEN__ === undefined) window.__NAPMS_RUNTIME_ACCESS_TOKEN__ = "%s";\n' "$escaped" > /usr/share/nginx/html/runtime-auth.js
