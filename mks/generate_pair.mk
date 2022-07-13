
include mks/path.mk

all: generate_pair_main \
	generate_pair_sup

INPUT_SCUD_DIR:=$(DATA_MAIN_SCUD_JSONL_DIR)
INPUT_JSON_DIR:=$(DATA_MAIN_JSON_DIR)
CONTEXT:=1
OUTPUT:=/please/designate
TRAIN_MAX_DISTANCE_UTTR:=$(CONTEXT)
TEST_MAX_DISTANCE_UTTR:=999999

INPUT_SUP_SCUD_DIR:=$(DATA_SUP_SCUD_DIR)


##### General Rules

%/train.jsonl: %/all.jsonl
	mkdir -p $(dir $@) \
	&& python3 -m asdc.convert.split \
		-i $< \
		--train $@.tmp \
		--dev $*/dev.jsonl \
		--test $*/test.jsonl \
		--context=$(CONTEXT) \
		--train_max_distance_uttr $(TRAIN_MAX_DISTANCE_UTTR) \
		--test_max_distance_uttr $(TEST_MAX_DISTANCE_UTTR) \
	&& mv $@.tmp $@


##### main

OUTPUT_MAIN_DIR:=$(OUTPUT)/main
OUTPUT_MAIN_ALL:=$(OUTPUT_MAIN_DIR)/all.jsonl
OUTPUT_MAIN_TRAIN:=$(OUTPUT_MAIN_DIR)/train.jsonl

$(OUTPUT_MAIN_ALL): $(INPUT_SCUD_DIR) $(INPUT_JSON_DIR)
	mkdir -p $(dir $@) \
	&& python3 -m asdc.convert.pair \
		-i $(INPUT_SCUD_DIR) --ref $(INPUT_JSON_DIR) -o $@

$(OUTPUT_MAIN_TRAIN): $(OUTPUT_MAIN_ALL)
generate_pair_main: $(OUTPUT_MAIN_ALL) $(OUTPUT_MAIN_TRAIN)


OUTPUT_SUP_DIR:=$(OUTPUT)/sup
OUTPUT_SUP_ALL:=$(OUTPUT_SUP_DIR)/all.jsonl
OUTPUT_SUP_TRAIN:=$(OUTPUT_SUP_DIR)/train.jsonl
INPUT_SUP_EXTRA:=/dev/null

$(OUTPUT_SUP_ALL): $(INPUT_SUP_SCUD_DIR) $(INPUT_SUP_EXTRA)
	mkdir -p $(dir $@) \
	&& find $(INPUT_SUP_SCUD_DIR) -type f | sort | xargs cat > $@.tmp \
	&& cat $(INPUT_SUP_EXTRA) >> $@.tmp \
		&& mv $@.tmp $@

$(DATA_SUP_DIR): $(OUTPUT_SUP_ALL)
	mkdir -p $(dir $@) \
	  && python3 -m asdc.convert.split \
		-i $< \
		--train $@.tmp \
		--dev $*/dev.jsonl \
		--test $*/test.jsonl \
		--context=$(CONTEXT) \
		--train_max_distance_uttr $(TRAIN_MAX_DISTANCE_UTTR) \
		--test_max_distance_uttr $(TEST_MAX_DISTANCE_UTTR) \
	&& mv $@.tmp $@


generate_pair_sup: $(OUTPUT_SUP_ALL) $(OUTPUT_SUP_TRAIN)


##### Misc

clean:
	rm -rf $(OUTPUT_MAIN_DIR) $(OUTPUT_SUP_DIR)


.PHONY: all clean
.DELETE_ON_ERROR:
