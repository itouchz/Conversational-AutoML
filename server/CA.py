import rule_based as rb


def rule_based_response(current_state, user_query, await_feature):
    return rb.get_response(current_state, user_query, await_feature)

def rule_based_reset():
    return rb.reset_slot()