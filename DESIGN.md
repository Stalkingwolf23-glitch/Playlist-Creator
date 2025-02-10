# Design Document

By Lucas Leong

Video Link: https://www.youtube.com/watch?v=dUjiGmLVC2E

## Scope
This project enables the user to search for songs on the Spotify database through the use of their complex genre system to find the songs that they might be interested in listening to. As such, included in the database's scope is:

* User, where the account details of each user is stored in, with the password being encrypted using the werkzeug security library in Python
* Playlists, where a list of playlists are stored, with foreign keys linking back to the user table to enable the search and specificiation of each user's playlist
* Songs, where the songs added to playlists are stored in, with foreign keys linking back to both the user and playlists table. This allows a more granular search approach and also allows the same song to be added for the same user or multiple users without any clashing.
* Genres, a built-in list of genres to help and enable users for finding whatever genre they seek. The list is sourced from https://github.com/Scottsdaaale/List-of-All-Spotify-Genres

## Functional Requirements
The database will support:

* Search of genres that interests the user
* Creation of multiple playlists for specific needs
* Storing and listing playlists contents

## Representation
Entities are captured in SQLite tables with the following schema.

### Entities
The database includes the following entities:

### Users
The `users` table includes:

* `id`, which specifies the unique ID for the user as an `INTEGER`. This column has the `PRIMARY KEY` constraint applied.
* `password`, which specifies the password chosen by the user and encrypted using the scrypt hashing algorithm done before the account details is logged into the database. `TEXT` is appropriate for this as the hashing outcome can be varied and using `TEXT` as a catchall will minimize any possible errors.
* `username`, which specifies the username chosen by the user and is stored as plaintext. `TEXT` is used here as well since the chosen username can come in various forms and `TEXT` has less rigorous conditions.

### Playlists
The `playlists` table includes:

* `id`, as per the `users` table, it allows a unique ID for each playlist to be made and uses `INTEGER`. This column has the `PRIMARY KEY` constraint applied.
* `name`, which specifies a name chosen by the user for their playlist. Uses `TEXT` to allow freedom for the user to name their playlist however they wish to.
* `user_id`, which specifies the unique ID of the user that made this playlist, uses `INTEGER` as per all the other unique IDs. This column is a `FOREIGN KEY` linked to `id` of the `users` table. Additionally, has the `ON DELETE CASCADE` clause to facilitate ease of function if the user `id` that this is linked to is deleted.

### Songs
The `songs` table includes:

* `id`, as per the previous entities, it allows for a unique ID so that the song can be easily referenced to when trying to find the one belonging to the right playlist. It uses `INTEGER` and has the `PRIMARY KEY` constraint applied.
* `name`, which specifies the name of the song, uses `TEXT` as song names generally use alphabetical characters but it can also include other types of characters.
* `playlist_id`, which specifies the unique `id` of the playlist that this song is in. Uses `INTGEGER` as per all the other unique IDs. This column is a `FOREIGN KEY` linked to `id` of the `playlist` table. Additionally, has the `ON DELETE CASCADE` clause to facilitate ease of function if the user `id` that this is linked to is deleted.
* `user_id`, which specifies the unique ID of the user that made this playlist, uses `INTEGER` as per all the other unique IDs. This column is a `FOREIGN KEY` linked to `id` of the `users` table. Additionally, has the `ON DELETE CASCADE` clause to facilitate ease of function if the user `id` that this is linked to is deleted.

### Genres
The `genres` table includes:

* `id`, as per the previous entities, it allows for a unique ID so that the desired genre can be easily referenced to when selecting genres. It uses `INTEGER` and has the `PRIMARY KEY` constraint applied.
* `genre`, which specifies a list of genres that the user can use to search for songs in the spotify database, uses `TEXT` to accomodate for the alphabetical and any special characters that the genre would use.

## Relationships
The below entity relationship diagram describes the relationships among the entities in the database.

![ER Diagram](diagram.png)

As detailed by the diagram:

* One user can have 0 to many playlists. 0 if the user has yet create a playlist, many if the user has created two or more playlists. A playlist can only belong to one user and it is impossible for a playlist to belong to more than one user.
* One playlist can have 0 to many songs. 0 if the user has yet to add a song to the playlist, many if the user has added two or more songs. A song can belong to many playlist if the user creates multiple playlists and adds the same song to those playlists.
* One to many songs can have one to many genres. One if the genre only contains a single song, many if the genre has two or more songs. A song can have a single genre or it can have two more genres at once.

## Limitations

The current database does not support hosting every song data and inserting said songs into the appropriate tables as spotify's song database gets updated constantly.