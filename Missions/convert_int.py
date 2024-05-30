def convert_bits_int(value_bits):
 # Initialisation des Variables
 value = 0
 signe = False
 # Inversion des Valeurs et Mise à Test du Signe
 value_bits.reverse()
 if value_bits[0] == True:
   signe = True
   value_bits[0] == False
 # Conversion Booléen en Entier
 value_bits = [int(b) for b in value_bits]
 # Conversion en Entier
 for i in range(1,len(value_bits)):
   index = len(value_bits) - i - 1
   # print (index)
   value = (int(value_bits[i]) * (2**index)) + value
 # Complément à 1 si de Signe
 if signe == True:
   value = (-1 * (value + 1))
 return value

testPositif = convert_bits_int([False, True, True, False, True, False, False, False, False, False, False ,False, False, False, False, False])
print (testPositif)

testNegatif = convert_bits_int([False, True, True, False, True, False, False, False, False, False, False ,False, False, False, False, True])
print (testNegatif)

