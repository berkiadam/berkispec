<!--
  The PROJECT-LANGUAGE blocks of `brainstorm` (9.4 extraction).
  The installer inlines this file at build time in place of the INCLUDE markers,
  according to the chosen PROJECT language (`PROJECT_LANG`); the marker form is
  `lang/brainstorm.md#<anchor>`.
  The blocks were moved here VERBATIM — do not rephrase, do not unify.
  The ANCHOR lines are NOT part of the inlined text, they are delimiters only (8.9).
  CAUTION: no comment-closing sequence may appear in this leading note.
-->

<!-- ANCHOR:BS4-gitignore-felajanlas -->
> *"The `.bs-brainstorm/` folder is currently not excluded from version control. These are raw, unfinished working files — not deliverables, and the `cycle-design-input.md` distilled from them gets committed anyway. I recommend adding the `.bs-brainstorm/*` entry to `.gitignore`. Shall I add it?"*

<!-- ANCHOR:BS2-munkafajl-csontvaz -->
# Brainstorm NN — <topic in one line>

Status: In progress   ·   Started: <YYYY-MM-DD>   ·   Last updated: <YYYY-MM-DD>

## 1. Goal / question

<What we want to decide in this session, in 2-4 lines. If the topic narrows or
shifts along the way, refine this section — but do not delete the earlier
wording, push a "Refinement:" line underneath it.>

## 2. Discovered facts

<One fact = one line, with its source. For code the source is `file:line`, for a
document the file name. Prefix an uncertain statement with "(uncertain)".>

- ...

## 3. Alternatives and trade-offs

<Per option: what it is briefly · what it gives · what we give up for it · what it
touches in the system. If an option was dropped, do not delete it: mark it
"(dropped: <why>)".>

### A) ...

## 4. Decisions

<What we decided, and in one sentence why. In a descriptive tone — this becomes
the body of `cycle-design-input.md`.>

- ...

## 5. Open questions

<A live, checkable list. What is settled: check it off and put the decision into
section 4. Do not delete the checked item.>

- [ ] ...

## 6. Proposed cycle split

<Units that can be developed and tested on their own, in order, with their
dependencies. Per unit: a short goal + how it can be seen that it is done. This is
the input of `01-add-cycles`. Until it exists, leave the "(not yet mature)" mark.>

- ...

## 7. Log

<1-2 lines per round: what happened, what changed. Threads that opened up outside
the topic and need a separate session also go here.>

- <YYYY-MM-DD> — ...
