
# フォーマット

## データ本体: [``data/main/dialog/json/*.json``](../../data/main/dialog/json)

スキーマは[``asdc.schema.dialog``](../../asdc/schema/dialog.py)の[``Utterances``クラス](../../asdc/schema/dialog.py#:~:text=class%20Utterances)．

- 誤字の修正
    - 元の発話内容に誤字がある場合は、修正を行った．
    - 修正前と修正後の投稿内容は、同じjsonファイル内でそれぞれカラム``text``、``text_fixed``に記載した．
    - ``text_fixed``は、誤植の修正がある場合にのみ、追加されている．誤植の修正がなかったものについては、``text_fixed``は存在しない．
- 正規化
    - 元データの発話内のタブ(U+0009)は全てスペース(U+0020)に置換している
    - NFKC正規化している．
- ``purpose``の割り振り
    - 機械学習用に``purpose``は``train : dev : test = 0.8 : 0.2 : 0.2``となるように割り振っている
    - ``train``は125対話，``dev``は41対話，``test``は44対話
- ``name``
    - ``operator_1``は観光業界での接客経験のあるオペレータ役 (対話ID=``001``〜``126``)
    - ``operator_2``は観光業界での接客経験のないオペレータ役 (対話ID=``127``〜``210``)
    - ``customer_1``から``customer_35``はカスタマー役

## 文境界付与済みテキスト: [``data/main/dialog/text/*.tsv``](../../data/main/dialog/text)

- 1列目が発話者，2列目が発話内容
- 発話内容は，改行を``▁`` (U+2581) ，文境界を``│`` (U+2502)で示している
