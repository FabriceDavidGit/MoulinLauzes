import mysql.connector
from datetime import date, datetime
import time
import pytz

import configparser

from aws_secrets_manager import AWSSecretsManager

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Création d'un Objet de la Classe AWSSecretsManager
aws_secrets_manager = AWSSecretsManager()

# Lecture du Fichier de Configuration
config.read('config.ini')

class MySQLManager:
    def __init__(self):
        secret = aws_secrets_manager.return_secret()
        self.conn = mysql.connector.connect(
            host=config['AWS']['hostrds'],
            user=secret["username"],
            password=secret["password"],
            database=config['AWS']['database']
            )
        self.today = date.today()
        paris = pytz.timezone('Europe/Paris')
        self.current_date_time = datetime.now(paris)
        self.current_time = self.current_date_time.strftime('%H:%M:%S')
        self.cur = self.conn.cursor()
        self.table = config['AWS']['table']

    # Méthode Permettant de Récupérer l'ID Suivant le Maximum en commencant à 1 si pas de Valeurs et de Récupérer l'ID Maximum : Utilisé pour des Tests Uniquement
    def return_id_sql(self, field):
        if field=="max+1":
            self.cur.execute(f"""SELECT COALESCE(MAX(id), 0) + 1 FROM {self.table}""")
            max_1_id = self.cur.fetchone()[0]
            print ("Maximum ID + 1 : ",max_1_id)
            return max_1_id
        if field=="max":
            self.cur.execute(f"""SELECT MAX(id) FROM {self.table}""")
            max_id = self.cur.fetchone()[0]
            print ("Maximum ID : ",max_id)
            return max_id
    # Méthode pour Ouvrir la Connexion SQL

    # Méthode pour Fermer la Connexion SQL
    def close_connection_sql(self):
        self.conn.close()

    # Méthode Permettant d'Envoyer la Première Valeur dans la Table
    def push_first_value_sql(self):
        req_sql = f"""INSERT INTO {self.table} (date,heure) VALUES (%s,%s)"""
        value_sql = (self.today,self.current_time)
        self.cur.execute(req_sql, value_sql)
        self.conn.commit()

    # Méthode Permettant de Pusher les Valeurs dans la Table
    def push_value_sql(self, field, value):
        self.cur.execute(f"""SELECT MAX(id) FROM {self.table}""")
        id = self.cur.fetchone()[0]
        self.cur.execute(f"""UPDATE {self.table} SET {field} = {value} WHERE id = {id}""")
        self.conn.commit()