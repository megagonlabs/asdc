
# 学習用データの作成

## Text2Text用データ: ``data/main/main.Example.jsonl``

```bash
poetry run python3 -m asdc.convert.main_scud_example -i data/main/scud --ref data/main/dialog/json -o data/main/main.Example.jsonl
```

- ``all.jsonl``: SCUDをまとめたファイル
- ``train.tsv`` ``dev.tsv``, ``test.tsv``: Text2Textの学習・開発・訓練のためのデータ
    - ``ID 入力 出力``の書式

## アライメント

SCUDと入力とのアライメントは以下のコマンドで生成できる．

```bash
poetry run python3 -m asdc.convert.scud_alignment -i ./generated_examples_dir/main/all.jsonl -o ./generated_examples_dir/main/alignment.jsonl
```
