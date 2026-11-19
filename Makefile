FACTORIES := .dotfiles/factories

.PHONY: daily note

daily: ## Create today's daily note
	@uv run $(FACTORIES)/new-daily.py

# `make note my-title` — the words after `note` are the title. Extra words
# would otherwise be unknown targets, so swallow them with a catch-all rule.
ifeq ($(filter note,$(MAKECMDGOALS)),note)
NOTE_TITLE := $(strip $(filter-out note,$(MAKECMDGOALS)))
%:
	@:
endif

note: ## Create a note: make note my-title
	@test -n "$(NOTE_TITLE)" || { echo 'usage: make note my-title'; exit 1; }
	@uv run $(FACTORIES)/new-note.py "$(NOTE_TITLE)"
