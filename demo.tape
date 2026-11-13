# Demo recording for the Flashcard Scheduler CLI.
#
# Requires https://github.com/charmbracelet/vhs. Optional for v0.1; the GIF is
# not part of the deliverable. Run with: vhs demo.tape
Output demo.gif
Set Shell "bash"
Set FontSize 14
Set Width 1000
Set Height 700
Set Padding 20

Type "# Import/validate a deck"
Enter
Type "./app import tests/fixtures/new_cards_deck.json"
Enter
Sleep 1s

Type "# Review the first card with grade 4"
Enter
Type "./app review tests/fixtures/new_cards_deck.json word-1 4 --reference-date 2026-01-15"
Enter
Sleep 1s

Type "# Due and stats"
Enter
Type "./app due tests/fixtures/mixed_deck.json --reference-date 2026-01-15"
Enter
Type "./app stats tests/fixtures/mixed_deck.json"
Enter
Sleep 2s
