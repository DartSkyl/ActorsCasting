from aiogram.fsm.state import StatesGroup, State


class ActorsState(StatesGroup):
    """Для актеров"""
    actor_name = State()
    passport_age = State()
    playing_age = State()
    education = State()
    sex = State()
    contacts = State()
    agent_contact = State()
    have_experience = State()
    roles_type_interest = State()
    # projects_interest = State()
    geo_location = State()
    # willingness_to_come = State()
    portfolio = State()
    social = State()
    preview = State()

    edit_actor_name = State()
    edit_passport_age = State()
    edit_playing_age = State()
    edit_education = State()
    edit_sex = State()
    edit_contacts = State()
    edit_agent_contact = State()
    edit_have_experience = State()
    edit_roles_type_interest = State()
    edit_geo_location = State()
    edit_portfolio = State()
    edit_social = State()
