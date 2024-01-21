# Pizzaioliste - Système de commande d'SOS

L'objectif de ce projet est de gérer la commande de SOS de la pizzaioliste durant la semaine de campagne CDP.
Cela passe par une interface web client et un serveur backend qui stocke les commandes dans une base de donnée SQLite et envoie celles-ci au serveur discord de la liste.

## Fonctionnalités

- [x] Détails de commande : prénom, nom, email, n°sos, créneau du sos, bat, turne
- [x] Vérification de la limite de 2 sos/jour/personne (via l'email du client)
- [X] Envoie de la demande de SOS au serveur discord
- [X] Interface web admin pour consulter la liste des SOS commandés et effectués
- [ ] Validation du SOS une fois qu'il est achevé (via discord ou l'interface web admin)


## A faire avant le déployement

- [ ] Améliorer les messages d'erreur, notamment quand il a plus de 2 sos reservé
- [ ] Mettre à jour les SOS, et leur description
- [ ] Changer le mot de passe, et ne pas le mettre en clair :)
- [ ] Affichage des bons SOS automatiquement sur le site wen

## API

|Endpoint|Description|Method|Query|Auth|
|---|---|---|---|---|---|
|/|Static ressources (index.html, css, etc.)|GET|||
|/api/student|Add a new SOS|POST|||
|/api/student|Get a list of the available SOS|GET|||
|/api/admin|Gather all the SOS|GET|done=[true/false]|X|
|/api/admin|Updates an SOS (eg. it is done)|PUT||X|
