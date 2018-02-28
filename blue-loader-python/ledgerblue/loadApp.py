"""
*******************************************************************************
*   Ledger Blue
*   (c) 2016 Ledger
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      http://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License.
********************************************************************************
"""

DEFAULT_ALIGNMENT = 1024

import argparse

def get_argparser():
	parser = argparse.ArgumentParser(description="Load an app onto the device from a hex file.")
	parser.add_argument("--targetId", help="The device's target ID (default is Ledger Blue)", type=auto_int)
	parser.add_argument("--fileName", help="The application hex file to be loaded onto the device")
	parser.add_argument("--icon", help="The icon content to use (hex encoded)")
	parser.add_argument("--curve", help="""A curve on which BIP 32 derivation is locked ("secp256k1", "prime256r1", or
"ed25519"), can be repeated""", action='append')
	parser.add_argument("--path", help="""A BIP 32 path to which derivation is locked (format decimal a'/b'/c), can be
repeated""", action='append')
	parser.add_argument("--appName", help="The name to give the application after loading it")
	parser.add_argument("--signature", help="A signature of the application (hex encoded)")
	parser.add_argument("--appFlags", help="The application flags", type=auto_int)
	parser.add_argument("--bootAddr", help="The application's boot address", type=auto_int)
	parser.add_argument("--rootPrivateKey", help="""The Signer private key used to establish a Secure Channel (otherwise
a random one will be generated)""")
	parser.add_argument("--apdu", help="Display APDU log", action='store_true')
	parser.add_argument("--deployLegacy", help="Use legacy deployment API", action='store_true')
	parser.add_argument("--apilevel", help="Use given API level when interacting with the device", type=auto_int)
	parser.add_argument("--delete", help="Delete the app with the same name before loading the provided one", action='store_true')
	parser.add_argument("--params", help="Store icon and install parameters in a parameter section before the code", action='store_true')
	parser.add_argument("--appVersion", help="The application version (as a string)")
	return parser

def auto_int(x):
	return int(x, 0)

def parse_bip32_path(path, apilevel):
		if len(path) == 0:
				return b""
		result = b""
		elements = path.split('/')
		if apilevel >= 5:
			result = result + chr(len(elements))
		for pathElement in elements:
				element = pathElement.split('\'')
				if len(element) == 1:
						result = result + struct.pack(">I", int(element[0]))
				else:
						result = result + struct.pack(">I", 0x80000000 | int(element[0]))
		return result

if __name__ == '__main__':
	from .ecWrapper import PrivateKey
	from .comm import getDongle
	from .hexParser import IntelHexParser, IntelHexPrinter
	from .hexLoader import HexLoader
	from .deployed import getDeployedSecretV1, getDeployedSecretV2
	import struct
	import binascii
	import sys

	args = get_argparser().parse_args()

	if args.apilevel == None:
		args.apilevel = 5
	if args.targetId == None:
		args.targetId = 0x31000002
	if args.fileName == None:
		raise Exception("Missing fileName")
	if args.appName == None:
		raise Exception("Missing appName")
	if args.appFlags == None:
		args.appFlags = 0
	if args.rootPrivateKey == None:
		privateKey = PrivateKey()
		publicKey = binascii.hexlify(privateKey.pubkey.serialize(compressed=False))
		print("Generated random root public key : %s" % publicKey)
		args.rootPrivateKey = privateKey.serialize()


	if (sys.version_info.major == 3):
		args.appName = bytes(args.appName,'ascii')
	if (sys.version_info.major == 2):
		args.appName = bytes(args.appName)

	parser = IntelHexParser(args.fileName)
	if args.bootAddr == None:
		args.bootAddr = parser.getBootAddr()

	path = b""
	curveMask = 0xff
	if args.curve != None:
		curveMask = 0x00
		for curve in args.curve:
			if curve == 'secp256k1':
				curveMask |= 0x01
			elif curve == 'prime256r1':
				curveMask |= 0x02
			elif curve == 'ed25519':
				curveMask |= 0x04
			else:
				raise Exception("Unknown curve " + curve)

	if args.apilevel >= 5:
		path += struct.pack('>B',curveMask)
		if args.path != None:
			for item in args.path:
				if len(item) != 0:
					path += parse_bip32_path(item, args.apilevel)
	else:
		if args.curve != None:
			print("Curve not supported using this API level, ignoring")
		if args.path != None:
			if len(args.path) > 1:
				print("Multiple path levels not supported using this API level, ignoring")
			else:
				path = parse_bip32_path(args.path[0], args.apilevel)

	icon = None
	if not args.icon is None:
		icon = bytearray.fromhex(args.icon)

	signature = None
	if not args.signature is None:
		signature = bytearray.fromhex(args.signature)

	#prepend app's data with the icon content (could also add other various install parameters)
	printer = IntelHexPrinter(parser)
	#todo build a TLV zone to keep install params
	#todo dney nvm_write in that section ?
	paramsSectionContent = []
	if icon:
		paramsSectionContent = icon

	# prepend the param section (arbitrary)
	if (args.params):
		#take care of aligning the parameters sections to avoid possible invalid dereference of aligned words in the program nvram.
		#also use the default MPU alignment
		param_start = printer.minAddr()-len(paramsSectionContent)-(DEFAULT_ALIGNMENT-(len(paramsSectionContent)%DEFAULT_ALIGNMENT))
		printer.addArea(param_start, paramsSectionContent)

	# account for added regions (install parameters, icon ...)
	appLength = printer.maxAddr() - printer.minAddr()


	dongle = getDongle(args.apdu)

	if args.deployLegacy:
		secret = getDeployedSecretV1(dongle, bytearray.fromhex(args.rootPrivateKey), args.targetId)
	else:
		secret = getDeployedSecretV2(dongle, bytearray.fromhex(args.rootPrivateKey), args.targetId)
	loader = HexLoader(dongle, 0xe0, True, secret)

	if (not (args.appFlags & 2)) and args.delete:
			loader.deleteApp(args.appName)

	#heuristic to guess how to pass the icon
	if (args.params):
		loader.createApp(args.appFlags, appLength, args.appName, None, path, 0, len(paramsSectionContent), args.appVersion)
	else:
		loader.createApp(args.appFlags, appLength, args.appName, icon, path, None, None, args.appVersion)

	hash = loader.load(0x0, 0xF0, printer)
	print("Application hash : " + hash)
	loader.run(printer, args.bootAddr, signature)
