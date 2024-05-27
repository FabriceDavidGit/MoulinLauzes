# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError
import json
import mysql.connector
import configparser

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Lecture du Fichier de Configuration avec toutes les Variables
config.read('config.ini')

def return_secret():

    secret_name = config['AWS']['secret_name']
    region_name = config['AWS']['region_name']

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = json.loads(get_secret_value_response['SecretString'])
    # print (secret)
    username = str(secret['username'])
    password = str(secret['password'])
    return {"username": username, "password": password}

secret = return_secret()

conn = mysql.connector.connect(
    host=config['AWS']['hostRDS'],
    user=secret["username"],
    password=secret["password"]
    )

cur = conn.cursor()

db = config['AWS']['database']

cur.execute("SHOW DATABASES;")

databases = cur.fetchall()

database_exists = False

for database in databases:
    if db in database:
        database_exists = True
        break

if database_exists:
    cur.execute(f"""DROP DATABASE {db};""")
    cur.execute(f"""CREATE DATABASE {db};""")
else:
    cur.execute(f"""CREATE DATABASE {db};""")

conn.commit()

conn.close()

conn = mysql.connector.connect(
    host=config['AWS']['hostRDS'],
    user=secret["username"],
    password=secret["password"],
    database=config['AWS']['database']
    )

cur = conn.cursor()

cur.execute("CREATE TABLE valeurs (id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT, temps DATETIME DEFAULT CURRENT_TIMESTAMP, date DATE NULL, " \
            "heure TIME NULL, capt_bas_moulin TINYINT NULL, sign_ext_son TINYINT NULL, capt_rot_blute TINYINT NULL, inter_shunt_secu TINYINT NULL, " \
            "capt_ensach TINYINT NULL, run_powerflex TINYINT NULL, moteur_succion TINYINT NULL, moteur_son TINYINT NULL, battage TINYINT NULL, out_sign_son TINYINT NULL, " \
            " moteur_bluterie TINYINT NULL, courant_meule_mesuree REAL NULL, stop_powerflex_true TINYINT NULL, stop_powerflex_4 TINYINT NULL, start_powerflex TINYINT NULL, " \
            "start_bluterie_0 TINYINT NULL, current_meule_mesuree REAL NULL, temperature_meule SMALLINT NULL, capt_rot_bluterie_0 TINYINT NULL, alarm_entretien TINYINT NULL, " \
            "horametre INT NULL, retour_frequence_meule REAL NULL, stop_powerflex_vibrat TINYINT NULL, reglage_intensite_meule REAL NULL, capt_ensach_alarme TINYINT NULL, " \
            " capt_bas_alarme TINYINT NULL, intensite_meule TINYINT NULL, arret_vibra TINYINT NULL, succion_force TINYINT NULL, vibra_eleve TINYINT NULL, vidan_trem TINYINT NULL, " \
            "speed_ref_vibrat REAL NULL, start_powerflex_vibrat TINYINT NULL, cv_manuel REAL NULL, PRIMARY KEY (id));")

conn.commit()

conn.close()