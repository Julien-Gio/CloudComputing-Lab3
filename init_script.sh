#!/bin/bash
# Script d'initialisation d'une session SSH

# Copier les tokens de connexion AWS pour les mettre dans notre instance plus tard
credentials=$( cat "C:\Users\Julien Giovinazzo\.aws\credentials")

# Lancer notre instance
aws ec2 start-instances --instance-ids "i-068d57622c916ab92"

# Attendre 30 secondes le temps que l'instance s'initialise
sleep 30

# Recuperer son adresse ip public pour s'y connecter en SSH
ip=$( aws ec2 describe-instances --instance-ids "i-068d57622c916ab92" --query "Reservations[*].Instances[*].PublicIpAddress" --output text )

# Aller dans le dossier avec ma clé
cd "C:\Users\Julien Giovinazzo\Documents\COURS\FISE3\Cloud Computing 2020-2021\AWS"

# ${ip//./-} : remplace les '.' par de '-'
myarg="ec2-user@ec2-${ip//./-}.compute-1.amazonaws.com"

# Connexion SSH
ssh -i "myKey.pem" $myarg << EOF

# Commandes pour l'instance EC2

echo "$credentials" > ~/.aws/credentials
python3 ~/lab3/main.py

# Fin de notre connexion
EOF

echo "Done."
read t