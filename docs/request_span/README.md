# Request span (要望スパン)

`Request_span` is a short phrase that is extracted from user utterance and represents user's requests to the hotel.
These spans can be used for dialog state tracking or as a search query in the hotel database.

## ``data/main/request_span``

- 3,393 spans are annotated for 210 dialogues.
- Each span is labeled with one of these categories: `['service', 'schedule', 'budget', 'guest_num', 'child', 'accommodation', 'facility', 'travel', 'location', 'room', 'bath', 'food']`.
- Each span is annotated with importance label: `strong/neutral/weak`.
- Refer to `manuals` for more detailed description of above annotations.

## Related publications

- [A Sequence-to-sequence Approach for Numerical Slot-filling Dialog Systems](https://aclanthology.org/2020.sigdial-1.34) (Shi, SIGDIAL 2020)
- [A Span Extraction Approach for Dialog State Tracking: A Case Study in Hotel Booking Application](https://www.anlp.jp/proceedings/annual_meeting/2021/pdf_dir/P8-10.pdf) (Shi, 言語処理学会 NLP2021)
