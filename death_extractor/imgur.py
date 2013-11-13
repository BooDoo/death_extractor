import pyimgur

#imgur things
def imgur_init_with_refresh(client_id, client_secret, refresh_token=None):
  imgur = pyimgur.Imgur(client_id, client_secret)
  imgur.refresh_token = refresh_token
  return imgur

def imgur_manual_auth(self):
  auth_url = self.authorization_url('pin')
  print auth_url
  pin = raw_input("input PIN:\n")
  access_token, request_token = self.exchange_pin(pin)
  print "access_token:",access_token
  print "refresh_token:",refresh_token
  return refresh_token
