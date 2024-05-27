from pyModbusTCP.client import ModbusClient
from datetime import date, datetime
import time
import mysql.connector
import pytz
import os
import logging
import boto3
import shutil
import configparser
from influxdb_manager import InfluxDBManager
from mysql_manager import MySQLManager

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Lecture du Fichier de Configuration avec toutes les Variables
config.read('config.ini')

# Création d'un Objet de la Classe InfluxDBManager
infdb_manager = InfluxDBManager()
# Création d'un Objet de la Classe MySQLManager
mysql_manager = MySQLManager()

paris = pytz.timezone('Europe/Paris')
current_date_log = datetime.now(paris)
current_date_log = current_date_log.strftime('%d-%m-%Y %H:%M:%S')
print (current_date_log)

logger = logging.getLogger(__name__)

logging.basicConfig(filename='MoulinLauzes.log', encoding='utf-8', level=logging.DEBUG)

logger.debug('Log : %s', current_date_log)
# logger.debug('Message Debug')
# logger.info('Message Information')
# logger.warning('Message Warning')
# logger.error('Message Erreur')

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

# Accès à l'Automate par ModBus TCP
c = ModbusClient(host=config['Modbus']['IP'], port=int(config['Modbus']['Port']), unit_id=1, auto_open=True)
# Lecture de Tous les Registres
regs = c.read_coils(1, 205)
if regs:
  print ("Lecture des Registres Correct\n")
  logger.info('Accès au Registre Correct')
  # print ("Type des Variables : ",type(regs),"\n")
else:
  print ("Erreur de Lecture")
  logger.error('Erreur de Lecture des Registres')

try:
  while True:
    today = date.today()
    print (today)
    current_date_time = datetime.now(paris)
    current_time = current_date_time.strftime('%H:%M:%S')
    print (current_time)
    current_date_log = datetime.now(paris)
    current_date_log = current_date_log.strftime('%d-%m-%Y %H:%M:%S')
    print (current_date_log)
    # Registre en Liste de Booléen de 1 sauf Mention

    """
    cur.execute("LOCK TABLES valeurs WRITE")
    """

    # max_1_id = mysql_manager.return_id_sql("max+1")
    # max_id = mysql_manager.return_id_sql("max")

    # On Push les Premières Informations qui Sont la Date et l'Heure 
    mysql_manager.push_first_value_sql()

    

"""
    capt_bas_moulin = c.read_coils(0, 1)
    capt_bas_moulin = capt_bas_moulin[0]
    mysql_manager.push_value_sql("capt_bas_moulin",capt_bas_moulin)

    sign_ext_son = c.read_coils(1, 1)
    sign_ext_son = sign_ext_son[0]
    mysql_manager.push_value_sql("sign_ext_son",sign_ext_son)

    capt_rot_blute = c.read_coils(2, 1)
    capt_rot_blute = capt_rot_blute[0]
    mysql_manager.push_value_sql("capt_rot_blute",capt_rot_blute)

    inter_shunt_secu = c.read_coils(3, 1)
    inter_shunt_secu = inter_shunt_secu[0]
    mysql_manager.push_value_sql("inter_shunt_secu",inter_shunt_secu)

    capt_ensach = c.read_coils(4, 1)
    capt_ensach = capt_ensach[0]
    mysql_manager.push_value_sql("capt_ensach",capt_ensach)

    run_powerflex = c.read_coils(5, 1)
    run_powerflex = run_powerflex[0]
    mysql_manager.push_value_sql("run_powerflex",run_powerflex)

    moteur_succion = c.read_coils(6, 1)
    moteur_succion = moteur_succion[0]
    mysql_manager.push_value_sql("moteur_succion",moteur_succion)
    
    moteur_son = c.read_coils(7, 1)
    moteur_son = moteur_son[0]
    mysql_manager.push_value_sql("moteur_son",moteur_son)

    battage = c.read_coils(8, 1)
    battage = battage[0]
    mysql_manager.push_value_sql("battage",battage)

    out_sign_son = c.read_coils(9, 1)
    out_sign_son = out_sign_son[0]
    mysql_manager.push_value_sql("out_sign_son",out_sign_son)

    moteur_bluterie = c.read_coils(10, 1)
    moteur_bluterie = moteur_bluterie[0]
    mysql_manager.push_value_sql("moteur_bluterie",moteur_bluterie)

    # Courant Meule Mesurée en Réel sur 32 Bits
    courant_meule_mesuree = c.read_coils(11, 32)
    courant_meule_mesuree = convert_32bits_reel(courant_meule_mesuree)
    mysql_manager.push_value_sql("courant_meule_mesuree",courant_meule_mesuree)
    infdb_manager.send_InfluxDB("courant_meule_mesuree",courant_meule_mesuree)

    stop_powerflex_true = c.read_coils(43, 1)
    stop_powerflex_true = stop_powerflex_true[0]
    mysql_manager.push_value_sql("stop_powerflex_true",stop_powerflex_true)

    # Stop PowerFlex en Booléen sur 5 Bits
    stop_powerflex = c.read_coils(44, 5)
    stop_powerflex_4 = int(stop_powerflex[4])
    mysql_manager.push_value_sql("stop_powerflex_4",stop_powerflex_4)

    start_powerflex = c.read_coils(49, 1)
    start_powerflex = int(start_powerflex[0])
    mysql_manager.push_value_sql("start_powerflex",start_powerflex)

    # Start Bluterie en Booléen sur 2 Bits
    start_bluterie = c.read_coils(50, 2)
    start_bluterie_0 = int(start_bluterie[0])
    mysql_manager.push_value_sql("start_bluterie_0",start_bluterie_0)
  
    # Current Meule Mesurée en Réel sur 32 Bits
    current_meule_mesuree = c.read_coils(52, 32)
    current_meule_mesuree = convert_32bits_reel(current_meule_mesuree)
    mysql_manager.push_value_sql("current_meule_mesuree",current_meule_mesuree)
 
    # Température Meule en INT sur 16 Bits
    temperature_meule = c.read_coils(84, 16)
    temperature_meule = convert_bits_int(temperature_meule)
    mysql_manager.push_value_sql("temperature_meule",temperature_meule)
    infdb_manager.send_InfluxDB("temperature_meule", temperature_meule)

    capt_rot_bluterie_0 = c.read_coils(100, 1)
    capt_rot_bluterie_0 = int(capt_rot_bluterie_0[0])
    mysql_manager.push_value_sql("capt_rot_bluterie_0",capt_rot_bluterie_0)

    alarm_entretien = c.read_coils(101, 1)
    alarm_entretien = int(alarm_entretien[0])
    mysql_manager.push_value_sql("alarm_entretien",alarm_entretien)

    # Horamètre en DINT sur 32 Bits
    horametre = c.read_coils(102, 32)
    horametre = convert_bits_int(horametre)
    mysql_manager.push_value_sql("horametre",horametre)

    # Retour Fréquence Meule en Réel sur 32 Bits
    retour_frequence_meule = c.read_coils(134, 32)
    retour_frequence_meule = convert_32bits_reel(retour_frequence_meule)
    mysql_manager.push_value_sql("retour_frequence_meule",retour_frequence_meule)
    infdb_manager.send_InfluxDB("retour_frequence_meule", retour_frequence_meule)

    stop_powerflex_vibrat = c.read_coils(166, 1)
    stop_powerflex_vibrat = int(stop_powerflex_vibrat[0])
    mysql_manager.push_value_sql("stop_powerflex_vibrat",stop_powerflex_vibrat)    

    # Réglage Intensité Meule en Réel sur 32 Bits
    reglage_intensite_meule = c.read_coils(167, 32)
    reglage_intensite_meule = convert_32bits_reel(reglage_intensite_meule)
    mysql_manager.push_value_sql("reglage_intensite_meule",reglage_intensite_meule)
    infdb_manager.send_InfluxDB("reglage_intensite_meule", reglage_intensite_meule)

    capt_ensach_alarme = c.read_coils(199, 1)
    capt_ensach_alarme = int(capt_ensach_alarme[0])
    mysql_manager.push_value_sql("capt_ensach_alarme",capt_ensach_alarme)

    capt_bas_alarme = c.read_coils(200, 1)
    capt_bas_alarme = int(capt_bas_alarme[0])
    mysql_manager.push_value_sql("capt_bas_alarme",capt_bas_alarme)

    intensite_meule = c.read_coils(201, 1)
    intensite_meule = int(intensite_meule[0])
    mysql_manager.push_value_sql("intensite_meule",intensite_meule)
   
    arret_vibra = c.read_coils(202, 1)
    arret_vibra = int(arret_vibra[0])
    mysql_manager.push_value_sql("arret_vibra",arret_vibra)

    succion_force = c.read_coils(203, 1)
    succion_force = int(succion_force[0])
    mysql_manager.push_value_sql("succion_force",succion_force)

    vibra_eleve = c.read_coils(204, 1)
    vibra_eleve = int(vibra_eleve[0])
    mysql_manager.push_value_sql("vibra_eleve",vibra_eleve)

    vidan_trem = c.read_coils(205, 1)
    vidan_trem = int(vidan_trem[0])
    mysql_manager.push_value_sql("vidan_trem",vidan_trem)

    # Vitesse Vibrateur en Réel sur 32 Bits
    speed_ref_vibrat = c.read_coils(206, 32)
    speed_ref_vibrat = convert_32bits_reel(speed_ref_vibrat)
    mysql_manager.push_value_sql("speed_ref_vibrat",speed_ref_vibrat)
    infdb_manager.send_InfluxDB("speed_ref_vibrat", speed_ref_vibrat)

    start_powerflex_vibrat = c.read_coils(238, 1)
    start_powerflex_vibrat = int(start_powerflex_vibrat[0])
    mysql_manager.push_value_sql("start_powerflex_vibrat",start_powerflex_vibrat)

    # Consigne Vibrateur en Réel sur 32 Bits
    cv_manuel = c.read_coils(239, 32)
    cv_manuel = convert_32bits_reel(cv_manuel)
    mysql_manager.push_value_sql("cv_manuel",cv_manuel)
    infdb_manager.send_InfluxDB("cv_manuel", cv_manuel)
"""

#    cur.execute("UNLOCK TABLES")

    # Affichage et Logs
    print ("Etat Capteur Bas Moulin : ",capt_bas_moulin)
    logger.warning('%s - Capteur Moulin : %s', current_date_log, capt_bas_moulin)
    print ("Sign Ext Son : ",sign_ext_son)
    logger.info('%s - Sign Ext Son : %s', current_date_log, sign_ext_son)
    print ("Capteur Rotation Bluterie : ",capt_rot_blute)
    logger.info('%s - Capteur Rotation Bluterie : %s', current_date_log, capt_rot_blute)
    print ("Etat Capteur Interrupteur Shunt Sécurité : ",inter_shunt_secu)
    logger.info('%s - Etat Capteur Interrupteur Shunt Sécurité : %s', current_date_log, inter_shunt_secu)
    print ("Etat Capteur Ensachage : ",capt_ensach)
    logger.warning('%s - Etat Capteur Ensachage : %s', current_date_log, capt_ensach)
    print ("Etat Run PowerFlex : ",run_powerflex)
    logger.info('%s - Etat Run PowerFlex : %s', current_date_log, run_powerflex)
    print ("Etat Moteur Succion : ",moteur_succion)
    print ("Etat Moteur Son : ",moteur_son)
    logger.info('%s - Etat Moteur Son : %s', current_date_log, moteur_son)
    print ("Etat Moteur Battage : ",battage)
    logger.info('%s - Etat Moteur Battage : %s', current_date_log, battage)
    print ("Etat Out Son : ",out_sign_son)
    logger.info('%s - Etat Out Son : %s', current_date_log, out_sign_son)
    print ("Etat Moteur Bluterie : ",moteur_bluterie)
    logger.info('%s - Etat Moteur Bluterie : %s', current_date_log, moteur_bluterie)
    print ("Courant Meule Mesurée : " + str(courant_meule_mesuree) + " A")
    logger.info('%s - Courant Meule Mesurée : %s', current_date_log, courant_meule_mesuree)
    print ("Stop PowerFlex True : ",stop_powerflex_true)
    logger.info('%s - Stop PowerFlex True : %s', current_date_log, stop_powerflex_true)
    print ("Stop PowerFlex : ",stop_powerflex)
    logger.info('%s - Stop PowerFlex : %s', current_date_log, stop_powerflex)
    print ("Stop PowerFlex 4 : ",stop_powerflex_4)
    logger.info('%s - Stop PowerFlex 4 : %s', current_date_log, stop_powerflex_4)
    print ("Start PowerFlex : ",start_powerflex)
    logger.info('%s - Start PowerFlex : %s', current_date_log, start_powerflex)
    print ("Start Bluterie : ",start_bluterie)
    logger.info('%s - Start Bluterie : %s', current_date_log, start_bluterie)
    print ("Start Bluterie 0 : ",start_bluterie_0)
    logger.info('%s - Start Bluterie 0 : %s', current_date_log, start_bluterie_0)
    print ("Current Meule Mesurée : " + str(current_meule_mesuree) + " A")
    logger.info('%s - Current Meule Mesurée : %s', current_date_log, current_meule_mesuree)
    print ("Température Meule : " + str(temperature_meule) + " °C")
    logger.info('%s - Température Meule : %s', current_date_log, temperature_meule)
    print ("Etat Capteur Rotation Bluterie : ",capt_rot_bluterie_0)
    logger.info('%s - Etat Capteur Rotation Bluterie : %s', current_date_log, capt_rot_bluterie_0)
    print ("Etat Alarme Entretien : ",alarm_entretien)
    logger.warning('%s - Etat Alarme Entretien : %s', current_date_log, alarm_entretien)
    print ("Horamètre : " + str(horametre) + " h")
    logger.info('%s - Horamètre : %s', current_date_log, horametre)
    print ("Retour Fréquence Meule : " + str(retour_frequence_meule) + " Hz")
    logger.info('%s - Retour Fréquence Meule : %s', current_date_log, retour_frequence_meule)
    print ("Stop PowerFlex Vibrateur : ",stop_powerflex_vibrat)
    logger.info('%s - Stop PowerFlex Vibrateur : %s', current_date_log, stop_powerflex_vibrat)
    print ("Réglage Intensité Meule : " + str(reglage_intensite_meule) + " A")
    logger.info('%s - Réglage Intensité Meule : %s', current_date_log, reglage_intensite_meule)
    print ("Etat Capteur Ensachage : ",capt_ensach_alarme)
    logger.info('%s - Etat Capteur Ensachage : %s', current_date_log, capt_ensach_alarme)
    print ("Etat Capteur Bas Alarme : ",capt_bas_alarme)
    logger.info('%s - Etat Capteur Bas Alarme : %s', current_date_log, capt_bas_alarme)
    print ("Etat Intensité Meule : ",intensite_meule)
    logger.info('%s - Etat Intensité Meule : %s', current_date_log, intensite_meule)
    print ("Arrêt Vibrateur : ",arret_vibra)
    logger.info('%s - Arrêt Vibrateur : %s', current_date_log, arret_vibra)
    print ("Etat Succion Forcé : ",succion_force)
    logger.info('%s - Etat Succion Forcé : %s', current_date_log, succion_force)
    print ("Etat Vibration Elevé : ",vibra_eleve)
    logger.error('%s - Etat Vibration Elevé : %s', current_date_log, vibra_eleve)
    print ("Etat Vidange Trémis : ",vidan_trem)
    logger.info('%s - Etat Vidange Trémis : %s', current_date_log, vidan_trem)
    print ("Vitesse Vibrateur : " + str(speed_ref_vibrat) + " Hz")
    logger.info('%s - Vitesse Vibrateur : %s', current_date_log, speed_ref_vibrat)
    print ("Start PowerFlex Vibrateur : ",start_powerflex_vibrat)
    logger.info('%s - Start PowerFlex Vibrateur : %s', current_date_log, start_powerflex_vibrat)
    print ("Consigne Vibrateur : " + str(cv_manuel) + " Hz")
    logger.info('%s - Consigne Vibrateur : %s', current_date_log, cv_manuel)
    print ("------------------------------------------------------")
    time.sleep(1)

except KeyboardInterrupt:
  current_date_file = datetime.now(paris)
  current_date_file = current_date_file.strftime('%d-%m-%Y %H:%M:%S')
  name_file = current_date_file + "-" + "ml.log"
  print (name_file)
  shutil.copyfile('MoulinLauzes.log',name_file)
  s3 = boto3.resource('s3')
  with open(name_file, 'rb') as data:
    s3.Bucket(config['AWS']['bucket']).put_object(Key=name_file, Body=data)
  print ("Boucle Arrêté")

finally:
  mysql_manager.close_connection_sql()