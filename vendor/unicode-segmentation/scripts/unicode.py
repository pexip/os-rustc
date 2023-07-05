#!/usr/bin/env python
#
# Copyright 2011-2015 The Rust Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution and at
# http://rust-lang.org/COPYRIGHT.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

# This script uses the following Unicode tables:
# - DerivedCoreProperties.txt
# - auxiliary/GraphemeBreakProperty.txt
# - auxiliary/WordBreakProperty.txt
# - ReadMe.txt
# - UnicodeData.txt
#
# Since this should not require frequent updates, we just store this
# out-of-line and check the unicode.rs file into git.

import fileinput, re, os, sys

preamble = '''// Copyright 2012-2018 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

// NOTE: The following code was generated by "scripts/unicode.py", do not edit directly

#![allow(missing_docs, non_upper_case_globals, non_snake_case)]
'''

# Mapping taken from Table 12 from:
# http://www.unicode.org/reports/tr44/#General_Category_Values
expanded_categories = {
    'Lu': ['LC', 'L'], 'Ll': ['LC', 'L'], 'Lt': ['LC', 'L'],
    'Lm': ['L'], 'Lo': ['L'],
    'Mn': ['M'], 'Mc': ['M'], 'Me': ['M'],
    'Nd': ['N'], 'Nl': ['N'], 'No': ['N'],
    'Pc': ['P'], 'Pd': ['P'], 'Ps': ['P'], 'Pe': ['P'],
    'Pi': ['P'], 'Pf': ['P'], 'Po': ['P'],
    'Sm': ['S'], 'Sc': ['S'], 'Sk': ['S'], 'So': ['S'],
    'Zs': ['Z'], 'Zl': ['Z'], 'Zp': ['Z'],
    'Cc': ['C'], 'Cf': ['C'], 'Cs': ['C'], 'Co': ['C'], 'Cn': ['C'],
}

# these are the surrogate codepoints, which are not valid rust characters
surrogate_codepoints = (0xd800, 0xdfff)

UNICODE_VERSION = (15, 0, 0)

UNICODE_VERSION_NUMBER = "%s.%s.%s" %UNICODE_VERSION

def is_surrogate(n):
    return surrogate_codepoints[0] <= n <= surrogate_codepoints[1]

def fetch(f):
    if not os.path.exists(os.path.basename(f)):
        if "emoji" in f:
            os.system("curl -O https://www.unicode.org/Public/%s/ucd/emoji/%s"
                      % (UNICODE_VERSION_NUMBER, f))
        else:
            os.system("curl -O https://www.unicode.org/Public/%s/ucd/%s"
                      % (UNICODE_VERSION_NUMBER, f))

    if not os.path.exists(os.path.basename(f)):
        sys.stderr.write("cannot load %s" % f)
        exit(1)

def load_gencats(f):
    fetch(f)
    gencats = {}

    udict = {};
    range_start = -1;
    for line in fileinput.input(f):
        data = line.split(';');
        if len(data) != 15:
            continue
        cp = int(data[0], 16);
        if is_surrogate(cp):
            continue
        if range_start >= 0:
            for i in range(range_start, cp):
                udict[i] = data;
            range_start = -1;
        if data[1].endswith(", First>"):
            range_start = cp;
            continue;
        udict[cp] = data;

    for code in udict:
        [code_org, name, gencat, combine, bidi,
         decomp, deci, digit, num, mirror,
         old, iso, upcase, lowcase, titlecase ] = udict[code];

        # place letter in categories as appropriate
        for cat in [gencat, "Assigned"] + expanded_categories.get(gencat, []):
            if cat not in gencats:
                gencats[cat] = []
            gencats[cat].append(code)

    gencats = group_cats(gencats)
    return gencats

def group_cats(cats):
    cats_out = {}
    for cat in cats:
        cats_out[cat] = group_cat(cats[cat])
    return cats_out

def group_cat(cat):
    cat_out = []
    letters = sorted(set(cat))
    cur_start = letters.pop(0)
    cur_end = cur_start
    for letter in letters:
        assert letter > cur_end, \
            "cur_end: %s, letter: %s" % (hex(cur_end), hex(letter))
        if letter == cur_end + 1:
            cur_end = letter
        else:
            cat_out.append((cur_start, cur_end))
            cur_start = cur_end = letter
    cat_out.append((cur_start, cur_end))
    return cat_out

def ungroup_cat(cat):
    cat_out = []
    for (lo, hi) in cat:
        while lo <= hi:
            cat_out.append(lo)
            lo += 1
    return cat_out

def format_table_content(f, content, indent):
    line = " "*indent
    first = True
    for chunk in content.split(","):
        if len(line) + len(chunk) < 98:
            if first:
                line += chunk
            else:
                line += ", " + chunk
            first = False
        else:
            f.write(line + ",\n")
            line = " "*indent + chunk
    f.write(line)

def load_properties(f, interestingprops):
    fetch(f)
    props = {}
    re1 = re.compile(r"^ *([0-9A-F]+) *; *(\w+)")
    re2 = re.compile(r"^ *([0-9A-F]+)\.\.([0-9A-F]+) *; *(\w+)")

    for line in fileinput.input(os.path.basename(f)):
        prop = None
        d_lo = 0
        d_hi = 0
        m = re1.match(line)
        if m:
            d_lo = m.group(1)
            d_hi = m.group(1)
            prop = m.group(2)
        else:
            m = re2.match(line)
            if m:
                d_lo = m.group(1)
                d_hi = m.group(2)
                prop = m.group(3)
            else:
                continue
        if interestingprops and prop not in interestingprops:
            continue
        d_lo = int(d_lo, 16)
        d_hi = int(d_hi, 16)
        if prop not in props:
            props[prop] = []
        props[prop].append((d_lo, d_hi))

    # optimize if possible
    for prop in props:
        props[prop] = group_cat(ungroup_cat(props[prop]))

    return props

def escape_char(c):
    return "'\\u{%x}'" % c

def emit_table(f, name, t_data, t_type = "&'static [(char, char)]", is_pub=True,
        pfun=lambda x: "(%s,%s)" % (escape_char(x[0]), escape_char(x[1])), is_const=True):
    pub_string = "const"
    if not is_const:
        pub_string = "let"
    if is_pub:
        pub_string = "pub " + pub_string
    f.write("    %s %s: %s = &[\n" % (pub_string, name, t_type))
    data = ""
    first = True
    for dat in t_data:
        if not first:
            data += ","
        first = False
        data += pfun(dat)
    format_table_content(f, data, 8)
    f.write("\n    ];\n\n")

def emit_util_mod(f):
    f.write("""
pub mod util {
    #[inline]
    pub fn bsearch_range_table(c: char, r: &'static [(char,char)]) -> bool {
        use core::cmp::Ordering::{Equal, Less, Greater};
        r.binary_search_by(|&(lo,hi)| {
            if lo <= c && c <= hi { Equal }
            else if hi < c { Less }
            else { Greater }
        }).is_ok()
    }

    #[inline]
    fn is_alphabetic(c: char) -> bool {
        match c {
            'a' ..= 'z' | 'A' ..= 'Z' => true,
            c if c > '\x7f' => super::derived_property::Alphabetic(c),
            _ => false,
        }
    }

    #[inline]
    fn is_numeric(c: char) -> bool {
        match c {
            '0' ..= '9' => true,
            c if c > '\x7f' => super::general_category::N(c),
            _ => false,
        }
    }

    #[inline]
    pub fn is_alphanumeric(c: char) -> bool {
        is_alphabetic(c) || is_numeric(c)
    }
}

""")

def emit_property_module(f, mod, tbl, emit):
    f.write("mod %s {\n" % mod)
    for cat in sorted(emit):
        emit_table(f, "%s_table" % cat, tbl[cat], is_pub=False)
        f.write("    #[inline]\n")
        f.write("    pub fn %s(c: char) -> bool {\n" % cat)
        f.write("        super::util::bsearch_range_table(c, %s_table)\n" % cat)
        f.write("    }\n\n")
    f.write("}\n\n")

def emit_break_module(f, break_table, break_cats, name):
    Name = name.capitalize()
    f.write("""pub mod %s {
    use core::result::Result::{Ok, Err};

    pub use self::%sCat::*;

    #[allow(non_camel_case_types)]
    #[derive(Clone, Copy, PartialEq, Eq, Debug)]
    pub enum %sCat {
""" % (name, Name, Name))

    break_cats.append("Any")
    break_cats.sort()
    for cat in break_cats:
        f.write(("        %sC_" % Name[0]) + cat + ",\n")
    f.write("""    }

    fn bsearch_range_value_table(c: char, r: &'static [(char, char, %sCat)]) -> (u32, u32, %sCat) {
        use core::cmp::Ordering::{Equal, Less, Greater};
        match r.binary_search_by(|&(lo, hi, _)| {
            if lo <= c && c <= hi { Equal }
            else if hi < c { Less }
            else { Greater }
        }) {
            Ok(idx) => {
                let (lower, upper, cat) = r[idx];
                (lower as u32, upper as u32, cat)
            }
            Err(idx) => {
                (
                    if idx > 0 { r[idx-1].1 as u32 + 1 } else { 0 },
                    r.get(idx).map(|c|c.0 as u32 - 1).unwrap_or(core::u32::MAX),
                    %sC_Any,
                )
            }
        }
    }

    pub fn %s_category(c: char) -> (u32, u32, %sCat) {
        bsearch_range_value_table(c, %s_cat_table)
    }

""" % (Name, Name, Name[0], name, Name, name))

    emit_table(f, "%s_cat_table" % name, break_table, "&'static [(char, char, %sCat)]" % Name,
        pfun=lambda x: "(%s,%s,%sC_%s)" % (escape_char(x[0]), escape_char(x[1]), Name[0], x[2]),
        is_pub=False, is_const=True)
    f.write("}\n")

if __name__ == "__main__":
    r = "tables.rs"
    if os.path.exists(r):
        os.remove(r)
    with open(r, "w") as rf:
        # write the file's preamble
        rf.write(preamble)
        rf.write("""
/// The version of [Unicode](http://www.unicode.org/)
/// that this version of unicode-segmentation is based on.
pub const UNICODE_VERSION: (u64, u64, u64) = (%s, %s, %s);
""" % UNICODE_VERSION)

        # download and parse all the data
        gencats = load_gencats("UnicodeData.txt")
        derived = load_properties("DerivedCoreProperties.txt", ["Alphabetic"])

        emit_util_mod(rf)
        for (name, cat, pfuns) in ("general_category", gencats, ["N"]), \
                                  ("derived_property", derived, ["Alphabetic"]):
            emit_property_module(rf, name, cat, pfuns)

        ### grapheme cluster module
        # from http://www.unicode.org/reports/tr29/#Grapheme_Cluster_Break_Property_Values
        grapheme_cats = load_properties("auxiliary/GraphemeBreakProperty.txt", [])

        # Control
        #  Note:
        # This category also includes Cs (surrogate codepoints), but Rust's `char`s are
        # Unicode Scalar Values only, and surrogates are thus invalid `char`s.
        # Thus, we have to remove Cs from the Control category
        grapheme_cats["Control"] = group_cat(list(
            set(ungroup_cat(grapheme_cats["Control"]))
            - set(ungroup_cat([surrogate_codepoints]))))

        grapheme_table = []
        for cat in grapheme_cats:
            grapheme_table.extend([(x, y, cat) for (x, y) in grapheme_cats[cat]])
        emoji_props = load_properties("emoji-data.txt", ["Extended_Pictographic"])
        grapheme_table.extend([(x, y, "Extended_Pictographic") for (x, y) in emoji_props["Extended_Pictographic"]])
        grapheme_table.sort(key=lambda w: w[0])
        last = -1
        for chars in grapheme_table:
            if chars[0] <= last:
                raise "Grapheme tables and Extended_Pictographic values overlap; need to store these separately!"
            last = chars[1]
        emit_break_module(rf, grapheme_table, list(grapheme_cats.keys()) + ["Extended_Pictographic"], "grapheme")
        rf.write("\n")

        word_cats = load_properties("auxiliary/WordBreakProperty.txt", [])
        word_table = []
        for cat in word_cats:
            word_table.extend([(x, y, cat) for (x, y) in word_cats[cat]])
        word_table.sort(key=lambda w: w[0])
        emit_break_module(rf, word_table, list(word_cats.keys()), "word")

        # There are some emoji which are also ALetter, so this needs to be stored separately
        # For efficiency, we could still merge the two tables and produce an ALetterEP state
        emoji_table = [(x, y, "Extended_Pictographic") for (x, y) in emoji_props["Extended_Pictographic"]]
        emit_break_module(rf, emoji_table, ["Extended_Pictographic"], "emoji")

        sentence_cats = load_properties("auxiliary/SentenceBreakProperty.txt", [])
        sentence_table = []
        for cat in sentence_cats:
            sentence_table.extend([(x, y, cat) for (x, y) in sentence_cats[cat]])
        sentence_table.sort(key=lambda w: w[0])
        emit_break_module(rf, sentence_table, list(sentence_cats.keys()), "sentence")
