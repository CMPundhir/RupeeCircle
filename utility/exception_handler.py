from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import ErrorDetail


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    status_code = 406
    # message = repr(exc)
    message = str(exc)
    try:
        response = exception_handler(exc, context)
        #print(f"custom_exception_handler : ")
        # Now add the HTTP status code to the response.
        if response is not None:
            status_code = response.status_code
            message = response.data
    except Exception as e:
        #message = repr(e)
        message = str(e)
    message2 = simplifySerializerErrors(message)
    print(f"custom_exception_handler : {message}")
    return Response({"status_code": status_code, "message": message2, "error": message}, status=status_code)


def simplifySerializerErrors(errors):
    try:
        print(type(errors))
        if type(errors) is str:
            return errors
        res = ""
        for k in dict(errors):
            v = errors[k]
            if isinstance(v, ErrorDetail):
                if not res:
                    res = v
                else:
                    if isinstance(v, str):
                        res = res + ", " + str(v)
            else:
                for i in v:
                    print(i)
                    if not res:
                        res = i
                    else:
                        if isinstance(i, str):
                            res = res + ", " + str(i)
                        else:
                            pass
                            # for i in v:
                            #     res = res + ", " + str(i)
            #print(f"{k} : {str(v[0])}")
        if not res:
            res = "Something went wrong"
        return res
    except Exception as e:
        print(e)
        return errors


