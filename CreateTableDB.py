# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

import boto3
from botocore.exceptions import ClientError
import json
import mysql.connector
import configparser

from aws_secrets_manager import AWSSecretsManager

# Création d'un Objet de la Classe AWSSecretsManager
aws_secrets_manager = AWSSecretsManager()

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Lecture du Fichier de Configuration avec toutes les Variables
config.read('config.ini')

secret = aws_secrets_manager.return_secret()

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
    print('Base de Données Effacée')
    cur.execute(f"""CREATE DATABASE {db};""")
    print('Base de Données Créée')
else:
    cur.execute(f"""CREATE DATABASE {db};""")
    print('Base de Données Créee')

print('Table Créée')

conn.commit()

conn.close()

conn = mysql.connector.connect(
    host=config['AWS']['hostRDS'],
    user=secret["username"],
    password=secret["password"],
    database=config['AWS']['database']
    )

cur = conn.cursor()

table = config['AWS']['table']

cur.execute(f"""CREATE TABLE {table} (id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT, temps DATETIME DEFAULT CURRENT_TIMESTAMP, date DATE NULL, """ \
            "heure TIME NULL, capt_bas_moulin TINYINT NULL, sign_ext_son TINYINT NULL, capt_rot_blute TINYINT NULL, inter_shunt_secu TINYINT NULL, " \
            "capt_ensach TINYINT NULL, run_powerflex TINYINT NULL, moteur_succion TINYINT NULL, moteur_son TINYINT NULL, battage TINYINT NULL, out_sign_son TINYINT NULL, " \
            " moteur_bluterie TINYINT NULL, courrant_meule REAL NULL, stop_powerflex_true TINYINT NULL, stop_powerflex TINYINT NULL, start_poxerflex TINYINT NULL, " \
            "start_bluterie TINYINT NULL, current_meule REAL NULL, t_meule SMALLINT NULL, capt_rot_blut TINYINT NULL, alarm_entret TINYINT NULL, " \
            "horametre INT NULL, retour_freq_meule REAL NULL, stop_powerflex_vibrat TINYINT NULL, reg_intens_meule REAL NULL, capt_ensach_alarm TINYINT NULL, " \
            " capt_bas_alarm TINYINT NULL, intensite_meule TINYINT NULL, arret_vibra TINYINT NULL, succion_force TINYINT NULL, vibra_eleve TINYINT NULL, vidan_trem TINYINT NULL, " \
            "speed_ref_vibrat REAL NULL, start_powerflex_vibrat TINYINT NULL, cv_manuel REAL NULL, PRIMARY KEY (id));")
print('Table Créée')
user = "grafanaReader"
password = "PwdPwdPwd-2024"
cur.execute(f"""CREATE USER {user} IDENTIFIED BY '{password}';""")
cur.execute(f"""GRANT SELECT ON {db}.* TO {user}@'%';""")
cur.execute(f"""FLUSH PRIVILEGES;""")
print('Utilisateur Créé')

conn.commit()

conn.close()