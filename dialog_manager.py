class DialogState:
    START        = "start"
    WAIT_CITY    = "wait_city"
    WAIT_DATE    = "wait_date"
    SHOW_WEATHER = "show_weather"
    SHOW_TIME    = "show_time"
    SHOW_DATE    = "show_date"
    SHOW_HELP    = "show_help"
    SMALLTALK    = "smalltalk"


_user_states: dict = {}

_user_data: dict = {}


def get_state(user_id) -> str:
    return _user_states.get(user_id, DialogState.START)


def set_state(user_id, state: str):
    _user_states[user_id] = state


def get_user_data(user_id) -> dict:
    if user_id not in _user_data:
        _user_data[user_id] = {}
    return _user_data[user_id]


def set_user_data(user_id, key: str, value):
    if user_id not in _user_data:
        _user_data[user_id] = {}
    _user_data[user_id][key] = value


def reset_user_data(user_id):
    _user_data[user_id] = {}