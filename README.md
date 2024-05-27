# Projet Agrégation DAVID Fabrice - SII Informatique - Session 2024
Le projet a été réalisé avec un compte AWS Academy, il faut :
* Une Instance EC2 sous Linux Ubuntu 24.04 - t2.large de Préférence sauf si vous Découpez les Services
* Une Adresse IP Elastique Associée à l'Instance EC2
* Un Bucket S3 : moulinlauzes
* Une Base de Données RDS si vous n'utilisez pas MySQL Server et un Accès à AWS Secrets Manager
* Une Connexion VPN comprenant une Passerelle Cient, une Passerelle Réseau Privé Virtuel et une Connexion VPN Site à Site

> [!CAUTION]
> Ouvrir les Ports 22, 3000, 3306 et 8086 pour les Security Groups de l'Instance EC2

> [!TIP]
> Ouvrir le Protocole ICMP pour les Security Groups de l'Instance EC2 pour les Tests

> [!WARNING]
> Mettre le Rôle IAM LabInstanceProfile sur l'Instance EC2 pour Avoir les Credentials sur le Bucket S3 et la Base de Donnée RDS :
>
> ![plot](./IAM_Role.png)

## Install apt
~~~ shell
sudo apt update
sudo apt install -y python3
sudo apt install -y python3-pip
sudo apt install -y pythonpy
sudo apt install -y python3-venv
sudo apt install -y unzip

~~~

## Install InfluxDB
~~~ shell
sudo tee /etc/apt/sources.list.d/influxdb.list<<EOF
deb [signed-by=/usr/share/keyrings/influxdb-keyring.gpg] https://repos.influxdata.com/ubuntu jammy stable
EOF
curl -fsSL https://repos.influxdata.com/influxdata-archive_compat.key|sudo gpg --dearmor -o /usr/share/keyrings/influxdb-keyring.gpg
sudo apt -y update
sudo apt -y install influxdb2
sudo influxdb start
sudo systemctl enable influxdb.service
~~~

> [!IMPORTANT]
> Finir la Configuration : http://@IP_Elastique_AWS:8086  
> Bucket = MoulinLauzes

## Amazon RDS
> [!IMPORTANT]
> Bien Respecter les Consignes de l'Installation d'Amazon RDS :
> 
> ![plot](./Amazon_RDS_1.png)
> 
> ![plot](./Amazon_RDS_2.png)
> 
> ![plot](./Amazon_RDS_3.png)


> [!TIP]
> Gérer la Rotation des Mots de Passe aves AWS Secrets Manager et Attribuer la Sécurisation de l'Accès à la Base de Données avec un Rôle IAM :
> 
> ![plot](./AWS_Secrets_Manager.png)
> 
> ![plot](./Amazon_RDS_Modify_Role_IAM.png)

> [!CAUTION]
> Configurer les Securitys Groups de votre Instance EC2 avec l'Assistant d'Amazon RDS :
> 
> ![plot](./Amazon_RDS_Configure_EC2_1.png)
> 
> ![plot](./Amazon_RDS_Configure_EC2_2.png)
> 
> ![plot](./Amazon_RDS_Configure_EC2_3.png)


> [!TIP]
> Un Script (Fonctionne avec le *Config.ini*) Est Fourni pour la Création de la Base de Données avec Amazon RDS, Pensez à l'Utiliser 😄 :
> ~~~ shell
> python CreateTableDB.py
> ~~~


## Install MySQL Server Si vous n'Utilisez Pas Amazon RDS
~~~ shell
sudo apt install -y mysql-server
sudo apt install -y phpmyadmin
~~~

> [!TIP]
> Choisir Apache2, Yes et Pas de Mot de Passe en Appuyant sur Entrée

~~~ shell
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
~~~

> [!IMPORTANT]
> bind-address : Mettre l'Adresse IP Publique de votre Moulin si vous Utilisez une Machine Virtuelle

~~~ shell
sudo mysql
~~~

> CREATE USER 'grafanaReader' IDENTIFIED BY 'PwdPwdPwd-2024';  
> CREATE USER 'grafanaAll' IDENTIFIED BY 'PwdPwdPwd-2024';  
> CREATE DATABASE MoulinLauzes;  
> GRANT SELECT ON MoulinLauzes.* TO 'grafanaReader'@'%';  
> GRANT ALL PRIVILEGES ON \*.\* TO 'grafanaAll'@'%' WITH GRANT OPTION;  
> FLUSH PRIVILEGES;  
> USE MoulinLauzes;  

> CREATE TABLE valeurs (  
> id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,  
> temps DATETIME DEFAULT CURRENT_TIMESTAMP,  
> date DATE NULL,  
> heure TIME NULL,  
> capt_bas_moulin TINYINT NULL,  
> sign_ext_son TINYINT NULL,  
> capt_rot_blute TINYINT NULL,  
> inter_shunt_secu TINYINT NULL,  
> capt_ensach TINYINT NULL,  
> run_powerflex TINYINT NULL,  
> moteur_succion TINYINT NULL,  
> moteur_son TINYINT NULL,  
> battage TINYINT NULL,  
> out_sign_son TINYINT NULL,  
> moteur_bluterie TINYINT NULL,  
> courant_meule_mesuree REAL NULL,  
> stop_powerflex_true TINYINT NULL,  
> stop_powerflex_4 TINYINT NULL,  
> start_powerflex TINYINT NULL,  
> start_bluterie_0 TINYINT NULL,  
> current_meule_mesuree REAL NULL,  
> temperature_meule SMALLINT NULL,  
> capt_rot_bluterie_0 TINYINT NULL,  
> alarm_entretien TINYINT NULL,  
> horametre INT NULL,  
> retour_frequence_meule REAL NULL,  
> stop_powerflex_vibrat TINYINT NULL,  
> reglage_intensite_meule REAL NULL,  
> capt_ensach_alarme TINYINT NULL,  
> capt_bas_alarme TINYINT NULL,  
> intensite_meule TINYINT NULL,  
> arret_vibra TINYINT NULL,  
> succion_force TINYINT NULL,  
> vibra_eleve TINYINT NULL,  
> vidan_trem TINYINT NULL,  
> speed_ref_vibrat REAL NULL,  
> start_powerflex_vibrat TINYINT NULL,  
> cv_manuel REAL NULL,  
> PRIMARY KEY (id)  
> );  

## Install Grafana
~~~ shell
sudo apt install -y apt-transport-https software-properties-common wget
sudo mkdir -p /etc/apt/keyrings/
wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com beta main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt update
~~~
~~~ shell
sudo nano /etc/apt/sources.list.d/grafana.list
~~~

> [!IMPORTANT]
> Commenter la Ligne n°2 :  
> deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main  
> #deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com beta main

~~~ shell
sudo apt update
sudo apt install -y grafana
sudo /bin/systemctl start grafana-server
sudo systemctl enable grafana-server.service
~~~

> [!IMPORTANT]
> Accès à Grafana : http://@IP_Elastique_AWS:3000

## Installer AWS CLI
~~~ shell
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
~~~

## Activer l'Environnement Virtuel
~~~ shell
python3 -m venv .venv
~~~

> [!NOTE]
> Commande à Taper Après Chaque Redémarrage du Serveur :

~~~ shell
source .venv/bin/activate
~~~
## Install pip
~~~ shell
pip3 install pyModbusTCP
pip install mysql-connector-python
pip install datetime
pip install pytz
pip3 install influxdb-client
pip install boto3
~~~
## Désactiver l'Environnement Virtuel
~~~ shell
deactivate
~~~
## Génération des Variables
Le fichier **config.py** permet de générer les variables dans un fichier de configuration *config.ini*, vous devrez donc modifier **config.py** et générer le fichier de configuration :
~~~ shell
python config.py
~~~
## Lancement du Programme
Le programme se lance avec **main.py** :
~~~ shell
python main.py
~~~
## GitHub
Token Provisoire jusqu'au 17 Juin 2024 :
~~~ shell
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
~~~

Si Erreur de Branch :  

~~~ shell
git pull --ff-only
~~~

~~~ shell
git pull --rebase
~~~


## CCWMOD to CSV File Conversion - Modify By Fabrice DAVID
Cet utilitaire permet de convertir les adresses de Modbus exportées par Connected Components Workbench (CCW) dans un fichier CSV Adapté au Moulin Lauzes à Savoir un Export d'un CSV contenant :  

* Name : Nom de la Variable dans CCW
* Address : Adresse Modbus
* Data Type et Sud Elem Type : Contient le Type de la Variable, il faut utiliser l'un ou l'autre pour définir le type
* Data Type Size : Taille de la Donnée en Octets
* Data Final Type : Type Défini par un Traitement Effectué

<ins>Fichier Original de CCW</ins> : [Export.ccwmod](./Export.ccwmod)

<ins>Exemple de Fichier Généré</ins> : [Export_Modbus.csv](./Export_Modbus.csv)

Voici une Commande pour de l'Aide sur la Syntaxe :
~~~ shell
python ccwmod-moulin-lauzes-csv.py -h
~~~
Exemple :

~~~ shell
python ccwmod-moulin-lauzes-csv.py -m Export.ccwmod -o Export_Modbus.csv -p Moulin_Lauzes_ -r
~~~

> [!IMPORTANT]
> Cet utilitaire a permis de créer la Classe **import_ccwmod_manager.py** mais il peut servir pour convertir le fichier en CSV.
