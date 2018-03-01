
## Installation pre-requisites

### clone this repo to $HOME:
    cd ~
    git clone https://github.com/zcoinofficial/Ledger-xzc
    cd Ledger-xzc

### install ledgerblue (Note this is a modified version from current pip version)
    cd blue-loader-python
    sudo python setup.py install

### (Linux only) Add udev rules:
    sed -i "s/USER/$USER/g" scripts/add_udev_rules.sh
    sudo bash scripts/add_udev_rules.sh

## Install

### OPTIONAL - Building App from Source (Linux Only - Skip to 'Binary' section for direct install)

 #### dependancies:
   sudo apt-get update
     sudo apt-get install libc6-dev-i386 libudev-dev libusb-1.0-0-dev python-dev

  #### link the environment variable BOLOS_ENV to current directory:
    export BOLOS_ENV=~/Ledger-xzc

  #### download a prebuild gcc from [here](https://launchpad.net/gcc-arm-embedded/+milestone/5-2016-q1-update) and unpack it:
    wget https://launchpad.net/gcc-arm-embedded/5.0/5-2016-q1-update/+download/gcc-arm-none-eabi-5_3-2016q1-20160330-linux.tar.bz2
    tar -xvjf gcc-arm-none-eabi-5_3-2016q1-20160330-mac.tar.bz2
    rm -rf gcc-arm-none-eabi-5_3-2016q1-20160330-linux.tar.bz2

  #### Download a prebuild clang from [here](http://releases.llvm.org/download.html#4.0.0), unpack it and rename to 'clang-arm-fropi' (Ubuntu 16.04 in below command):
    wget http://releases.llvm.org/4.0.0/clang+llvm-4.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz
    tar xf clang+llvm-4.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz
    rm -rf clang+llvm-4.0.0-x86_64-linux-gnu-ubuntu-16.04.tar.xz
    mv clang+llvm-4.0.0-x86_64-linux-gnu-ubuntu-16.04 clang-arm-fropi

   #### Download the Nano S SDK and link the environment variable BOLOS_SDK to it:
    git clone https://github.com/ledgerhq/nanos-secure-sdk
    export BOLOS_SDK=~/Ledger-xzc/nanos-secure-sdk

 #### Make Zcoin application:
    sudo COIN=zcoin BOLOS_SDK=~/Ledger-xzc/nanos-secure-sdk BOLOS_ENV=~/Ledger-xzc/ make -B

### Binary

#### Application Verification (Optional but recommended)
 Firstly verify that entries in 'verification' folder match what's on https://zcoin.io/get-zcoin/
##### verify application hash:
    python -m ledgerblue.hashApp --hex bin/app.hex

##### verify application signature:
    python -m ledgerblue.verifyApp --hex bin/app.hex --key verification/key.txt --signature verification/sig.txt

#### Plug in your Ledger and unlock.

#### Add zcoin developer public key to your device:
    python -m ledgerblue.setupCustomCA --targetId 0x31100002 --public verification/key.txt --name Zcoin-dev
On device,  ensure 'Name' is equal to 'Zcoin-dev' and 'Public Key' is 0435...A99D.

#### Load Zcoin app onto your device:
    python -m ledgerblue.loadApp --appFlags 0x50 --curve secp256k1 --targetId 0x31100002 --fileName bin/app.hex --appName "Zcoin" `ICONHEX=\`python ~/Ledger-xzc/nanos-secure-sdk/icon.py nanos_app_zcoin.gif hexbitmaponly 2>/dev/null\` ; [ ! -z "$ICONHEX" ] && echo "--icon $ICONHEX"`   --path "" --signature verification/sig.txt

### Usage

Tested working with Electrum-xzc: follow instructions at https://github.com/zcoinofficial/electrum-xzc/.

### Troubleshooting

Get into the Zcoin Discord dev channel [here](https://discordapp.com/channels/358305508849090560/368817851143815178).
