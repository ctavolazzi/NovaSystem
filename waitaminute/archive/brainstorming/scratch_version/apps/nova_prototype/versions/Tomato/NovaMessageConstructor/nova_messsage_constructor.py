from nova_continuation_text import nova_continuation_text as nct
from nova_system_message import nova_system_message as nsm
from nova_primer_text import nova_primer_text as npt
from Utils.formatters.openai_message_formatter import openai_message_formatter as omf

def nova_message_constructor(messages):
  return messages