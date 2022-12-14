//! Unsafety checker: every impl either implements a trait defined in this
//! crate or pertains to a type defined in this crate.

use rustc_errors::struct_span_err;
use rustc_hir as hir;
use rustc_hir::def::DefKind;
use rustc_hir::Unsafety;
use rustc_middle::ty::TyCtxt;

pub fn check(tcx: TyCtxt<'_>) {
    for id in tcx.hir().items() {
        if matches!(tcx.def_kind(id.def_id), DefKind::Impl) {
            let item = tcx.hir().item(id);
            if let hir::ItemKind::Impl(ref impl_) = item.kind {
                check_unsafety_coherence(
                    tcx,
                    item,
                    Some(&impl_.generics),
                    impl_.unsafety,
                    impl_.polarity,
                );
            }
        }
    }
}

fn check_unsafety_coherence<'tcx>(
    tcx: TyCtxt<'tcx>,
    item: &hir::Item<'_>,
    impl_generics: Option<&hir::Generics<'_>>,
    unsafety: hir::Unsafety,
    polarity: hir::ImplPolarity,
) {
    if let Some(trait_ref) = tcx.impl_trait_ref(item.def_id) {
        let trait_def = tcx.trait_def(trait_ref.def_id);
        let unsafe_attr = impl_generics.and_then(|generics| {
            generics.params.iter().find(|p| p.pure_wrt_drop).map(|_| "may_dangle")
        });
        match (trait_def.unsafety, unsafe_attr, unsafety, polarity) {
            (Unsafety::Normal, None, Unsafety::Unsafe, hir::ImplPolarity::Positive) => {
                struct_span_err!(
                    tcx.sess,
                    item.span,
                    E0199,
                    "implementing the trait `{}` is not unsafe",
                    trait_ref.print_only_trait_path()
                )
                .emit();
            }

            (Unsafety::Unsafe, _, Unsafety::Normal, hir::ImplPolarity::Positive) => {
                struct_span_err!(
                    tcx.sess,
                    item.span,
                    E0200,
                    "the trait `{}` requires an `unsafe impl` declaration",
                    trait_ref.print_only_trait_path()
                )
                .emit();
            }

            (Unsafety::Normal, Some(attr_name), Unsafety::Normal, hir::ImplPolarity::Positive) => {
                struct_span_err!(
                    tcx.sess,
                    item.span,
                    E0569,
                    "requires an `unsafe impl` declaration due to `#[{}]` attribute",
                    attr_name
                )
                .emit();
            }

            (_, _, Unsafety::Unsafe, hir::ImplPolarity::Negative(_)) => {
                // Reported in AST validation
                tcx.sess.delay_span_bug(item.span, "unsafe negative impl");
            }
            (_, _, Unsafety::Normal, hir::ImplPolarity::Negative(_))
            | (Unsafety::Unsafe, _, Unsafety::Unsafe, hir::ImplPolarity::Positive)
            | (Unsafety::Normal, Some(_), Unsafety::Unsafe, hir::ImplPolarity::Positive)
            | (Unsafety::Normal, None, Unsafety::Normal, _) => {
                // OK
            }
        }
    }
}
