#!/bin/bash
# Script d'initialisation d'une session SSH

# Copier les tokens de connexion AWS pour les mettre dans notre instance plus tard
credentials=$( cat "C:\Users\Julien Giovinazzo\.aws\credentials" )

# Lancer notre instance
aws ec2 start-instances --instance-ids "i-068d57622c916ab92"

# Attendre 45 secondes le temps que l'instance s'initialise
sleep 45

# Recuperer son adresse ip public pour s'y connecter en SSH
ip=$( aws ec2 describe-instances --instance-ids "i-068d57622c916ab92" --query "Reservations[*].Instances[*].PublicIpAddress" --output text )


# ${ip//./-} : remplace les '.' par de '-'
myarg="ec2-user@ec2-${ip//./-}.compute-1.amazonaws.com"

# Aller dans le dossier avec ma clé
cd "C:\Users\Julien Giovinazzo\Documents\COURS\FISE3\Cloud Computing 2020-2021\AWS"

# Connexion SSH
ssh -i "myKey.pem" $myarg << EOF

  echo "$credentials" > ~/.aws/credentials
  python3 ~/lab3/main.py

EOF

echo "Done."