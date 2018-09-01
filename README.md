# iBriz | Idol Token (ICON Foundation)

<img src="https://ibriz.ai/wp-content/themes/ibriz-blog/assets/images/ibriz.svg" width="80" height="80"><img src="https://icondev.io/img/logo.png" width="188" height="35">
### Installing **IdolToken** to tbears 
``````sh
$ tbears deploy -t tbears idol_token -f hx65f6e18d378b57612a28f72acb97021eaa82aa5a -k keystore.json -c tbears_cli_config.json
``````
### Sample _keystore.json_ file  ( password is "_password_" )
``````json
{"address":"hx65f6e18d378b57612a28f72acb97021eaa82aa5a","id":"2f19df35-9a11-4b24-a83d-11c8d5e903db","coinType":"icx","version":3,"crypto":{"cipher":"aes-128-ctr","ciphertext":"469900238420d66b02dbbc1d6e978ef0e1f46321e8767cbc9f59bd93499166d4","cipherparams":{"iv":"432a04c7317d83e663e67f605befb326"},"kdf":"scrypt","kdfparams":{"dklen":32,"n":4096,"p":6,"r":8,"salt":"66fad93a131f21c18c8c8bf08ca56641d984eaa20855bcfeac78dcb5264ce3fb"},"mac":"036ab5c07ec0060bf558010108c78c5427e4223047fd2cca3ae523c8e4d9e25e"}}
``````
