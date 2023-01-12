# Adding a new target

These are a set of steps to add support for a new target. There are
numerous end states and paths to get there, so not all sections may be
relevant to your desired goal.

## Specifying a new LLVM

For very new targets, you may need to use a different fork of LLVM
than what is currently shipped with Rust. In that case, navigate to
the `src/llvm-project` git submodule (you might need to run `./x.py
check` at least once so the submodule is updated), check out the
appropriate commit for your fork, then commit that new submodule
reference in the main Rust repository.

An example would be:

```
cd src/llvm-project
git remote add my-target-llvm some-llvm-repository
git checkout my-target-llvm/my-branch
cd ..
git add llvm-project
git commit -m 'Use my custom LLVM'
```

### Using pre-built LLVM

If you have a local LLVM checkout that is already built, you may be
able to configure Rust to treat your build as the system LLVM to avoid
redundant builds.

You can tell Rust to use a pre-built version of LLVM using the `target` section
of `config.toml`:

```toml
[target.x86_64-unknown-linux-gnu]
llvm-config = "/path/to/llvm/llvm-7.0.1/bin/llvm-config"
```

If you are attempting to use a system LLVM, we have observed the following paths
before, though they may be different from your system:

- `/usr/bin/llvm-config-8`
- `/usr/lib/llvm-8/bin/llvm-config`

Note that you need to have the LLVM `FileCheck` tool installed, which is used
for codegen tests. This tool is normally built with LLVM, but if you use your
own preinstalled LLVM, you will need to provide `FileCheck` in some other way.
On Debian-based systems, you can install the `llvm-N-tools` package (where `N`
is the LLVM version number, e.g. `llvm-8-tools`). Alternately, you can specify
the path to `FileCheck` with the `llvm-filecheck` config item in `config.toml`
or you can disable codegen test with the `codegen-tests` item in `config.toml`.

## Creating a target specification

You should start with a target JSON file. You can see the specification
for an existing target using `--print target-spec-json`:

```
rustc -Z unstable-options --target=wasm32-unknown-unknown --print target-spec-json
```

Save that JSON to a file and modify it as appropriate for your target.

### Adding a target specification

Once you have filled out a JSON specification and been able to compile
somewhat successfully, you can copy the specification into the
compiler itself.

You will need to add a line to the big table inside of the
`supported_targets` macro in the `rustc_target::spec` module. You
will then add a corresponding file for your new target containing a
`target` function.

Look for existing targets to use as examples.

## Patching crates

You may need to make changes to crates that the compiler depends on,
such as [`libc`][] or [`cc`][]. If so, you can use Cargo's
[`[patch]`][patch] ability. For example, if you want to use an
unreleased version of `libc`, you can add it to the top-level
`Cargo.toml` file:

```diff
diff --git a/Cargo.toml b/Cargo.toml
index be15e50e2bc..4fb1248ba99 100644
--- a/Cargo.toml
+++ b/Cargo.toml
@@ -66,10 +66,11 @@ cargo = { path = "src/tools/cargo" }
 [patch.crates-io]
 # Similar to Cargo above we want the RLS to use a vendored version of `rustfmt`
 # that we're shipping as well (to ensure that the rustfmt in RLS and the
 # `rustfmt` executable are the same exact version).
 rustfmt-nightly = { path = "src/tools/rustfmt" }
+libc = { git = "https://github.com/rust-lang/libc", rev = "0bf7ce340699dcbacabdf5f16a242d2219a49ee0" }

 # See comments in `src/tools/rustc-workspace-hack/README.md` for what's going on
 # here
 rustc-workspace-hack = { path = 'src/tools/rustc-workspace-hack' }
```

After this, run `cargo update -p libc` to update the lockfiles.

Beware that if you patch to a local `path` dependency, this will enable
warnings for that dependency. Some dependencies are not warning-free, and due
to the `deny-warnings` setting in `config.toml`, the build may suddenly start
to fail. To work around the warnings, you may want to disable `deny-warnings`
in the config, or modify the dependency to remove the warnings.

[`libc`]: https://crates.io/crates/libc
[`cc`]: https://crates.io/crates/cc
[patch]: https://doc.rust-lang.org/stable/cargo/reference/overriding-dependencies.html#the-patch-section

## Cross-compiling

Once you have a target specification in JSON and in the code, you can
cross-compile `rustc`:

```
DESTDIR=/path/to/install/in \
./x.py install -i --stage 1 --host aarch64-apple-darwin.json --target aarch64-apple-darwin \
compiler/rustc library/std
```

If your target specification is already available in the bootstrap
compiler, you can use it instead of the JSON file for both arguments.

## Promoting a target from tier 2 (target) to tier 2 (host)

There are two levels of tier 2 targets:
  a) Targets that are only cross-compiled (`rustup target add`)
  b) Targets that [have a native toolchain][tier2-native] (`rustup toolchain install`)

[tier2-native]: https://doc.rust-lang.org/nightly/rustc/target-tier-policy.html#tier-2-with-host-tools

For an example of promoting a target from cross-compiled to native,
see [#75914](https://github.com/rust-lang/rust/pull/75914).