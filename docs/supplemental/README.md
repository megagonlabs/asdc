
# Supplemental examples

Supplemental SCUD annotations.

## Additional examples

### 2 turn

SCUDS annotated to two turn dialogs made by crowd workers.

- ``2turn.Example.jsonl``: 425 examples

### 4 turn

SCUDS annotated to four turn dialogs made by crowd workers.

- ``4turn.Example.jsonl``: 4,451 examples

### Short utterances

Crowd workers were asked to rewrite the client's utterances so that they were in multiple shorter sentences.
The original id is stored in ``meta.data["original_doc_id"]``.

- ``situation.short.Example.jsonl``: 1,887 examples
    - Original utterances: ``data/supplemental/utterances/situation.short.has_scud.VanillaUtterances.jsonl``
    - Utterances without SCUDs: ``data/vanilla/situation.short.VanillaUtterances.jsonl``
- ``situation.normal.Example.jsonl``: 8,320 examples

## Featured examples

### YES/NO question

Dialogs about YES/NO question made by crowd workers.

- ``yn_multi.Example.jsonl``: 9,780 examples
    - ``meta.instruction`` is a answer type among multiple options ``YES``, ``NYNN`` or ``NO``.
    - ``NYNN`` is answer that is neither yes nor no.
    - Some conversations consist of four turns
- ``yn_yes.Example.jsonl``: 2,709 examples
- ``yn_no.Example.jsonl``: 2,709 examples
- ``yn_add.Example.jsonl``: 192 examples

### Question

- ``question.long_a.Example.jsonl``: 201 examples
    - This file contains pairs of question(s) and its answer.
    - Most customers' utterances contain several sentences.

### Choices

- ``2turn_choices.Example.jsonl``: 6,606 examples
    - Pairs of a question about a choice between two things and its answer.
    - ``meta.answer_type`` is an answer type (``INDIRECT`` or  ``NYNN``).
        - ``INDIRECT`` is indirect answer to choose one.
        - ``NYNN`` is answer that is neither yes nor no.

    | Operator | Customer | Type |
    | --- | --- | --- |
    | お部屋のお風呂はコンパクトなユニットバスと造り付けの露天風呂どちらが良いですか? | ゆっくり入りたいので後者でお願いします | INDIRECT |
    | 和室と洋室のどちらにされますか? | どちらも海が見えますか? | NYNN |

### Ellipsis

Every example includes SCUDs to resolve ellipsis

- ``ellipsis.Example.jsonl``: 591 examples

### Multi requests

Utterances made by crowd workers that are likely to generate multiple SCUDs.

- ``mul_req_01.Example.jsonl``: 644 examples
- ``mul_req_02.Example.jsonl``: 998 examples

## Examples to reduce errors

- ``re_001.Example.jsonl``: 33 examples
    - Collection of fixed SCUDs of a SCUD generation system.
    - This is made by an annotator.
- ``re_002.Example.jsonl``: 870 examples
    - Collection of gold SCUDs that SCUD generation systems should work well for.
    - This is made by an annotator.

## Talk about a specific topic

- ``topic_talk.Example.jsonl``: 169 examples

## Other examples

- ``basic.Example.jsonl``: 76 examples
    - Basic test suite
- ``hotel.Example.jsonl``: 199 examples
    - This file contains pairs of a question about hotels and its answer.

| Question | Answer |
| --- | --- |
| あなたが、小学校低学年の子どもと配偶者との家族旅行で泊まるとしたらどのようなホテルに泊まりたいですか? | 子どもが楽しめるホテル |
| あなたが、夏に泊まるとしたらどのようなホテルに泊まりたいですか? | 空気が美味しいホテル |
| あなたが、秋に泊まるとしたらどのようなホテルに泊まりたいですか? | 紅葉が美しい庭のあるホテル|
