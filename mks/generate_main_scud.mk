
include mks/path.mk

DOCCANO_JSON1:=/please/designate
$(DATA_MAIN_SCUD_DOCCANO_DIR): $(DOCCANO_JSON1)
	python3 -m asdc.convert.doccano --trim -i $< -o $@ --ref $(DATA_MAIN_JSON_DIR)


$(DATA_MAIN_SCUD_SENTENCE_DIR): $(DATA_MAIN_SCUD_DOCCANO_DIR)
	python3 -m asdc.convert.doccano -i $(DATA_MAIN_SCUD_SENTENCE_DIR) \
		--result $(DATA_MAIN_SCUD_DOCCANO_DIR) \
		--update \
		-o $(DATA_MAIN_SCUD_SENTENCE_DIR).tmp \
		--ref $(DATA_MAIN_JSON_DIR) \
		&& mv $(DATA_MAIN_SCUD_SENTENCE_DIR).tmp $(DATA_MAIN_SCUD_SENTENCE_DIR)

update_original_scud_text: $(DATA_MAIN_SCUD_SENTENCE_DIR)



generate_main_scud: $(DATA_MAIN_SCUD_JSONL_DIR) $(DATA_MAIN_SCUD_DOCCANO_DIR)
$(DATA_MAIN_SCUD_JSONL_DIR): $(DATA_MAIN_SCUD_SENTENCE_DIR) $(DATA_MAIN_SCUD_DOCCANO_DIR)
	python3 -m asdc.convert.doccano -i $(DATA_MAIN_SCUD_SENTENCE_DIR) \
		--result $(DATA_MAIN_SCUD_DOCCANO_DIR) \
		--ref $(DATA_MAIN_JSON_DIR) \
		-o $(DATA_MAIN_SCUD_JSONL_DIR)

