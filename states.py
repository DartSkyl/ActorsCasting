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
    fee = State()
    geo_location = State()
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
    edit_fee = State()
    edit_geo_location = State()
    edit_portfolio = State()
    edit_social = State()

    setup = State()

    playing_age_setup = State()
    education_setup = State()
    contacts_setup = State()
    agent_contact_setup = State()
    have_experience_setup = State()
    roles_type_interest_setup = State()
    fee_setup = State()
    geo_location_setup = State()
    portfolio_setup = State()
    social_setup = State()
    passport_age_setup = State()


class AdminStates(StatesGroup):
    """Для администраторов"""
    # Взаимодействие с юзер-ботом
    start_add_user_bot = State()
    api_id_input = State()
    api_hash_input = State()
    phone_number_input = State()
    check_data = State()
    change_api_id = State()
    change_api_hash = State()
    change_phone_number = State()
    code_input = State()

    # Взаимодействие с БД
    set_period = State()
    set_user_date = State()

    second_text = State()


class AddNewCasting(StatesGroup):
    """Для добавления нового кастинга"""
    description = State()
    cath_file = State()

    e_description = State()
    e_file = State()
    edit_new_casting = State()
