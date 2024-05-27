import boto3
from botocore.exceptions import ClientError
import json
import configparser

# Création de l'Objet ConfigParser
config = configparser.ConfigParser()

# Lecture du Fichier de Configuration
config.read('config.ini')

class AWSSecretsManager:
    def __init__(self):
        self.secret_name = config['AWS']['secret_name']
        self.region_name = config['AWS']['region_name']
    
    # Méthode Permettant de Récupérer l'ID Suivant le Maximum en commencant à 1 si pas de Valeurs et de Récupérer l'ID Maximum : Utilisé pour des Tests Uniquement
    def return_secret(self):
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(
        service_name='secretsmanager',
        region_name=self.region_name
        )
        try:
            get_secret_value_response = client.get_secret_value(
            SecretId=self.secret_name
            )
        except ClientError as e:
            raise e
        secret = json.loads(get_secret_value_response['SecretString'])
        # print (secret)
        username = str(secret['username'])
        password = str(secret['password'])
        return {"username": username, "password": password}