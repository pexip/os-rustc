// Various tests related to testing how region inference works
// with respect to the object receivers.

// revisions: base nll
// ignore-compare-mode-nll
//[nll] compile-flags: -Z borrowck=mir

trait Foo {
    fn borrowed<'a>(&'a self) -> &'a ();
}

// Here we have two distinct lifetimes, but we try to return a pointer
// with the longer lifetime when (from the signature) we only know
// that it lives as long as the shorter lifetime. Therefore, error.
fn borrowed_receiver_related_lifetimes2<'a,'b>(x: &'a (dyn Foo + 'b)) -> &'b () {
    x.borrowed()
    //[base]~^ ERROR cannot infer
    //[nll]~^^ ERROR lifetime may not live long enough
}

fn main() {}
