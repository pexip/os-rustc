#!/bin/bash

set -ex

if [[ -n "$1" ]]; then
  ver="$1"
fi

if [[ -z "$ver" ]]; then
  echo '$ver must be set'
  exit 1
fi

suffix="+dfsg1"
if [[ -n "$2" ]]; then
  suffix="$2"
fi
echo "Setting repack suffix to '$suffix'"

tarball=../"rustc-${ver/\~/-}-src.tar.xz"

echo "Looking up top-level dir in '$tarball'.."
top="$(tar tf "$tarball" | head -n1)"

if [[ -z "$top" ]]; then
  echo "Failed to extract top-level dir from '$tarball'"
  exit 1
fi

echo "Top-level dir: '$top'"

grep-dctrl -n -F Files-Excluded -s Files-Excluded '' debian/copyright \
	| sed -r 's/^ +//; /^$/d' \
	| awk -v top="$top/" '/^\*/{print; next} {print top $$0}' \
	> "$tarball.excludes"

echo "Extracting tarball to '$top'"
tar --exclude-from="$tarball.excludes" -xf "$tarball"

echo "Removing excludes file"
rm -f "$tarball.excludes"

echo "Removing empty dirs"
find "$top" -depth -type d -empty -print -delete

tar_options="--sort=name --owner=0 --group=0 --numeric-owner"
origtxz="../rustc_$ver$suffix.orig.tar.xz"

echo "Repacking extracted tarball.."
rm -f "$origtxz"
tar $tar_options -cf - "$top" | xz -6 -T0 - > "$origtxz"

