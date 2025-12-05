# Defiant Newt Intergalactic Chat

CTF réalisé par [Defiant Newt](https://defiantnewt.fr/) et [Courtcircuits](https://courtcircuit.xyz/) avec 💖.

[➡️Lien vers le challenge⬅️](https://dtn-ctf.courtcircuit.xyz)

En gros ce challenge vous permet de découvrir la vulnérabilité [React2Shell](https://react2shell.com/) qui a été découverte il y a quelques jours. En plus de ça ce chat se base sur un protocole appelé [BERMUDA](https://eprint.iacr.org/2025/806), ce protocole permet d'échanger de message chiffrés de bout-en-bout meme avec des conditions réseaux détériorées. Ce protocole a été inventé pour communiquer avec des satellites/des sous-marins. Seulement, les administrateurs du chat n'avaient qu'une nuit pour déployer cette technologie de pointe, nécessairement ils ont fait n'importe quoi. A vous de trouver les failles qui vous permettront de retrouver le flag ! Happy hacking ┌( ͝° ͜ʖ͡°)=ε/̵͇̿̿/’̿’̿ ̿

PS : le flag est en clair dans le code, pitié svp essayez de le retrouver uniquement en utilisant la RCE React2Shell et ensuite une fois que vous avez un reverse shell essayez de trouver la clé.


SI IL YA UN PROBLEME AVEC LE CHALLENGE, ENVOYEZ MOI UN MAIL à radulescutristan@proton.me.

[Vidéo de présentation + write-up du challenge](https://youtu.be/-xAcFjKJxZs)

# Write-up

## 0. Reconnaissance

-> Indice version Next
-> Websocket proposée : `ws://localhost:8000/ws`

## 1. Exécution de la RCE

```bash
$ tmux
$ nc -vlnp 80002
$ cd exploit
$ bat next_rce.py # expliquer la RCE
$ uv run next_rce.py # retourner dans le term nc
```

## 2. Private key disclosure

```
$ cat ../dtn_crypto_chat/user.py
$ ps aux | grep "python" # quitter tmux
$ uv run private_key_disclosure.py
```
Et voilà vous avez le flag !

# Remédiation

Il faut mettre à jour Next vers les versions suivantes : 15.0.5, 15.1.9, 15.2.6, 15.3.6, 15.4.8, 15.5.7, 16.0.7.
et React dans les versions suivantes : 19.0.1, 19.1.2, 19.2.1

Concernant la remédiation de la private key disclosure, toute clé privée qui ne se trouve pas dans un [HSM](https://fr.wikipedia.org/wiki/Hardware_Security_Module) ou un [keystore kernel](https://archive.fosdem.org/2024/events/attachments/fosdem-2024-3371-what-is-linux-kernel-keystore-and-why-you-should-use-it-in-your-next-application/slides/22841/keystore_VOjPH5I.pdf) peut être retrouvable par un moyen ou un autre. Le but de ce challenge était de montrer que vous avez beau faire du chiffrement de bout en bout, utiliser des protocoles qui permettent de communiquer dans l'espace, etc. Votre sécurité sera toujours aussi faible que le maillon le plus faible de votre  infrastructure (ça fait bien gamberger) ☝️🤓

