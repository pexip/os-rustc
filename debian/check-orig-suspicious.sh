#!/bin/bash
set -e

ver="$1"
test -n "$ver" || exit 2
dfsg="$2"
if test -z "$dfsg"; then
  dfsg=1
fi

SUS_WHITELIST="$(find "${PWD}/debian" -name upstream-tarball-unsuspicious.txt -type f)"

rm -rf "rustc-${ver/*~*/beta}-src/"
tar xf "../rustc_$ver+dfsg$dfsg.orig.tar.xz" && cd "rustc-${ver/*~*/beta}-src/"
if test -f "../../rustc_$ver+dfsg$dfsg.orig-extra.tar.xz" ; then
  tar xf "../../rustc_$ver+dfsg$dfsg.orig-extra.tar.xz"
fi

../debian/scripts/audit-vendor-source \
  "$SUS_WHITELIST" \
  "Files-Excluded: in debian/copyright and run a repack." \
  -m text/x-script.python \
  -m application/csv

echo "Artifacts left in rustc-$ver-src, please remove them yourself."
