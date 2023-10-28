from Modules.Helpers import NovaHelper

from NovaSystem import NovaSystem

from Modules.Funsies.zalgo_text import zalgo_text
text_corruptor = zalgo_text

NovaHelper.stc(f"Welcome to the NovaSystem.\n")

stc = NovaHelper.stc

stc(f"Initializing...\n")

stc("Nova can help you with many things, including:\n")
stc(" - Writing\n")
stc(" - Programming\n")
stc(" - Finding the meaning of life\n")
stc(f"_______________{text_corruptor('______________________')}\n", .05)

from Modules.Helpers.clear_console import clear_console

clear_console()

stc("Nova system cannot help you with the meaning of life.\n")
stc("But it can help you with the other two.\n")
stc("And probably some other stuff too, who knows, I just work here.\n")
stc("_______________________________________________________________\n")

clear_console()

stc("Initializing NovaSystem...\n")
stc("NovaSystem initialized.\n")
stc("That was not a glitch, it was a feature.\n")

