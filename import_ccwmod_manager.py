import sys
import signal
import argparse
import xml.etree.ElementTree as et
import csv
import re
import configparser

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Lecture du Fichier de Configuration avec toutes les Variables
config.read('config.ini')


class ImportCCWManager:
  def __init__(self):
    self.fileHeader = ["Name",
                       "Address",
                       "Data Type",
                       "Sub Elem Type",
                       "Data Type Size",
                       "Data Final Type"
                       ]
    self.typeInt = {"_IO_EM_DI_00":"capt_bas_moulin",
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
    
  def return_list_address_modbus(self):
    try:
      tree = et.parse(config['Modbus']['FileCCWMOD']).getroot()
      assert(tree.tag == "modbusServer")
    except (AssertionError, et.ParseError) as e:
      print("ERROR - Malformed XML file")
      sys.exit(0)
    list = []
    for child in tree:
      if(child.tag == "modbusRegister"):
        for addr in child:
          if(addr.tag == "mapping"):
            name = addr.attrib["variable"]
            if name.startswith("_"):
              name = self.typeInt[addr.attrib["variable"]]
            name = name.lower()
            name = (re.sub((r"@\S+"), "", name))
            # print (name)
            address = addr.attrib["address"]
            # print (address)
            dataType = addr.attrib["dataType"]
            # print (dataType)
            for addr2 in addr:
              if(addr2.tag == "MBVarInfo"):
                subElementType = addr2.attrib["SubElemType"]
                # print (subElementType)
                dataTypeSize = addr2.attrib["DataTypeSize"]
                # print (dataTypeSize)
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
                # print (dataFinalType)
                dict = {"name": name, "address": address, "dataTypeSize": dataTypeSize, "dataFinalType": dataFinalType}
                # print (dict)
                list.append(dict)
                # print ("-----")
    # print (list)
    return (list)