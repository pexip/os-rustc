//! POSIX-style filesystem functions which operate on bare paths.

#[cfg(not(any(
    target_os = "illumos",
    target_os = "netbsd",
    target_os = "redox",
    target_os = "wasi",
)))]
use crate::fs::StatFs;
#[cfg(not(any(
    target_os = "illumos",
    target_os = "netbsd",
    target_os = "redox",
    target_os = "wasi",
)))]
use crate::{imp, io, path};

/// `statfs`—Queries filesystem metadata.
///
/// # References
///  - [Linux]
///
/// [Linux]: https://man7.org/linux/man-pages/man2/statfs.2.html
#[cfg(not(any(
    target_os = "illumos",
    target_os = "netbsd",
    target_os = "redox",
    target_os = "wasi",
)))]
#[inline]
pub fn statfs<P: path::Arg>(path: P) -> io::Result<StatFs> {
    path.into_with_c_str(imp::fs::syscalls::statfs)
}
