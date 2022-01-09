
def no_content_response(message=None):
    return {"code": 4000, "message": message}


def dome_not_found():
    return {"code": 4007, "message": "No such dome”"}
    
def user_not_found():
     return {"code": 4000, "message": "No such user"}

def success_response(result=None):
    # result must be dict it's a user data.
    return {"code":200,
            "jsonrpc":"2.0", 
            "result":result,
            "id":2
        }
