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

test1 = convert_bits_int([True, True, True, True, True, True, True, False])
print (test1)
test2 = convert_bits_int([False, True, False, False, False, False, False, False])
print (test2)
test3 = convert_bits_int([True, False, False, False, False, False, False, False])
print (test3)
test4 = convert_bits_int([False, False, False, False, False, False, False, False])
print (test4)
test5 = convert_bits_int([True, True, True, True, True, True, True, True])
print (test5)
test6 = convert_bits_int([False, True, True, True, True, True, True, True])
print (test6)
test7 = convert_bits_int([True, False, False, False, False, False, False, True])
print (test7)
test8 = convert_bits_int([False, False, False, False, False, False, False, True])
print (test8)

testPositif = convert_bits_int([False, True, True, False, True, False, False, False, False, False, False ,False, False, False, False, False])
print (testPositif)

testNegatif = convert_bits_int([False, True, True, False, True, False, False, False, False, False, False ,False, False, False, False, True])
print (testNegatif)

