use crate::table::AnswerIndex;
use crate::{ExClause, TableIndex, TimeStamp};
use std::fmt::Debug;

use chalk_derive::HasInterner;
use chalk_ir::fold::{FallibleTypeFolder, TypeFoldable};
use chalk_ir::interner::Interner;
use chalk_ir::{Canonical, DebruijnIndex, UniverseMap};

#[derive(Clone, Debug, HasInterner)]
pub(crate) struct Strand<I: Interner> {
    pub(super) ex_clause: ExClause<I>,

    /// Index into `ex_clause.subgoals`.
    pub(crate) selected_subgoal: Option<SelectedSubgoal>,

    pub(crate) last_pursued_time: TimeStamp,
}

pub(crate) type CanonicalStrand<I> = Canonical<Strand<I>>;

#[derive(Clone, Debug)]
pub(crate) struct SelectedSubgoal {
    /// The index of the subgoal in `ex_clause.subgoals`
    pub(crate) subgoal_index: usize,

    /// The index of the table that we created or found for this subgoal
    pub(super) subgoal_table: TableIndex,

    /// Index of the answer we should request next from the table
    pub(crate) answer_index: AnswerIndex,

    /// Maps the universes of the subgoal to the canonical universes
    /// used in the table
    pub(crate) universe_map: UniverseMap,
}

impl<I: Interner> TypeFoldable<I> for Strand<I> {
    fn try_fold_with<E>(
        self,
        folder: &mut dyn FallibleTypeFolder<I, Error = E>,
        outer_binder: DebruijnIndex,
    ) -> Result<Self, E> {
        Ok(Strand {
            ex_clause: self.ex_clause.try_fold_with(folder, outer_binder)?,
            last_pursued_time: self.last_pursued_time,
            selected_subgoal: self.selected_subgoal,
        })
    }
}
