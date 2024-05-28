import sys
import signal
import argparse
import xml.etree.ElementTree as et
import csv
import re

def KeyboardInterruptHandler(sig, frame):
	print("Script interrupted by user.")
	sys.exit(0)

signal.signal(signal.SIGINT, KeyboardInterruptHandler)

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
        description = 
        "Take a Modbus map file from Connected Components Workbench and " +
        "translate it to a Kepware tag CSV file.\r\n" + 
        "See https://github.com/Dureddo for details.")
parser.add_argument("-m", "--mapfile", required=True,
	help="Modbus mapping file from Connected Components Workbench")
parser.add_argument("-o", "--outfile", required=True,
	help="Kepware tag CSV file")
parser.add_argument("-p", "--prefix", default='',
	help="Tag prefix")
parser.add_argument("-r", "--readonly", action="store_true",
	help="Default all tags to read-only (read-write if not specified)")
parser.add_argument("-s", "--scanrate", type=int,default=100,
	help="Specify scan rate in ms (100 ms by default)")
parser.add_argument("--noprog", action="store_true",
        help="Remove the '@<program>' suffix from variable names")
parser.add_argument("-v", "--verbose", action="store_true",
        help="Verbose output")
args = parser.parse_args()

try:
    tree = et.parse(args.mapfile).getroot()
    assert(tree.tag == "modbusServer")
except IOError as e:
    print("ERROR - Unable to open file: {}".format(args.mapfile))
    sys.exit(0)
except (AssertionError, et.ParseError) as e:
    print("ERROR - Malformed XML file")
    sys.exit(0)

fileHeader = ["Name",
              "Address",
              "Data Type",
              "Sub Elem Type",
              "Data Type Size",
              "Data Final Type"
             ]

typeInt = {"_IO_EM_DI_00":"capt_bas_moulin",
           "_IO_EM_DI_03":"sign_ext_son",
           "_IO_EM_DI_04":"capt_rot_blute",
           "_IO_EM_DI_05":"inter_shunt_secu",
           "_IO_EM_DI_06":"capt_ensach",
           "_IO_EM_DI_07":"run_powerflex",
           "_IO_EM_DO_00":"moteur_succion",
           "_IO_EM_DO_01":"moteur_son",
           "_IO_EM_DO_02":"battage",
           "_IO_EM_DO_03":"out_sign_son",
           "_IO_EM_DO_05":"moteur_bluterie"
          }

try:
    with open(args.outfile, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(fileHeader)
        for child in tree:
            if(child.tag == "modbusRegister"):
                for addr in child:
                    if(addr.tag == "mapping"):
                        name = addr.attrib["variable"]
                        if name.startswith("_"):
                            name = typeInt[addr.attrib["variable"]]
                        name = name.lower()
                        name = (re.sub((r"@\S+"), "", name))
                        print (name)
                        if args.noprog:
                            name = name.split('@')[0]
                        address = addr.attrib["address"]
                        print (address)
                        dataType = addr.attrib["dataType"]
                        print (dataType)
                        for addr2 in addr:
                            if(addr2.tag == "MBVarInfo"):
                                subElementType = addr2.attrib["SubElemType"]
                                print (subElementType)
                                dataTypeSize = addr2.attrib["DataTypeSize"]
                                print (dataTypeSize)
                                if (dataType) == "Bool" or (subElementType) == "Bool":
                                    dataFinalType = "Bool"
                                elif (dataType) == "Real" or (subElementType) == "Real":
                                    dataFinalType = "Float"
                                elif (dataType) == "Int" or (subElementType) == "Int":
                                    dataFinalType = "Int"
                                elif (dataType) == "Dint" or (subElementType) == "Dint":
                                    dataFinalType = "DInt"
                                else:
                                    dataFinalType = "Non Défini"
                                print (dataFinalType)
                                print ("-----")
                                csvRow = [name,
                                          address,
                                          dataType,
                                          subElementType,
                                          dataTypeSize,
                                          dataFinalType
                                          ]
                                writer.writerow(csvRow)

except IOError as e:
    print("Unable to write to file: {}".format(args.outfile))
    