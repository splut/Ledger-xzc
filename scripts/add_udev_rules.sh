#!/bin/bash
echo "SUBSYSTEMS==\"usb\", ATTRS{idVendor}==\"2c97\", ATTRS{idProduct}==\"0000\", MODE=\"0660\", TAG+=\"uaccess\", TAG+=\"udev-acl\", GROUP=\"plugdev\", OWNER=\"USER\"" >>/etc/udev/rules.d/20-hw1.rules
echo "SUBSYSTEMS==\"usb\", ATTRS{idVendor}==\"2c97\", ATTRS{idProduct}==\"0001\", MODE=\"0660\", TAG+=\"uaccess\", TAG+=\"udev-acl\", GROUP=\"plugdev\", OWNER=\"USER\"" >>/etc/udev/rules.d/20-hw1.rules
udevadm trigger
udevadm control --reload-rules