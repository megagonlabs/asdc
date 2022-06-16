# 対話行為データフォーマット

1. ``utterance_id``: 全ての発話に付与したユニックID
2. ``src_file_id``: 対話セッションに付与したユニックID
3. ``nth``: 対話内における発話のindex
4. ``speaker``: agent or user
5. ``utterance``: 発話テキスト
6. ``speech_act``: 対話行為ラベル
    - `質問`, `確認`, `伝達`, `要求`, `はい`, `いいえ`, `その他`, `照応要求`, `感想` のいずれか
7. ``has_typos``: 発話文内にTypoがあるかどうかを示すフラグ
8. ``difficult``: Annotationが迷った時のフラグ
9. ``duplicate``: 重複を示すフラグ
10. ``memo``: 補足メモ
