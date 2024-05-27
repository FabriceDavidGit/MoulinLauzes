fileOpen = open('TestFileR.txt', 'r')
fileWrite = open('TestFileWrite.txt', 'w')
fileConvert = open('TestFileConvert.txt', 'w')

lines = fileOpen.readlines()

count = 0

for line in lines:
  count += 1
  read_line = line.strip()
  fileWrite.writelines(read_line)
  if read_line.startswith("2"):
    fileConvert.writelines(read_line)
    fileConvert.writelines("\n") 
  fileWrite.writelines("\n")
  print ("Line{}: {}".format(count, read_line))

fileOpen.close()
fileWrite.close()
fileConvert.close()