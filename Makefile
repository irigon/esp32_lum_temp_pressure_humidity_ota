# === CONFIGURATION ===
SRC_DIR = src
BUILD_DIR = build

MPY_CROSS = mpy-cross
MPREMOTE = mpremote

# Files that MUST stay as .py for MicroPython to auto-run
ENTRY_PY_FILES = boot.py main.py version.txt

.PHONY: all compile flash clean repl

all: compile flash

compile:
	@if [ ! -f $(SRC_DIR)/secrets.py ]; then \
		echo "\033[1;31mERROR: $(SRC_DIR)/secrets.py not found! OTA and Wi-Fi will not work. Use /src/secrets.py.template for it.\033[0m"; \
		exit 1; \
	fi
	@mkdir -p $(BUILD_DIR)
	@for file in $(SRC_DIR)/*.py $(SRC_DIR)/*.txt; do \
		base=$$(basename $$file); \
		if echo "$(ENTRY_PY_FILES)" | grep -wq "$$base"; then \
			echo "Copying $$file (not compiling)..."; \
			cp $$file $(BUILD_DIR)/$$base; \
		else \
			echo "Compiling $$file to $(BUILD_DIR)/$${base%.py}.mpy..."; \
			$(MPY_CROSS) $$file -o $(BUILD_DIR)/$${base%.py}.mpy; \
		fi \
	done

flash:
	@for file in $(BUILD_DIR)/*; do \
		echo "Flashing $$file..."; \
		$(MPREMOTE) cp $$file :; \
	done

clean:
	@echo "Cleaning files on ESP32..."
	@$(MPREMOTE) exec "import os; [os.remove(f) for f in os.listdir() if not f.startswith('.')]"
	@echo "Cleaning local build directory..."
	@rm -rf $(BUILD_DIR)

repl:
	$(MPREMOTE) repl

