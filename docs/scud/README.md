# SCUD

Self-Contained Utterance Description (SCUD) describes the intent of an utterance in a dialog with multiple simple natural sentences without the context.
We proposed it in the LREC 2022 paper.
([NLP 2021の論文](https://www.anlp.jp/proceedings/annual_meeting/2021/pdf_dir/P2-5.pdf)で「要約文」と呼んでいたものを改称)

There are SCUD annotations for 210 dialogs in `main`.
They are in two formats.

## ``data/main/main.Example.jsonl``

- Schema: [``asdc.schemaexample.Example``](../asdc/schema/example.py)
- Auto generated from ``data/main/scud`` by using ``asdc.convert.main_scud_example``
- This format is used for training of auto SCUD generator

## ``data/main/scud``

- Schema: The class ``Scud`` in [``asdc.schema.dialog``](../asdc/schema/dialog.py)
    - ``groups``: SCUDと発話の対応関係 ([NLP 2021の論文](https://www.anlp.jp/proceedings/annual_meeting/2021/pdf_dir/P2-5.pdf) 3.2節を参照)
    - ``queries``: SCUDと対応する「対話の最後にオペレータが挙げる要件」 ([NLP 2021の論文](https://www.anlp.jp/proceedings/annual_meeting/2021/pdf_dir/P2-5.pdf) 3.3節を参照)
        - ``Utterances``クラスの``meta.conditions``の要件と対応づいている
        - その要件が最も関係のある場合，``★`` (U+2605) を要件の先頭に付与
        - 要件として列挙されるべきだがされていない場合，``@`` (U+0040) を記入している
