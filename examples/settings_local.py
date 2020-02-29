SERVICE_BUS_CONNECTION_STRING = "Endpoint=sb://lieturd-factoring-test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=GA/6mNlMcl/4uIYbg8CF7L4MXlNZeRdkYqcmjb/fzJQ="

try:
    from settings_local import *
except ImportError:
    pass