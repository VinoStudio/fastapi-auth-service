#####################################################################################
# App is using ssl generated keys for jwt-tokens. Here instructions how to make one #
#####################################################################################

# GENERATE an RSA private-key with 2048 size
openssl genrsa -out jwt-private.pem 2048

#GENERATE a public key from the private key, which we'll use as public certificate
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem