// DO NOT EDIT THIS FILE. IT WAS AUTOMATICALLY GENERATED BY:
//
//   ucd-generate dfa --name SIMPLE_WORD_FWD --sparse --minimize --state-size 2 src/unicode/fsm/ \w
//
// ucd-generate 0.2.8 is available on crates.io.

#[cfg(target_endian = "big")]
lazy_static! {
    pub static ref SIMPLE_WORD_FWD: ::regex_automata::SparseDFA<&'static [u8], u16> = {
        #[repr(C)]
        struct Aligned<B: ?Sized> {
            _align: [u8; 0],
            bytes: B,
        }

        static ALIGNED: &'static Aligned<[u8]> = &Aligned {
            _align: [],
            bytes: *include_bytes!("simple_word_fwd.bigendian.dfa"),
        };

        unsafe { ::regex_automata::SparseDFA::from_bytes(&ALIGNED.bytes) }
    };
}

#[cfg(target_endian = "little")]
lazy_static! {
    pub static ref SIMPLE_WORD_FWD: ::regex_automata::SparseDFA<&'static [u8], u16> = {
        #[repr(C)]
        struct Aligned<B: ?Sized> {
            _align: [u8; 0],
            bytes: B,
        }

        static ALIGNED: &'static Aligned<[u8]> = &Aligned {
            _align: [],
            bytes: *include_bytes!("simple_word_fwd.littleendian.dfa"),
        };

        unsafe { ::regex_automata::SparseDFA::from_bytes(&ALIGNED.bytes) }
    };
}