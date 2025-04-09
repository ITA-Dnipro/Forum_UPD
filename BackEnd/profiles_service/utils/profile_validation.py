from models import StartupProfileOrm, InvestorProfileOrm

def validate_startup(startup_profile: StartupProfileOrm):
    if startup_profile.is_fop and not startup_profile.rnokpp:
        return False
    
    elif not startup_profile.is_fop and not startup_profile.edrpou:
        return False
    
    if not startup_profile.phone:
        return False
    
    if not startup_profile.startup_idea:
        return False

    return True


def validate_investor(investor_profile: InvestorProfileOrm):
    if investor_profile.is_legal_entity and not investor_profile.rnokpp:
        return False
    
    elif not investor_profile.is_legal_entity and not investor_profile.edrpou:
        return False
    
    if not investor_profile.phone:
        return False
    
    return True
    
