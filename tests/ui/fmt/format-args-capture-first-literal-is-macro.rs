// aux-build:format-string-proc-macro.rs

#[macro_use]
extern crate format_string_proc_macro;

macro_rules! identity_mbe {
    ($tt:tt) => {
        $tt
        //~^ ERROR there is no argument named `a`
    };
}

fn main() {
    let a = 0;

    format!(identity_pm!("{a}"));
    //~^ ERROR there is no argument named `a`
    format!(identity_mbe!("{a}"));
    format!(concat!("{a}"));
    //~^ ERROR there is no argument named `a`
}
