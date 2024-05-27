def lambda_handler(event, context):
    print ("Toto")
    fileOpen = open('Test.txt', 'r')
    fileWrite = open('/tmp/TestFileWrite.txt', 'w')
    lines = fileOpen.readlines()
    count = 0
    for line in lines:
        count += 1
        read_line = line.strip()
        print ("Line{}: {}".format(count, read_line))
        fileWrite.writelines(read_line)
        fileWrite.writelines("\n")
    return {
    }