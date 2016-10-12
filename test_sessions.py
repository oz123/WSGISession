from wsgisession import SessionIdChecked, SlottedSessionIdChecked


sc = SessionIdChecked()
try:
    sc.id = "asdfasdf?_"
except ValueError:
    print("ValueError caught")
    sc.id = "asdfasdf"
    print(sc.id)

sc = SlottedSessionIdChecked()

sc.id = "asdfadsfadsf>?"
