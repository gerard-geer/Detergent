Detergent
=========

It turns out that remaking things using new things is a great way to learn things.
This is a casual remake of SOAP that follows slightly different and unconsulted design ideas.

Features
--------
* Playlists! No longer will you have to find a 10 minute song so that you can have music for the
  duration of your shower.
* Persistence! Those playlists are even saved for you!
* iButton interactivity! Start and stop your playlist with a flick of the wrist. Shower sniping is a
  thing of the past.
* Scalability! Each shower can have its own audio without any weird channel division and whatnot.
* Less sketchiness! I don't know how the old SOAP broke so often.

Client
------
The SOAP shower client is simply a Pi with an iButton reader.

More specifically it is a Python script that waits on iButton reads. When an iButton is read, the ID
is used to retrieve the user's playlist. The playlist--which is just a list of URLs--is then dumped 
into a helper thread that force feeds it into SoX, a hella-robust audio player.

Server
------
The server is me learning Node.js, and hosts a web interface and listens for users to POST new playlists.
When a playlist is received it is given to a local Redis store, keyed to the user's username.

Dependencies
------------
Client:
* Py-Redis
* CSHLDAP

Server (Just use the install script):
* Node-Redis (Preferably with the HiRedis parser)
* Cookies (A Cookie interface)
* Node-krb5 (Shit nasty yo)


