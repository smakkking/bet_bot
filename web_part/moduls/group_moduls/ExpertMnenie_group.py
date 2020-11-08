WALL_URL = 'https://vk.com/csgo_expert_dota'
NAME = 'ExpertMnenie'

from moduls.bookmaker_moduls import BETSCSGO_betting 
  
BET_TEMPLATES = BETSCSGO_betting.PHOTO_PARSING_TEMPLATES # + other bookmakers templates

# here may be other speciefic templates, so add them to BET_TEMPLATES
# like BET_TEMPLATES += [(template, parse)]