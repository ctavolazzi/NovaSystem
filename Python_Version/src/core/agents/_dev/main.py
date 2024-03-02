# Initialization and running the group chat
from agents.DebateCoordinator import DebateCoordinator
from agents.AffirmativeDebater import AffirmativeDebater
from agents.NegativeDebater import NegativeDebater
from agents.SensoryInputAgent import SensoryInputAgent
from agents.groupchat.DebateGroupChat import DebateGroupChat
from agents.groupchat.UserProxyAgent import DebateTerminator

# Assume 'llm_config' and 'config_list_gpt4' are already defined
agents = [DebateCoordinator(llm_config), AffirmativeDebater(llm_config), NegativeDebater(llm_config), SensoryInputAgent(llm_config), DebateTerminator()]
group_chat = DebateGroupChat(agents=agents, messages=[], max_round=30)

# Start the debate simulation
group_chat.start()
