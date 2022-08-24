
# Supplemental examples

Supplemental SCUD annotations.

## Additional examples

### Hotel

SCUDS annotated to answers about hotels.

- ``hotel.Example.jsonl``

### 2 turn

SCUDS annotated to two turn dialogs made by crowd workers.

- 2turn.Example.jsonl

### 4 turn

SCUDS annotated to four turn dialogs made by crowd workers.

- 4turn.Example.jsonl

## Featured examples

### Conditional generation of Utterances

- ``conditional.Example.jsonl``

Some kinds of dialogs among ``negation`` ,``question`` ,``conditional_answer`` made by an annotator.

### YES/NO question

Dialogs about YES/NO question made by crowd workers.

- ``yn_multi.Example.jsonl``
    - ``meta.instruction`` is a answer type among multiple options ``YES``, ``NYNN`` or ``NO``.
    - ``NYNN`` is answer that is neither yes nor no.
    - Some conversations consist of four turns
- ``yn_yes.Example.jsonl``
- ``4turn_yn_no.Example.jsonl``

### Ellipsis

Every example includes SCUDs to resolve ellipsis

- ``ellipsis.Example.jsonl``

### Multi requests

Utterances made by crowd workers that are likely to generate multiple SCUDs.

- ``mul_req_01.Example.jsonl``
- ``mul_req_02.Example.jsonl``

## Examples to reduce errors

- ``re_001.Example.jsonl``
    - Collection of fixed SCUDs of a SCUD generation system.
    - This is made by an annotator.
- ``re_002.Example.jsonl``
    - Collection of gold SCUDs that SCUD generation systems should work well for.
    - This is made by an annotator.

## Other examples

- ``basic.Example.jsonl``
    - Basic test suite
- ``data/supplemental/wrong_scud/contrastive.Example.jsonl``
    - Include wrong SCUDs
