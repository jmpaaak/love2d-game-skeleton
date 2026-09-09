LOVE ?= love
ZIP ?= zip
BUILD_DIR ?= build
LOVE_PACKAGE ?= $(BUILD_DIR)/game.love

.PHONY: test smoke love asset-contract verify clean

HEADLESS_ENV = GAME_HEADLESS=1 SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy

test:
	$(HEADLESS_ENV) GAME_UNIT=1 $(LOVE) .

smoke:
	$(HEADLESS_ENV) $(LOVE) .

love:
	@mkdir -p "$(BUILD_DIR)"
	@rm -f "$(LOVE_PACKAGE)"
	@$(ZIP) -q -9 -r "$(LOVE_PACKAGE)" . \
		-x '.git' -x '.git/*' -x '.github/*' -x 'build/*' \
		-x 'tmp/*' -x 'logs/*' -x '.venv/*' -x '__pycache__/*' \
		-x '.env' -x '.env.*' -x '.DS_Store' -x '*.swp'

asset-contract:
	python3 tools/verify_asset_pipeline_contract.py

verify: asset-contract test smoke love
	$(HEADLESS_ENV) $(LOVE) "$(LOVE_PACKAGE)"
	python3 tools/verify_bundle.py "$(LOVE_PACKAGE)"

clean:
	rm -rf "$(BUILD_DIR)"
