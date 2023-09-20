// check-pass

#![feature(type_alias_impl_trait)]

trait SuperExpectation: Fn(i32) {}

impl<T: Fn(i32)> SuperExpectation for T {}

type Foo = impl SuperExpectation;

fn main() {
    let _: Foo = |x| {
        let _ = x.to_string();
    };
}
