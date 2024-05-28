import logging.handlers
from pyModbusTCP.client import ModbusClient
from datetime import date, datetime
import time
import pytz
import os
import logging
import boto3
import shutil
import configparser
from influxdb_manager import InfluxDBManager
from mysql_manager import MySQLManager
from import_ccwmod_manager import ImportCCWManager
#Push
## Fontion qui Permet la Conversion de Valeur en 32 Bits en Réel
def convert_32bits_reel(value_32bits):
  # Initialisation des Variables
  exposant = 0
  mantisse = 1.0
  # Conversion Booléen en Entier et Inversion des Valeurs
  value_32bits = [int(b) for b in value_32bits]
  value_32bits.reverse()
  # Calcul de l'Exposant
  for i in range(1,9):
    index = 8 - i
    exposant = (int(value_32bits[i]) * (2**index)) + exposant
  exposant = 2**(exposant - 127)
  # Calcul de la Mantisse
  for i in range(9,32):
    index = i - 8
    mantisse = (int(value_32bits[i]) * (1/(2**index))) + mantisse
  # Calcul du Réel avec Inversion du Signe si le Premier Bit est à 1
  value = mantisse * exposant * (1 - (2*value_32bits[0]))
  # Arrondie du Réel et Conversion en String
  value = round(value,2)
  return value

## Fontion qui Permet la Conversion de Valeurs en Bits Quelque Soit la Longueur en Réel
def convert_bits_int(value_bits):
  # Initialisation des Variables
  value = 0
  # Inversion des Valeurs et Test du Signe
  value_bits.reverse()
  if value_bits[0] == True:
    [not elem for elem in value_bits]
  # Conversion Booléen en Entier
  value_bits = [int(b) for b in value_bits]
  # Conversion en Entier
  for i in range(1,len(value_bits)):
    index = len(value_bits) - i - 1
    value = (int(value_bits[i]) * (2**index)) + value
  # Complément à 1 si de Signe
  if value_bits[0] == True:
    value = (-1 * (value + 1))
  return value

list_Unit = {"courrant_meule": "A",
             "current_meule": "A",
             "t_meule": "°C",
             "reg_intens_meule": "A",
             "speed_ref_vibrat": "Hz",
             "cv_manuel": "Hz"
             }

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Lecture du Fichier de Configuration avec toutes les Variables
config.read('config.ini')

test = config['AWS']['bucket']

print(test)
print(type(test))

# Création d'un Objet de la Classe InfluxDBManager
infdb_manager = InfluxDBManager()

# Création d'un Objet de la Classe MySQLManager
mysql_manager = MySQLManager()

# Création d'un Objet de la Classe ImportCCWManager
import_ccw_manager = ImportCCWManager()

# Récupération des Variables, des Adresses Modbus et de leur Type
list_address_modbus = import_ccw_manager.return_list_address_modbus()
print(list_address_modbus)

# Accès à l'Automate par ModBus TCP
c = ModbusClient(host=config['Modbus']['IP'], port=int(config['Modbus']['Port']), unit_id=1, auto_open=True)

# Lecture de Tous les Registres
regs = c.read_coils(1, 205)
if regs:
  print ("Lecture des Registres Correct\n")
else:
  print ("Erreur de Lecture")



try:
  while True:
    # Informations de la Date et l'Heure à Utiliser pour MySQL et les Logs
    paris = pytz.timezone('Europe/Paris')
    current_dl = datetime.now(paris)
    current_dl = current_dl.strftime('%d-%m-%Y %H:%M:%S')
    print ("Premier Current Date Log" + current_dl)

    # Récupération et Affichage de la Date en Cours
    today = date.today()
    print (today)
    current_date_time = datetime.now(paris)
    # Récupération et Affichage de l'Heure en Cours
    current_time = current_date_time.strftime('%H:%M:%S')
    print (current_time)

    # Création d'un Fichier de Logs
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename=current_dl, encoding='utf-8', level=logging.DEBUG)
    myhandler = logging.FileHandler(current_dl)
    myhandler.setLevel(logging.INFO)
    logger.addHandler(myhandler)
    #logger.debug('Log : %s', current_dl)
    # logger.debug('Message Debug')
    # logger.info('Message Information')
    # logger.warning('Message Warning')
    # logger.error('Message Erreur')

    # On Push les Premières Informations qui Sont la Date et l'Heure dans MySQL
    mysql_manager.push_first_value_sql()

    # On Récupère tous les Eléments de l'Automate et on Convertit les Valeurs pour les Transférer dans MySQL et InfluxDB
    for elem in list_address_modbus:
      print (elem)
      name = elem.get("name")
      print (name)
      address = int(elem.get("address")) - 1
      print (address)
      dataTypeSize = int(elem.get("dataTypeSize"))
      print (dataTypeSize)
      dataFinalType = elem.get("dataFinalType")
      print (dataFinalType)
      if (dataFinalType) != "Bool":
        dataTypeSize *= 8
      print (dataTypeSize)
      valeur = c.read_coils(address, dataTypeSize)
      print(valeur)
      if (dataFinalType) == "Bool" and (dataTypeSize) == 5:
        valeur = int(valeur[4])
      elif (dataFinalType) == "Bool":
        valeur = int(valeur[0])
      elif (dataFinalType) == "Float":
        print(valeur)
        valeur = convert_32bits_reel(valeur)
        infdb_manager.send_InfluxDB(name,valeur)
      elif (dataFinalType) == "DInt" or (dataFinalType) == "Int":
        valeur = convert_bits_int(valeur)
        infdb_manager.send_InfluxDB(name,valeur)
      mysql_manager.push_value_sql(name,valeur)
      # On Rajoute les Unités pour 6 Métriques
      x = list(list_Unit.keys())
      if (x.count(name) == 1):
        unit = list_Unit.get(name)
      else: unit =""
      print ("Etat ou Valeur " + name + " : " + str(valeur) + " " + unit)
      logger.info('%s - %s : %s %s', current_dl, name, valeur, unit)
    logger.warning("-------------------------------------------------------")
    logger.warning("Fin du Fichier de Logs du %s ", current_dl)
    name_file = current_dl + "-" + "ml.log"
    shutil.copyfile(current_dl,name_file)

    # Fermeture du Fichier de Logs
    handlers = logger.handlers[:]
    for handler in handlers:
      logger.removeHandler(handler)
      handler.close()

    # Copie du Fichier de Logs dans un Bucket S3
    s3 = boto3.resource('s3')
    with open(name_file, 'rb') as data:
      s3.Bucket(config['AWS']['bucket']).put_object(Key=name_file, Body=data)
    logging.shutdown()

except KeyboardInterrupt:
  print ("Boucle Arrêté")

finally:
  mysql_manager.close_connection_sql()
