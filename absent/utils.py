

def get_responder(request):
    user = request.user
    # The person who obtains approval
    # 1. If it is the department leader
    if user.department.leader.uid == user.uid:
        # 1.1. If it is the board of directors
        if user.department.name == 'Board Department':
            responder = None
        else:
            responder = user.department.manager
    # 2. If it is not the department leader
    else:
        responder = user.department.leader
    return responder