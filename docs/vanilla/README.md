
# Vanilla dialogs

Files ``data/vanilla/*.VanillaUtterances.jsonl`` are Additional dialogs with no SCUD annotations.
Schema is [``asdc.schema.vanilla.VanillaUtterances``](asdc/schema/vanilla.py).

All dialogs are fictitious by crowd workers.

## ``hotel.VanillaUtterances.jsonl``: 8,445 dialogs

This file contains pairs of a question about hotels and its answer.

| Question | Answer |
| --- | --- |
| あなたが、小学校低学年の子どもと配偶者との家族旅行で泊まるとしたらどのようなホテルに泊まりたいですか? | 子どもが楽しめるホテル |
| あなたが、夏に泊まるとしたらどのようなホテルに泊まりたいですか? | 空気が美味しいホテル |
| あなたが、秋に泊まるとしたらどのようなホテルに泊まりたいですか? | 紅葉が美しい庭のあるホテル|

Note: Dialogs with SCUDs are in ``data/supplemental/scud/hotel.Example.jsonl``

## ``travel.VanillaUtterances.jsonl``: 2,969 dialogs

This file contains pairs of a question about travel and its answer.

| Question | Answer |
| --- | --- |
| あなたが、今度の連休に国内旅行をするとしたら、どのような旅行をしたいですか? | 家族で遊びもできて、のんびりもできる旅行 |
| あなたが、京都に旅行するとしたら、どのような旅行をしたいですか? | 清水寺を巡る旅行|
| あなたが、学校低学年の子どもと配偶者との家族国内旅行をするとしたら、どのような旅行をしたいですか? | 子供が思いっきりはしゃげるような旅行|

## ``question.single.VanillaUtterances.jsonl``: 1,061 dialogs

This file contains pairs of single question and its answer.

| Operator | Customer |
| --- | --- |
| 当ホテルは朝食バイキングのメニューが豊富で。宿泊いただいたお客様からも高い評価をいただいております。お食事付きのプランはいかがでしょうか | 朝食付きのプランはおいくらですか?|

## ``question.number.VanillaUtterances.jsonl``: 2,013 dialogs

This file contains pairs of question(s) about numbers and its answer.

- ``meta.data["instruction"]``: The instructed type of numbers to make a pair.
- ``meta.data["num_number_q"]``: The crowd worker must use a number greater than or equal to the number written here in the question.
- ``meta.data["num_number_a"]``: The crowd worker must use a number greater than or equal to the number written here in the answer.

## ``question.long_q.VanillaUtterances.jsonl``: 5,576 dialogs

This file contains pairs of question(s) and its answer.
Most operators' utterances contain several sentences.

## ``question.long_a.VanillaUtterances.jsonl``: 3,093 dialogs

This file contains pairs of question(s) and its answer.
Most customers' utterances contain several sentences.

- ``meta.data["q_num_sentences"]``: The number of sentences of the operator's utterance

## ``situation.normal.VanillaUtterances.jsonl``: 3,440 dialogs

This file contains dialogs under specific situation.
The situation is in ``meta.data["situation"]``.

| Situation | Customer | Operator | Customer | Operator |
| --- | --- | --- | --- | --- |
| 出張 | 新幹線駅から近い宿はありますか? | ご旅行でしょうか? | いいえ出張で翌日早朝また移動なので新幹線の駅の近くがいいのですが | かしこまりました、新幹線の駅近くでお探ししますね |

## ``situation.normal.extend.VanillaUtterances.jsonl``: 841 dialogs

This file contains the continuation of several conversations in Y ``situation.normal.VanillaUtterances.jsonl``.
The original id is stored in ``meta.data["original_doc_id"]``.

Crowd workers as asked to make operators suggest two or more accommodations.
The candidate hotels are named with alphabets like ``Aホテル``, ``B旅館``, and ``Cホテル``.

- ``meta.data["finalize"]``: Whether the customer finally selects one candidate or not.
- ``meta.data["single_candidates"]``: Whether the operator suggests only single accommodation.

## ``situation.short.VanillaUtterances.jsonl``: 1,634 dialogs

This file contains dialogs created by rewriting dialogs in ``situation.normal.VanillaUtterances.jsonl``.
Crowd workers were asked to rewrite the client's utterances so that they were in multiple shorter sentences.
The original id is stored in ``meta.data["original_doc_id"]``.

| Situation | Customer | Operator | Customer | Operator |
| --- | --- | --- | --- | --- |
| 出張 | 今度新幹線を使うんです<br>なので駅から近い宿を探して欲しいです |ご旅行ですか? | いや、出張なんです<br>翌朝また移動します<br>だから新幹線の駅近くの宿がいいのですが | 承知致しました<br>新幹線の駅付近でお探し致します|

## ``topic.*.1turn.VanillaUtterance.VanillaUtterances.jsonl``

These files contain customers' queries and dialogs about topics.
The topic id is stored in ``meta.data["topic"]``.

- 1 turn
    - ``topic.L1.1turn.VanillaUtterances.jsonl``: 17,334 queries
    - ``topic.L2.food.1turn.VanillaUtterances.jsonl``: 11,504 queries
        - ``meta.data["topics"]``: other topics if null
        - ``meta.data["topics_dist"]``: topic votes if null
    - ``topic.L2.misc.1turn.VanillaUtterances.jsonl``: 10,926 queries
    - ``topic.L3.1turn.VanillaUtterances.jsonl``: 8,681 queries
- 4 turn
    - ``topic.L1.4turn.VanillaUtterances.jsonl``: 6,294 dialogs
    - ``topic.L2.food.4turn.VanillaUtterances.jsonl``: 3,122 dialogs

| Topic | Query |
| --- | --- |
| ベッド | ツインは一いくらですか |
| 風呂 | 洗い場にアメニティが揃っているお風呂にして下さい |
| 食事::食材::野菜 | 食事は肉と魚が苦手なので野菜の食材がたくさん食べれる宿はありますか。|
| 食事::アレルギー::そば | そばにアレルギー反応があります。そば粉を使用した料理以外でお願いします。|/vanilla/topic.L2.food.4turn.VanillaUtterances.jsonl
