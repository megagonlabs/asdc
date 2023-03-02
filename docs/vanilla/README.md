
# Vanilla dialogs

Files ``data/vanilla/*.VanillaUtterances.jsonl`` are Additional dialogs with no SCUD annotations.
Schema is [``asdc.schema.vanilla.VanillaUtterances``](asdc/schema/vanilla.py).

All dialogs are fictitious by crowd workers.

## ``travel.VanillaUtterances.jsonl``: 2,969 dialogs

This file contains pairs of a question about travel and its answer.

| Question | Answer |
| --- | --- |
| あなたが、今度の連休に国内旅行をするとしたら、どのような旅行をしたいですか? | 家族で遊びもできて、のんびりもできる旅行 |
| あなたが、京都に旅行するとしたら、どのような旅行をしたいですか? | 清水寺を巡る旅行|
| あなたが、学校低学年の子どもと配偶者との家族国内旅行をするとしたら、どのような旅行をしたいですか? | 子供が思いっきりはしゃげるような旅行|

## ``question.single.VanillaUtterances.jsonl``: 1,049 dialogs

This file contains pairs of single question and its answer.

| Operator | Customer |
| --- | --- |
| 当ホテルは朝食バイキングのメニューが豊富で。宿泊いただいたお客様からも高い評価をいただいております。お食事付きのプランはいかがでしょうか | 朝食付きのプランはおいくらですか?|

## ``question.number.VanillaUtterances.jsonl``: 2,013 dialogs

This file contains pairs of question(s) about numbers and its answer.

- ``meta["instruction"]``: The instructed type of numbers to make a pair.
- ``meta["num_number_q"]``: The crowd worker must use a number greater than or equal to the number written here in the question.
- ``meta["num_number_a"]``: The crowd worker must use a number greater than or equal to the number written here in the answer.

## ``question.number_long_a.VanillaUtterances.jsonl``: 1,442 dialogs

## ``question.long_q.VanillaUtterances.jsonl``: 5,574 dialogs

This file contains pairs of question(s) and its answer.
Most operators' utterances contain several sentences.

- ``meta["q_num_sentences"]``: The number of sentences of the operator's utterance

## ``situation.normal.extend.VanillaUtterances.jsonl``: 841 dialogs

This file contains the continuation of several conversations in ``situation.normal.VanillaUtterances.jsonl``.
The original id is stored in ``meta["original_doc_id"]``.

Crowd workers as asked to make operators suggest two or more accommodations.
The candidate hotels are named with alphabets like ``Aホテル``, ``B旅館``, and ``Cホテル``.

- ``meta["finalize"]``: Whether the customer finally selects one candidate or not.
- ``meta["single_candidates"]``: Whether the operator suggests only single accommodation.

## ``topic.**.VanillaUtterance.VanillaUtterances.jsonl``

These files contain customers' queries and dialogs about topics.
The topic id is stored in ``meta["topic"]``.

- 1 turn
    - ``topic.L1.1turn.VanillaUtterances.jsonl``: 16,997 queries
    - ``topic.L2.food.1turn.VanillaUtterances.jsonl``: 11,485 queries
        - ``meta["topics"]``: other topics if null
        - ``meta["topics_dist"]``: topic votes if null
    - ``topic.L2.misc.1turn.VanillaUtterances.jsonl``: 10,914 queries
    - ``topic.L3.1turn.VanillaUtterances.jsonl``: 8,675 queries
- 4 turn
    - ``topic.L1.4turn.VanillaUtterances.jsonl``: 6,291 dialogs
    - ``topic.L2.food.4turn.VanillaUtterances.jsonl``: 3,121 dialogs

| Topic | Query |
| --- | --- |
| ベッド | ツインはいくらですか |
| 風呂 | 洗い場にアメニティが揃っているお風呂にして下さい |
| 食事::食材::野菜 | 食事は肉と魚が苦手なので野菜の食材がたくさん食べれる宿はありますか。|
| 食事::アレルギー::そば | そばにアレルギー反応があります。そば粉を使用した料理以外でお願いします。|
