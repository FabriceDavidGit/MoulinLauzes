# Projet Agrégation DAVID Fabrice - SII Informatique - Session 2024
Le projet a été réalisé avec un compte **AWS Academy**, il faut :
* Une **instance EC2** sous **Linux Ubuntu 24.04** - **t2.large** de préférence sauf si vous découpez les services
* Une **adresse IP élastique** associée à l'**instance EC2**
* Un **Bucket S3** : <ins>moulinlauzes</ins>
* Une **base de données RDS** si vous n'utilisez pas **MySQL Server** et un accès à **AWS Secrets Manager**
* Une **connexion VPN** comprenant une **passerelle client**, une **passerelle réseau privé virtuel** et une **connexion VPN Site à Site**

![plot](./Images/Schéma_Infrastructure_AWS.png)

> [!CAUTION]
> Ouvrir les ports <ins>22</ins>, <ins>3000</ins>, <ins>3306</ins> et <ins>8086</ins> pour les **Security Groups** de l'**instance EC2**

> [!TIP]
> Ouvrir le **protocole ICMP** pour les **Security Groups** de l'**instance EC2** pour les tests

> [!WARNING]
> <ins>Mettre le **rôle IAM** <ins>LabInstanceProfile</ins> sur l'**instance EC2** pour avoir les **Credentials** sur le **Bucket S3** et la **base de données RDS**</ins> :
>
> ![plot](./Images/IAM_Role.png)

## Install apt
~~~ shell
sudo apt update
sudo apt install -y python3
sudo apt install -y python3-pip
sudo apt install -y pythonpy
sudo apt install -y python3-venv
sudo apt install -y unzip

~~~

## Amazon RDS
> [!IMPORTANT]
> <ins>Bien respecter les consignes de l'installation d'**Amazon RDS**</ins> :
> 
> ![plot](./Images/Amazon_RDS_1.png)
> 
> ![plot](./Images/Amazon_RDS_2.png)
> 
> ![plot](./Images/Amazon_RDS_3.png)

> [!TIP]
> <ins>Gérer la rotation des mots de passe aves **AWS Secrets Manager** et attribuer la sécurisation de l'accès à la base de données avec un **rôle IAM**</ins> :
> 
> ![plot](./Images/AWS_Secrets_Manager.png)
> 
> ![plot](./Images/Amazon_RDS_Modify_Role_IAM.png)

> [!CAUTION]
> <ins>Configurer les **Securitys Groups** de votre **instance EC2** avec l'assistant d'**Amazon RDS**</ins> :
> 
> ![plot](./Images/Amazon_RDS_Configure_EC2_1.png)
> 
> ![plot](./Images/Amazon_RDS_Configure_EC2_2.png)
> 
> ![plot](./Images/Amazon_RDS_Configure_EC2_3.png)

> [!TIP]
> Un script (fonctionne avec le *Config.ini*) est fourni pour la création de la base de données avec **Amazon RDS**, pensez à l'utiliser 😄 :
> ~~~ shell
> python CreateTableDB.py
> ~~~


## Install MySQL Server si vous n'utilisez pas Amazon RDS
~~~ shell
sudo apt install -y mysql-server
sudo apt install -y phpmyadmin
~~~

> [!TIP]
> Choisir <ins>Apache2</ins>, <ins>Yes</ins> et <ins>pas de mot de passe</ins> en appuyant sur *Entrée*

~~~ shell
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
~~~

> [!IMPORTANT]
> bind-address : Mettre l'<ins>adresse IP publique</ins> de votre moulin si vous utilisez une machine virtuelle

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
> Commenter la ligne n°2 :  
> deb [ signed-by=/etc/apt/keyrings/grafana.gpg ] https://apt.grafana.com stable main  signed-by=/etc/apt/keyrings/grafana.gpg
> #deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com beta main

~~~ shell
sudo apt update
sudo apt install -y grafana
sudo /bin/systemctl start grafana-server
sudo systemctl enable grafana-server.service
~~~

> [!IMPORTANT]
> Accès à Grafana : http://@IP_Elastique_AWS:3000 :
>
> ![plot](./Images/Grafana.png)

> [!TIP]
> Pour sécuriser Grafana en HTTPS : https://grafana.com/docs/grafana/latest/setup-grafana/set-up-https/

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
> Finir la configuration avec Bucket = MoulinLauzes : http://@IP_Elastique_AWS:8086 :
> 
> ![plot](./Images/InfluxDB.png)

> [!TIP]
> Pour sécuriser InfluxDB en HTTPS : https://docs.influxdata.com/influxdb/v2/admin/security/enable-tls/

## Installer AWS CLI
~~~ shell
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
~~~

## Activer l'environnement virtuel
~~~ shell
python3 -m venv .venv
~~~

> [!NOTE]
> Commande à taper après chaque redémarrage du serveur :

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
## Désactiver l'environnement virtuel
~~~ shell
deactivate
~~~
## Génération des variables
Le fichier **config.py** permet de générer les variables dans un fichier de configuration *config.ini*, vous devrez donc modifier **config.py** et générer le fichier de configuration :
~~~ shell
python config.py
~~~
## Lancement du programme
Le programme se lance avec **main.py** :
~~~ shell
python main.py
~~~
## GitHub
Token provisoire jusqu'au 17 juin 2024 :
~~~ shell
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
~~~

Si erreur de Branch :  

~~~ shell
git pull --ff-only
~~~

~~~ shell
git pull --rebase
~~~


## CCWMOD to CSV File Conversion - Modify By Fabrice DAVID
Cet utilitaire permet de convertir les adresses de Modbus exportées par Connected Components Workbench (CCW) dans un fichier CSV Adapté au Moulin Lauzes à savoir l'export d'un CSV contenant :  

* Name : Nom de la Variable dans CCW
* Address : Adresse Modbus
* Data Type et Sud Elem Type : Contient le type de la variable, il faut utiliser l'un ou l'autre pour définir le type
* Data Type Size : Taille de la donnée en octets
* Data Final Type : Type défini par un traitement effectué

<ins>Fichier original de CCW</ins> : [Export.ccwmod](./Export.ccwmod)

<ins>Exemple de fichier généré</ins> : [Export_Modbus.csv](./Files/Export_Modbus.csv)

Voici une commande pour de l'aide sur la syntaxe :
~~~ shell
python ccwmod-moulin-lauzes-csv.py -h
~~~
Exemple :

~~~ shell
python ccwmod-moulin-lauzes-csv.py -m Export.ccwmod -o Export_Modbus.csv -p Moulin_Lauzes_ -r
~~~

> [!IMPORTANT]
> Cet utilitaire a permis de créer la classe **import_ccwmod_manager.py** mais il peut servir pour convertir le fichier en CSV.

## Connexion VPN Site à Site
Il faudra installer 3 composants AWS pour réaliser la connexion VPN site à site :
* <ins>Une passerelle client</ins> :

![plot](./Images/VPN_Passerelle_Client_2.png)

![plot](./Images/VPN_Passerelle_Client_3.png)

* <ins>Une passerelle réseau privé virtuel</ins> :

![plot](./Images/Passerelle_VPN_1.png)

![plot](./Images/Passerelle_VPN_2.png)

![plot](./Images/Passerelle_VPN_3.png)

![plot](./Images/Passerelle_VPN_4.png)

![plot](./Images/Passerelle_VPN_5.png)

* <ins>Une connexion VPN Site à Site</ins> :

![plot](./Images/VPN_Site_a_Site_1.png)

![plot](./Images/VPN_Site_a_Site_2.png)

![plot](./Images/VPN_Site_a_Site_3.png)

Il faudra configurer votre routeur Internet, une Livebox est situé sur le réseau du Moulin. Vous récupererez l'adresse IP côté AWS et la clé partagé en téléchargeant le fichier de configuration du tunnel n°1 :

![plot](./Images/Configuration_Livebox_VPN.png)

Il faut configurer la propagation du routage dans la table du routage de la passerelle VPN :

![plot](./Images/Propagation_Table_Routage_AWS_1.png)

![plot](./Images/Propagation_Table_Routage_AWS_2.png)

![plot](./Images/Propagation_Table_Routage_AWS_3.png)

Il faut configurer les options du tunnel n°1 AWS dans la console AWS et dans la Livebox :

![plot](./Images/AWS_VPN_Site_a_Site_Configuration_Tunnel_1_1.png)

![plot](./Images/AWS_VPN_Site_a_Site_Configuration_Tunnel_1_2.png)

![plot](./Images/AWS_VPN_Site_a_Site_Configuration_Tunnel_1_3.png)

![plot](./Images/Livebox_Configuration_Tunnel_1.png)

Quand le tunnel sera monté, vous pourrez le visualiser dans la console d'AWS et de la Livebox :

![plot](./Images/AWS_VPN_Site_a_Site_Tunnel_1_Test.png)

![plot](./Images/Livebox_Tunnel_1_Test.png)
