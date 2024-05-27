import configparser

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Ajout d'une Section et des Constantes
config['InfluxDB'] = {
    'org' : 'Lycée Jules FIL',
    'url' : 'http://34.234.6.183:8086',
    'token' : 'sJWNZrAruT5nHGhxjs02S3Ld7Ljy9YoRUV7FcNAhmwgHDnBxwChzcoDuU3ITMmvby2M7lciEMoWewh8fMXTtug==',
    'bucket' : 'MoulinLauzes',
    'measurement' : 'Monitoring',
    'nametag1' : 'location',
    'valuetag1' : 'Carcassonne'
}

config['MySql'] = {
    'host' : '34.234.6.183',
    'user' : 'grafanaAll',
    'password' : 'PwdPwdPwd-2024',
    'database' : 'MoulinLauzes',
    'table' : 'valeurs'
}

config['AWS'] = {
    'bucket' : 'moulinlauzes',
    'secret_name' : 'rds!db-9fa8189e-47a9-4721-b370-edf2db66f0c0',
    'region_name' : 'us-east-1',
    'hostRDS' : 'db-moulin-lauzes.ccktwd3qsgg4.us-east-1.rds.amazonaws.com',
    'database' : 'MoulinLauzes',
    'table' : 'valeurs'
}

config['Modbus'] = {
    'IP' : '193.251.39.79',
    'Port' : 502,
    'FileCCWMOD' : 'Export.ccwmod'
}

with open('config.ini', 'w') as configfile:
    config.write(configfile)
