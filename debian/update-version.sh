#!/bin/bash
# Don't run this directly, use "debian/rules update-version" instead

prev_stable() {
local V=$1
python3 -c 'import sys; k=list(map(int,sys.argv[1].split("."))); k[1]-=1; print(".".join(map(str,k)))' "$V"
}

update() {
local ORIG=$1 NEW=$2 NEW_LONG=$3

ORIG_M1=$(prev_stable $ORIG)
NEW_M1=$(prev_stable $NEW)
ORIG_R="${ORIG/./\\.}" # match a literal dot, otherwise this might sometimes match e.g. debhelper (>= 9.20141010)

WASI_CI="$(grep -Rl "git clone https://github.com/WebAssembly/wasi-libc" ../src/ci | head -n1)"
WASI_COMMIT="$(egrep -o '\b[0-9A-Fa-f]{7}' "$WASI_CI")"
WASI_REGEX='wasi-libc \(([><=]+) 0.0~git([0-9]+).([0-9a-f]+)([~+]+)\)'

if [ -z "$WASI_COMMIT" -o "$(printf '%s\n' "$WASI_COMMIT" | wc -l)" != 1 ]; then
  echo >&2 "error: could not determine unique WASI_COMMIT ($WASI_COMMIT), please figure it out from src/ci and update my logic"
  exit 1
fi

WASI_COMMIT_OLD="$(sed -nre 's|.*'"${WASI_REGEX}"'.*|\3|gp' control | sort -u)"
if [ -z "$WASI_COMMIT_OLD"  -o "$(printf '%s\n' "$WASI_COMMIT_OLD" | wc -l)" != 1 ]; then
  echo >&2 "error: could not determine unique WASI_COMMIT_OLD ($WASI_COMMIT_OLD), please figure it out from debian/control and update my logic"
  exit 1
fi

sed -i -e "s|libstd-rust-${ORIG_R}|libstd-rust-$NEW|g" \
       -e "s|rustc:native\( *\)(<= [^)]*)|rustc:native\1(<= $NEW_LONG++)|g" \
       -e "s|rustc:native\( *\)(>= ${ORIG_M1/./\\.}|rustc:native\1(>= ${NEW_M1}|g" \
       -e "s|cargo:native\( *\)(>= ${ORIG_M1/./\\.}|cargo:native\1(>= ${NEW_M1}|g" \
       control

if [ "$WASI_COMMIT" != "$WASI_COMMIT_OLD" ]; then
  sed -ri -e 's|'"${WASI_REGEX}"'|wasi-libc (\1 0.0~gitFIXME.'"${WASI_COMMIT}"'\4)|g' control
  echo >&2 "note: the version of the wasi-libc Build-Depends has changed and needs to be FIXME with the correct date"
  echo >&2 "please update that package, upload it to experimental, and supply the correct date in debian/control"
fi

if [ "$NEW" != "$ORIG" ]; then
git mv libstd-rust-$ORIG.install libstd-rust-$NEW.install
git mv libstd-rust-$ORIG.triggers libstd-rust-$NEW.triggers
git mv libstd-rust-$ORIG.lintian-overrides libstd-rust-$NEW.lintian-overrides
fi
sed -i -e "s|libstd-rust-${ORIG_R}|libstd-rust-$NEW|g" libstd-rust-$NEW.lintian-overrides
}

cd $(dirname "$0")
update "$@"
