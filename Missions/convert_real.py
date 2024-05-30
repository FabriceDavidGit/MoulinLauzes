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


test1 = convert_32bits_reel([True, False, True, True, True, True, False, False, False, True, False, True, False, False, False, False, True, True, True, False, False, False, False, False, False, False, False, False, False, False, True, False])
print (test1)

test1 = convert_32bits_reel([True, False, True, True, True, True, False, False, False, True, False, True, False, False, False, False, True, True, True, False, False, False, False, False, False, False, False, False, False, False, True, True])
print (test1)