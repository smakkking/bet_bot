from moduls.bookmaker_moduls import BETSCSGO_betting
from moduls.group_moduls import ExpertMnenie_group, \
                                CSgoVictory_group, \
                                BETSPEDIA_group, \
                                SaveMoney_group, \
                                Aristocrat_group, \
                                CSgo99percent_group, \
                                l1KKK_group,\
                                AcademiaBets_group,\
                                BetOn_group,\
                                PrivatePrognoze_group


GROUP_OFFSET = {
    ExpertMnenie_group.NAME: ExpertMnenie_group,
    #CSgoVictory_group.NAME: CSgoVictory_group,
    #BETSPEDIA_group.NAME: BETSPEDIA_group,
    #SaveMoney_group.NAME: SaveMoney_group,
    #Aristocrat_group.NAME: Aristocrat_group,
    #CSgo99percent_group.NAME: CSgo99percent_group,
    l1KKK_group.NAME: l1KKK_group,
    AcademiaBets_group.NAME: AcademiaBets_group,
    BetOn_group.NAME: BetOn_group,
    PrivatePrognoze_group.NAME: PrivatePrognoze_group
}

BOOKMAKER_OFFSET = {
    BETSCSGO_betting.NAME: BETSCSGO_betting,
}