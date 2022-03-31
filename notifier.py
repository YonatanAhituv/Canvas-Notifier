from twilio.rest import Client



def sendMessage(destination, contents):
    message = client.messages \
        .create(
            body='This is the ship that made the Kessel Run in fourteen parsecs?',
            from_='+15017122661',
            to='+15558675310'
        )
