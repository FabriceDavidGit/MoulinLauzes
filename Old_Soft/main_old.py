from pyModbusTCP.client import ModbusClient
from datetime import date
from datetime import datetime
import time
import mysql.connector
import pytz
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import logging
import boto3
import shutil
import configparser
from influxdb_manager import InfluxDBManager

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Lecture du Fichier de Configuration
config.read('config.ini')

client = InfluxDBClient(url=config['InfluxDB']['url'], token=config['InfluxDB']['token'], org="org")

bucket="MoulinLauzes"

# Création d'un Objet de la Classe InfluxDBManager
infdb_manager = InfluxDBManager()


# Connexion à la Base de Données
conn = mysql.connector.connect(
  host=config['MySql']['host'],
  user=config['MySql']['user'],
  password=config['MySql']['password'],
  database=config['MySql']['database']
)

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
  # print ("Exposant : ",exposant)
  exposant = 2**(exposant - 127)
  # print ("Exposant : ",exposant)
  # Calcul de la Mantisse
  for i in range(9,32):
    index = i - 8
    mantisse = (int(value_32bits[i]) * (1/(2**index))) + mantisse
  # print ("Mantisse : ",mantisse)
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
    # print (index)
    value = (int(value_bits[i]) * (2**index)) + value
  # Complément à 1 si de Signe
  if value_bits[0] == True:
    value = (-1 * (value + 1))
  return value

def send_influxdb(field, value):
  write_api = client.write_api(write_options=SYNCHRONOUS)
  point = (
     Point(config['InfluxDB']['measurement'])
     .tag(config['InfluxDB']['nametag1'], config['InfluxDB']['valuetag1'])
     .field(field, value)
   )
  write_api.write(bucket=bucket, org=config['InfluxDB']['org'], record=point)
  time.sleep(1)


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
    cur = conn.cursor()
    cur.execute("LOCK TABLES valeurs WRITE")
    cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM valeurs")
    max_id = cur.fetchone()[0]
    print ("ID Max : ",max_id)
    capt_bas_moulin = c.read_coils(0, 1)
    print (capt_bas_moulin)
    cur.execute("INSERT INTO valeurs (capt_bas_moulin) VALUES (%s)", capt_bas_moulin)
    print ("Type des Variables capt_bas_moulin : ",type(capt_bas_moulin),"\n")
    print ("capt_bas_moulin : ",capt_bas_moulin,"\n")
    cur.execute("SELECT MAX(id) FROM valeurs")
    id = cur.fetchone()[0]
    cur.execute("UPDATE valeurs SET date = %s WHERE id = %s",(today,id))
    cur.execute("UPDATE valeurs SET heure = %s WHERE id = %s",(current_time,id))
    sign_ext_son = c.read_coils(1, 1)
    sign_ext_son = sign_ext_son[0]
    cur.execute("UPDATE valeurs SET sign_ext_son = %s WHERE id = %s",(sign_ext_son,id))
    capt_rot_blute = c.read_coils(2, 1)
    capt_rot_blute = capt_rot_blute[0]
    cur.execute("UPDATE valeurs SET capt_rot_blute = %s WHERE id = %s",(capt_rot_blute,id))
    inter_shunt_secu = c.read_coils(3, 1)
    inter_shunt_secu = inter_shunt_secu[0]
    cur.execute("UPDATE valeurs SET inter_shunt_secu = %s WHERE id = %s",(inter_shunt_secu,id))
    capt_ensach = c.read_coils(4, 1)
    capt_ensach = capt_ensach[0]
    cur.execute("UPDATE valeurs SET capt_ensach = %s WHERE id = %s",(capt_ensach,id))
    run_powerflex = c.read_coils(5, 1)
    run_powerflex = run_powerflex[0]
    cur.execute("UPDATE valeurs SET run_powerflex = %s WHERE id = %s",(run_powerflex,id))
    moteur_succion = c.read_coils(6, 1)
    moteur_succion = moteur_succion[0]
    cur.execute("UPDATE valeurs SET moteur_succion = %s WHERE id = %s",(moteur_succion,id))
    moteur_son = c.read_coils(7, 1)
    moteur_son = moteur_son[0]
    cur.execute("UPDATE valeurs SET moteur_son = %s WHERE id = %s",(moteur_son,id))
    battage = c.read_coils(8, 1)
    battage = battage[0]
    cur.execute("UPDATE valeurs SET battage = %s WHERE id = %s",(battage,id))
    out_sign_son = c.read_coils(9, 1)
    out_sign_son = out_sign_son[0]
    cur.execute("UPDATE valeurs SET out_sign_son = %s WHERE id = %s",(out_sign_son,id))
    moteur_bluterie = c.read_coils(10, 1)
    moteur_bluterie = moteur_bluterie[0]
    cur.execute("UPDATE valeurs SET moteur_bluterie = %s WHERE id = %s",(moteur_bluterie,id))
    # Courant Meule Mesurée en Réel sur 32 Bits
    courant_meule_mesuree = c.read_coils(11, 32)
    courant_meule_mesuree = convert_32bits_reel(courant_meule_mesuree)
    cur.execute("UPDATE valeurs SET courant_meule_mesuree = %s WHERE id = %s",(courant_meule_mesuree,id))
    infdb_manager.send_InfluxDB("courant_meule_mesuree",courant_meule_mesuree)
    #send_influxdb("courant_meule_mesuree", courant_meule_mesuree)
    # write_api = client.write_api(write_options=SYNCHRONOUS)
    # point = (
    #   Point("Monitoring")
    #   .tag("location", "Carcassonne")
    #   .field("courant_meule_mesuree", courant_meule_mesuree)
    # )
    # write_api.write(bucket=bucket, org="Lycée Jules FIL", record=point)
    # time.sleep(1)
    stop_powerflex_true = c.read_coils(43, 1)
    stop_powerflex_true = stop_powerflex_true[0]
    cur.execute("UPDATE valeurs SET stop_powerflex_true = %s WHERE id = %s",(stop_powerflex_true,id))
    # Stop PowerFlex en Booléen sur 5 Bits
    stop_powerflex = c.read_coils(44, 5)
    stop_powerflex_4 = int(stop_powerflex[4])
    cur.execute("UPDATE valeurs SET stop_powerflex_4 = %s WHERE id = %s",(stop_powerflex_4,id))
    start_powerflex = c.read_coils(49, 1)
    start_powerflex = int(start_powerflex[0])
    cur.execute("UPDATE valeurs SET start_powerflex = %s WHERE id = %s",(start_powerflex,id))
    # Start Bluterie en Booléen sur 2 Bits
    start_bluterie = c.read_coils(50, 2)
    start_bluterie_0 = int(start_bluterie[0])
    cur.execute("UPDATE valeurs SET start_bluterie_0 = %s WHERE id = %s",(start_bluterie_0,id))
    # Current Meule Mesurée en Réel sur 32 Bits
    current_meule_mesuree = c.read_coils(52, 32)
    current_meule_mesuree = convert_32bits_reel(current_meule_mesuree)
    cur.execute("UPDATE valeurs SET current_meule_mesuree = %s WHERE id = %s",(current_meule_mesuree,id))
    # Température Meule en INT sur 16 Bits
    temperature_meule = c.read_coils(84, 16)
    temperature_meule = convert_bits_int(temperature_meule)
    cur.execute("UPDATE valeurs SET temperature_meule = %s WHERE id = %s",(temperature_meule,id))
    send_influxdb("temperature_meule", temperature_meule)
    capt_rot_bluterie_0 = c.read_coils(100, 1)
    capt_rot_bluterie_0 = int(capt_rot_bluterie_0[0])
    cur.execute("UPDATE valeurs SET capt_rot_bluterie_0 = %s WHERE id = %s",(capt_rot_bluterie_0,id))
    alarm_entretien = c.read_coils(101, 1)
    alarm_entretien = int(alarm_entretien[0])
    cur.execute("UPDATE valeurs SET alarm_entretien = %s WHERE id = %s",(alarm_entretien,id))
    # Horamètre en DINT sur 32 Bits
    horametre = c.read_coils(102, 32)
    horametre = convert_bits_int(horametre)
    cur.execute("UPDATE valeurs SET horametre = %s WHERE id = %s",(horametre,id))
    # Retour Fréquence Meule en Réel sur 32 Bits
    retour_frequence_meule = c.read_coils(134, 32)
    retour_frequence_meule = convert_32bits_reel(retour_frequence_meule)
    cur.execute("UPDATE valeurs SET retour_frequence_meule = %s WHERE id = %s",(retour_frequence_meule,id))
    send_influxdb("retour_frequence_meule", retour_frequence_meule)
    stop_powerflex_vibrat = c.read_coils(166, 1)
    stop_powerflex_vibrat = int(stop_powerflex_vibrat[0])
    cur.execute("UPDATE valeurs SET stop_powerflex_vibrat = %s WHERE id = %s",(stop_powerflex_vibrat,id))
    # Réglage Intensité Meule en Réel sur 32 Bits
    reglage_intensite_meule = c.read_coils(167, 32)
    reglage_intensite_meule = convert_32bits_reel(reglage_intensite_meule)
    cur.execute("UPDATE valeurs SET reglage_intensite_meule = %s WHERE id = %s",(reglage_intensite_meule,id))
    send_influxdb("reglage_intensite_meule", reglage_intensite_meule)
    capt_ensach_alarme = c.read_coils(199, 1)
    capt_ensach_alarme = int(capt_ensach_alarme[0])
    cur.execute("UPDATE valeurs SET capt_ensach_alarme = %s WHERE id = %s",(capt_ensach_alarme,id))
    capt_bas_alarme = c.read_coils(200, 1)
    capt_bas_alarme = int(capt_bas_alarme[0])
    cur.execute("UPDATE valeurs SET capt_bas_alarme = %s WHERE id = %s",(capt_bas_alarme,id))
    intensite_meule = c.read_coils(201, 1)
    intensite_meule = int(intensite_meule[0])
    cur.execute("UPDATE valeurs SET intensite_meule = %s WHERE id = %s",(intensite_meule,id))
    arret_vibra = c.read_coils(202, 1)
    arret_vibra = int(arret_vibra[0])
    cur.execute("UPDATE valeurs SET arret_vibra = %s WHERE id = %s",(arret_vibra,id))
    succion_force = c.read_coils(203, 1)
    succion_force = int(succion_force[0])
    cur.execute("UPDATE valeurs SET succion_force = %s WHERE id = %s",(succion_force,id))
    vibra_eleve = c.read_coils(204, 1)
    vibra_eleve = int(vibra_eleve[0])
    cur.execute("UPDATE valeurs SET vibra_eleve = %s WHERE id = %s",(vibra_eleve,id))
    vidan_trem = c.read_coils(205, 1)
    vidan_trem = int(vidan_trem[0])
    cur.execute("UPDATE valeurs SET vidan_trem = %s WHERE id = %s",(vidan_trem,id))
    # Vitesse Vibrateur en Réel sur 32 Bits
    speed_ref_vibrat = c.read_coils(206, 32)
    speed_ref_vibrat = convert_32bits_reel(speed_ref_vibrat)
    cur.execute("UPDATE valeurs SET speed_ref_vibrat = %s WHERE id = %s",(speed_ref_vibrat,id))
    send_influxdb("speed_ref_vibrat", speed_ref_vibrat)
    start_powerflex_vibrat = c.read_coils(238, 1)
    start_powerflex_vibrat = int(start_powerflex_vibrat[0])
    cur.execute("UPDATE valeurs SET start_powerflex_vibrat = %s WHERE id = %s",(start_powerflex_vibrat,id))
    # Consigne Vibrateur en Réel sur 32 Bits
    cv_manuel = c.read_coils(239, 32)
    cv_manuel = convert_32bits_reel(cv_manuel)
    cur.execute("UPDATE valeurs SET cv_manuel = %s WHERE id = %s",(cv_manuel,id))
    send_influxdb("cv_manuel", cv_manuel)
    conn.commit()
    cur.execute("UNLOCK TABLES")
    cur.close()

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
    conn.close()
