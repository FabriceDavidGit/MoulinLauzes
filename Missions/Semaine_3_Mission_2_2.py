from pyModbusTCP.client import ModbusClient
import time

def convert_bits_int(value_bits):
  # Initialisation des Variables
  value = 0
  signe = False
  # Inversion des Valeurs et Test du Signe
  print (value_bits)
  value_bits.reverse()
  print (value_bits)
  if value_bits[0] == True:
    value_bits = [not elem for elem in value_bits]
    print (value_bits)
    signe = True
  # Conversion Booléen en Entier
  value_bits = [int(b) for b in value_bits]
  print (value_bits)
  # Conversion en Entier
  for i in range(1,len(value_bits)):
    index = len(value_bits) - i - 1
    # print (index)
    value = (int(value_bits[i]) * (2**index)) + value
  # Complément à 1 si de Signe
  if signe == True:
    value = (-1 * (value + 1))
    print (value)
  return value

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



# Accès à l'Automate par ModBus TCP
c = ModbusClient(host="193.251.39.79", port=502, unit_id=1, auto_open=True)
# Lecture de Tous les Registres
regs = c.read_coils(1, 205)
if regs:
  print ("Lecture des Registres Correct\n")
  print ("Type des Variables : ",type(regs),"\n")
else:
  print ("Erreur de Lecture")

try:
  while True:

    # Registre en Liste de Booléen de 1 sauf Mention

    capt_bas_moulin = c.read_coils(0, 1)

    print ("Type des Variables capt_bas_moulin : ",type(capt_bas_moulin),"\n")
    print ("capt_bas_moulin : ",capt_bas_moulin,"\n")
    sign_ext_son = c.read_coils(1, 1)
    sign_ext_son = sign_ext_son[0]
    capt_rot_blute = c.read_coils(2, 1)
    capt_rot_blute = capt_rot_blute[0]
    inter_shunt_secu = c.read_coils(3, 1)
    inter_shunt_secu = inter_shunt_secu[0]
    capt_ensach = c.read_coils(4, 1)
    capt_ensach = capt_ensach[0]
    run_powerflex = c.read_coils(5, 1)
    run_powerflex = run_powerflex[0]
    moteur_succion = c.read_coils(6, 1)
    moteur_succion = moteur_succion[0]
    moteur_son = c.read_coils(7, 1)
    moteur_son = moteur_son[0]
    battage = c.read_coils(8, 1)
    battage = battage[0]
    out_sign_son = c.read_coils(9, 1)
    out_sign_son = out_sign_son[0]
    moteur_bluterie = c.read_coils(10, 1)
    moteur_bluterie = moteur_bluterie[0]

    # Courant Meule Mesurée en Réel sur 32 Bits
    courant_meule_mesuree = c.read_coils(11, 32)
    courant_meule_mesuree = convert_32bits_reel(courant_meule_mesuree)

    stop_powerflex_true = c.read_coils(43, 1)
    stop_powerflex_true = stop_powerflex_true[0]

    # Stop PowerFlex en Booléen sur 5 Bits
    stop_powerflex = c.read_coils(44, 5)
    stop_powerflex_4 = int(stop_powerflex[4])

    start_powerflex = c.read_coils(49, 1)
    start_powerflex = int(start_powerflex[0])

    # Start Bluterie en Booléen sur 2 Bits
    start_bluterie = c.read_coils(50, 2)
    start_bluterie_0 = int(start_bluterie[0])

    # Current Meule Mesurée en Réel sur 32 Bits
    current_meule_mesuree = c.read_coils(52, 32)
    current_meule_mesuree = convert_32bits_reel(current_meule_mesuree)


    # Température Meule en INT sur 16 Bits
    temperature_meule = c.read_coils(84, 16)
    temperature_meule = convert_bits_int(temperature_meule)

    capt_rot_bluterie_0 = c.read_coils(100, 1)
    capt_rot_bluterie_0 = int(capt_rot_bluterie_0[0])
    alarm_entretien = c.read_coils(101, 1)
    alarm_entretien = int(alarm_entretien[0])

    # Horamètre en DINT sur 32 Bits
    horametre = c.read_coils(102, 32)
    horametre = convert_bits_int(horametre)

    # Retour Fréquence Meule en Réel sur 32 Bits
    retour_frequence_meule = c.read_coils(134, 32)
    retour_frequence_meule = convert_32bits_reel(retour_frequence_meule)

    stop_powerflex_vibrat = c.read_coils(166, 1)
    stop_powerflex_vibrat = int(stop_powerflex_vibrat[0])

    # Réglage Intensité Meule en Réel sur 32 Bits
    reglage_intensite_meule = c.read_coils(167, 32)
    reglage_intensite_meule = convert_32bits_reel(reglage_intensite_meule)

    capt_ensach_alarme = c.read_coils(199, 1)
    capt_ensach_alarme = int(capt_ensach_alarme[0])

    capt_bas_alarme = c.read_coils(200, 1)
    capt_bas_alarme = int(capt_bas_alarme[0])

    intensite_meule = c.read_coils(201, 1)
    intensite_meule = int(intensite_meule[0])

    arret_vibra = c.read_coils(202, 1)
    arret_vibra = int(arret_vibra[0])

    succion_force = c.read_coils(203, 1)
    succion_force = int(succion_force[0])

    vibra_eleve = c.read_coils(204, 1)
    vibra_eleve = int(vibra_eleve[0])

    vidan_trem = c.read_coils(205, 1)
    vidan_trem = int(vidan_trem[0])

    # Vitesse Vibrateur en Réel sur 32 Bits
    speed_ref_vibrat = c.read_coils(206, 32)
  
    # speed_ref_vibrat = convert_32bits_reel(speed_ref_vibrat)
    start_powerflex_vibrat = c.read_coils(238, 1)
  
    # Consigne Vibrateur en Réel sur 32 Bits
    cv_manuel = c.read_coils(239, 32)
  

    # Affichage
    print ("Etat Capteur Bas Moulin : ",capt_bas_moulin)
    print ("Sign Ext Son : ",sign_ext_son)
    print ("Capteur Rotation Bluterie : ",capt_rot_blute)
    print ("Etat Capteur Interrupteur Shunt Sécurité : ",inter_shunt_secu)
    print ("Etat Capteur Ensachage : ",capt_ensach)
    print ("Etat Run PowerFlex : ",run_powerflex)
    print ("Etat Moteur Succion : ",moteur_succion)
    print ("Etat Moteur Son : ",moteur_son)
    print ("Etat Moteur Battage : ",battage)
    print ("Etat Out Son : ",out_sign_son)
    print ("Etat Moteur Bluterie : ",moteur_bluterie)
    print ("Courant Meule Mesurée : " + str(courant_meule_mesuree) + " A")
    print ("Stop PowerFlex True : ",stop_powerflex_true)
    print ("Stop PowerFlex : ",stop_powerflex)
    print ("Stop PowerFlex 4 : ",stop_powerflex_4)
    print ("Start PowerFlex : ",start_powerflex)
    print ("Start Bluterie : ",start_bluterie)
    print ("Start Bluterie 0 : ",start_bluterie_0)
    print ("Current Meule Mesurée : " + str(current_meule_mesuree) + " A")
    print ("Température Meule : " + str(temperature_meule) + " °C")
    print ("Etat Capteur Rotation Bluterie : ",capt_rot_bluterie_0)
    print ("Etat Alarme Entretien : ",alarm_entretien)
    print ("Horamètre : " + str(horametre) + " h")
    print ("Retour Fréquence Meule : " + str(retour_frequence_meule) + " Hz")
    print ("Stop PowerFlex Vibrateur : ",stop_powerflex_vibrat)
    print ("Réglage Intensité Meule : " + str(reglage_intensite_meule) + " A")
    print ("Etat Capteur Ensachage : ",capt_ensach_alarme)
    print ("Etat Capteur Bas Alarme : ",capt_bas_alarme)
    print ("Etat Intensité Meule : ",intensite_meule)
    print ("Arrêt Vibrateur : ",arret_vibra)
    print ("Etat Succion Forcé : ",succion_force)
    print ("Etat Vibration Elevé : ",vibra_eleve)
    print ("Etat Vidange Trémis : ",vidan_trem)
    print ("------------------------------------------------------")
    time.sleep(1)

except KeyboardInterrupt:
  print ("Boucle Arrêté")