from aiogram.fsm.state import StatesGroup, State


class ActorsState(StatesGroup):
    """Для актеров"""
    actor_name = State()
    passport_age = State()
    playing_age = State()
    education = State()
    sex = State()
    agent_contact = State()
    have_experience = State()
    roles_type_interest = State()
    fee = State()
    portfolio = State()
    social = State()
    preview = State()

    edit_actor_name = State()
    edit_passport_age = State()
    edit_playing_age = State()
    edit_education = State()
    edit_sex = State()
    edit_agent_contact = State()
    edit_have_experience = State()
    edit_roles_type_interest = State()
    edit_fee = State()
    edit_portfolio = State()
    edit_social = State()

    setup = State()

    playing_age_setup = State()
    education_setup = State()
    agent_contact_setup = State()
    have_experience_setup = State()
    roles_type_interest_setup = State()
    fee_setup = State()
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
    delete_user = State()
    newsletter = State()

    casting_text = State()
    add_text = State()

    sub_add = State()
    sub_del = State()
    show_user = State()


class AddNewCasting(StatesGroup):
    """Для добавления нового кастинга"""
    project_type = State()
    project_name = State()
    filming_dates = State()
    geolocation = State()
    role_type = State()
    sex = State()
    playing_age = State()
    role_name = State()
    role_description = State()
    additional_requirements = State()
    fee = State()
    have_prob = State()
    probe_file = State()
    contacts = State()
    rules = State()
    dop_info = State()
    preview = State()

    edit_project_type = State()
    edit_project_name = State()
    edit_filming_dates = State()
    edit_geolocation = State()
    edit_role_type = State()
    edit_sex = State()
    edit_playing_age = State()
    edit_role_name = State()
    edit_role_description = State()
    edit_additional_requirements = State()
    edit_fee = State()
    edit_have_prob = State()
    edit_probe_file = State()
    edit_contacts = State()
    edit_rules = State()
    edit_dop_info = State()
    new_text_prob = State()
    new_text_file = State()

