
# SCUDアノテーション

## SCUDアノテーションと対応付け

### CSVからJSONLに変換

以下の書式で，発話のSCUDを記したCSVファイル(例:``scud_tmp.csv``)を用意する．

```csv
文ID,SCUD,関係する最終クエリ(1行1文),メモ
```

これをJSONL(``data/original/main/scud/sentence/*.jsonl``)に変換する．
（SCUDはNFKC正規化されている）

```bash
poetry run python3 -m asdc.convert.scud_csv2jsonl -i ./data/main/dialog/json -s scud_tmp.csv -o ./data/original/main/scud/sentence
```

### JSONLからDoccano入力用に変換

```bssh
# 1からアノテーションする場合
# * SCUDと発話で文字が一致する箇所を仮の対応付けとして出力する
poetry run python3 -m asdc.convert.doccano -i data/original/main/scud/sentence -o doccano.input.jsonl --ref ./data/main/dialog/json

# 既存のアノテーションを利用する場合
poetry run python3 -m asdc.convert.doccano -i data/original/main/scud/sentence -o doccano.input.jsonl --ref ./data/main/dialog/json --use data/main/scud
```

- 出力されたファイルをDoccanoにインポート
- ラベルに``エラー``，``1``, ``2``, ``3``, ..., ``外0``，``外1``, ..., ``両0``, ``両1``, ...を追加，色を変更
- アノテーション
    - 画面には「文脈，文ID，対象の発話，SCUD」の順で並んでいる
- SCUDの訂正
    - Doccanoの管理者画面``/admin/api/document/``で対象の文書を探し，最終行を編集することで可能
    - 編集後，Doccanoで対応付けも修正すること

### Doccanoのアノテーションの反映

Doccanoから``JSON(Text-Labels)``でデータをダウンロードして変換する．

```bash
poetry run make generate_main_scud DOCCANO_JSON1=~/Downloads/file.json1
```

### SCUDの修正

``data/original/main/scud/sentence``と``data/original/main/scud/doccano``のファイル
(必要に応じて``data/main/scud``内のファイルも)
を修正し，

```bash
poetry run python3 -m asdc.convert.doccano -i data/original/main/scud/sentence -o doccano.input.jsonl --ref ./data/main/dialog/json --use data/main/scud
```

でDoccano用のファイルを生成し，Doccano上で修正する．

### SCUDの修正（大量にある場合）

CSVファイルに

```csv
文ID,修正前SCUD,修正後SCUD,メモ
```

という書式で``sheet.csv``に記入する．

```bash
# アップデート
rm ./data/original/main/scud/sentence/*
poetry run python3 -m asdc.convert.update_scud_text -s ./data/original/main/scud/sentence -i sheet.csv -o ./tmp_jsonl && \
    mv ./tmp_jsonl/* ./data/original/main/scud/sentence

# Doccano入力用ファイルの生成
# 変更がないアノテーションを無視する場合は--nosameオプションをつける
poetry run python3 -m asdc.convert.update_scud_text -s data/main/scud -i sheet.csv \
    | poetry run python3 -m asdc.convert.doccano -i /dev/stdin --ref ./data/main/dialog/json -o doccano.input.jsonl
```
