# Pizzaioliste - Système de commande d'SOS

L'objectif de ce projet est de gérer la commande de SOS de la pizzaioliste durant la semaine de campagne CDP.
Cela passe par une interface web client et un serveur backend qui stocke les commandes dans une base de donnée SQLite et envoie celles-ci au serveur discord de la liste.

## Fonctionnalités

- [x] Détails de commande : prénom, nom, email, n°sos, créneau du sos, bat, turne
- [x] Vérification de la limite de 2 sos/jour/personne (via l'email du client)
- [ ] Envoie de la demande de SOS au serveur discord
- [ ] Interface web admin pour consulter la liste des SOS commandés et effectués
- [ ] Validation du SOS une fois qu'il est achevé (via discord ou l'interface web admin)
