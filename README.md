
# Accommodation Search Dialog Corpus (in Japanese)

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Attribution 4.0 International License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a>
[![CI](https://github.com/megagonlabs/asdc/actions/workflows/ci.yml/badge.svg)](https://github.com/megagonlabs/asdc/actions/workflows/ci.yml)
[![Typos](https://github.com/megagonlabs/asdc/actions/workflows/typos.yml/badge.svg)](https://github.com/megagonlabs/asdc/actions/workflows/typos.yml)

## Main part: [``data/main``](data/main)

The main part of this corpus consists of 210 Japanese dialogs between two people acting as a customer and an operator in a fictitious accommodation consultation service by using [Slack](https://slack.com/).
In a dialog, the customer informed the operator of their situation and needs.
Then based on the information, the operator conducted a search to meet the customer's request.
The dialog was finished once the operator judged that the requirements were specific enough to narrow appropriate accommodations.
Dialogs are in two formats.

- [Text](data/main/dialog/text): ``data/main/dialog/text/*.tsv``
- [JSON](data/main/dialog/json): ``data/main/dialog/json/*.json``

Please read [documents](docs/dialog) for more details.

### Annotations

| Name | Doc | Data |
| --- | --- | --- |
| SCUD | [Doc](docs/scud) | [``data/main/scud``](data/main/scud) |
| Dialog act | [Doc](docs/dialog_act) | [``data/main/dialog_act``](data/main/dialog_act) |
| Request spans | [Doc](docs/request_span) | [``data/main/request_span``](data/main/request_span) |

The number of SCUDs is about 3,500.

| Name | Utterance | SCUD | DA | RS |
| --- | --- | --- | --- | ---|
| Agent | さようでございますか。 ||||
| | それでは、駐車場を無料でご利用できるホテルをお探しします。||||
| | 立地ですが、観光地をまわりやすい場所はいかがでしょうか？||||
| User | はい、観光地をまわりやすい場所にあるといいですね。| ホテルが観光地をまわりやすい場所にあると良い。 | はい ||
| | ただ1番の目的は出雲大社なので、そこまでアクセスがよければ助かります。|【customer】の1番の目的が出雲大社だ。<br>出雲大社までアクセスが良いホテルだと良い。|要求|出雲大社=>立地<br>アクセスがよければ=>立地|

## Supplemental SCUD part: [``data/supplemental/scud``](data/supplemental/scud): 37,171 examples

Files in ``data/supplemental/scud`` are Supplemental fictitious dialogs with SCUD annotations.
Please read [the documents](docs/supplemental/README.md) for more details.

- Most dialogs consist of a single pair of an agent utterance and a user utterance.
- Dialogs are stored in files in [``data/supplemental/utterances``](data/supplemental/utterances) : 36,400 dialogs

## Supplemental incorrect SCUD part: [``data/supplemental/incorrect_scud``](data/supplemental/incorrect_scud): 3,351 examples

Files in ``data/supplemental/incorrect_scud`` are Supplemental fictitious dialogs with SCUD annotations.
If ``meta['meta']`` of an example is ``true``, the example has incorrect SCUDs.

## Vanilla part: [``data/vanilla``](data/vanilla): 83,840 dialogs

Files in ``data/vanilla`` are fictitious dialogs or queries made by crowd workers with no SCUD annotations.
The number is over 100,000.
Please read [the documents](docs/vanilla/README.md) for more details.

| Utterance 1 | Utterance 2 |
| --- | --- |
| あなたが、高級ホテルに泊まるとしたらどのようなホテルに泊まりたいですか? | 食事と景色が美しく、バラ風呂などの工夫があるホテル
| あなたが、1週間の国内旅行ができることになったら、どのような旅行をしたいですか? | ゆっくり読書をたのしむ旅行|

## References

### Dialog collection and SCUDs

1. Yuta Hayashibe.
    Self-Contained Utterance Description Corpus for Japanese Dialog.
    Proc of LREC, pp.1249-1255. (LREC 2022)
    [[PDF]](http://www.lrec-conf.org/proceedings/lrec2022/pdf/2022.lrec-1.133.pdf)
2. 林部祐太．
    要約付き宿検索対話コーパス．
    言語処理学会第27回年次大会論文集，pp.340-344. 2021. (NLP 2021)
    [[PDF]](https://www.anlp.jp/proceedings/annual_meeting/2021/pdf_dir/P2-5.pdf)

### Dialog acts and request spans

1. Hongjie Shi.
    A Span Extraction Approach for Dialog State Tracking: A Case Study in Hotel Booking Application.
    言語処理学会第27回年次大会論文集，pp.1593-1598. 2021. (NLP 2021)
    [[PDF]](https://www.anlp.jp/proceedings/annual_meeting/2021/pdf_dir/P8-10.pdf)
2. Hongjie Shi.
    A Sequence-to-sequence Approach for Numerical Slot-filling Dialog Systems.
    Proc of SIGdial, pp.272-277. 2020. (SIGdial 2020)
    [[PDF]](https://aclanthology.org/2020.sigdial-1.34.pdf)

## License

- Corpus, annotations and documents are licensed under [Creative Commons Attribution 4.0 International License](LICENSE.txt)
- Programs are licensed under [Apache License, Version 2.0](LICENSE.APACHE.2.0.txt)
