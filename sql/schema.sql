PRAGMA foreign_keys = ON;

CREATE TABLE users(
  username VARCHAR PRIMARY KEY NOT NULL CHECK(length(username) <= 20),
  fullname VARCHAR NOT NULL CHECK(length(fullname) <= 40),
  email VARCHAR NOT NULL CHECK(length(email) <= 40),
  filename VARCHAR NOT NULL CHECK(length(filename) <= 64),
  password VARCHAR NOT NULL CHECK(length(password) <= 256),
  created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE posts(
    postid INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR NOT NULL CHECK(length(filename) <= 64),
    owner VARCHAR NOT NULL CHECK(length(owner) <= 20),
    created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE
);

CREATE TABLE following(
    follower VARCHAR NOT NULL CHECK(length(follower) <= 20),
    followee VARCHAR NOT NULL CHECK(length(followee) <= 20),
    created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(follower, followee),
    FOREIGN KEY(follower) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY(followee) REFERENCES users(username) ON DELETE CASCADE
);


CREATE TABLE comments(
  commentid INTEGER PRIMARY KEY AUTOINCREMENT,
  owner VARCHAR NOT NULL CHECK(length(owner) <= 20),
  postid INTEGER,
  text VARCHAR NOT NULL CHECK(length(text) <= 1024),
  created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE,
  FOREIGN KEY(postid) REFERENCES posts(postid) ON DELETE CASCADE
);

CREATE TABLE likes(
  likeid INTEGER PRIMARY KEY AUTOINCREMENT,
  owner VARCHAR NOT NULL CHECK(length(owner) <= 20),
  postid INTEGER, 
  created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(owner) REFERENCES users(username) ON DELETE CASCADE,
  FOREIGN KEY(postid) REFERENCES posts(postid) ON DELETE CASCADE
);