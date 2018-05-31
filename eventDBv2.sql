CREATE SCHEMA IF NOT EXISTS `eventDBv2`;

USE eventDBv2;

DROP TABLE IF EXISTS `availability`;
DROP TABLE IF EXISTS `records`;
DROP TABLE IF EXISTS `emps`;
DROP TABLE IF EXISTS `deps`;
DROP TABLE IF EXISTS `rooms`;

CREATE table deps(
  depID INTEGER AUTO_INCREMENT PRIMARY KEY,
  dep_code varchar(10),
  description varchar(30)
);

CREATE table rooms(
  roomID INTEGER AUTO_INCREMENT PRIMARY KEY,
  description varchar(15)
);

CREATE table emps(
  empID INTEGER AUTO_INCREMENT PRIMARY KEY,
  uid varchar(50),
  depID INTEGER,
  CONSTRAINT FK_EmpDepID FOREIGN KEY(depID) REFERENCES deps(depID)
);

CREATE table records(
  recordID INTEGER AUTO_INCREMENT PRIMARY KEY,
  roomID INTEGER,
  uid varchar(50),
  timecheck timestamp,
  depID INTEGER,
  flag bool,
  auth bool,
  CONSTRAINT FK_RecordRoomID FOREIGN KEY(roomID) REFERENCES rooms(roomID)
);

CREATE table availalbity(
  ID INTEGER AUTO_INCREMENT PRIMARY KEY,
  roomID INTEGER,
  HCA bool,
  HK bool,
  timecheck timestamp,
  flag bool,
  roomStatus bool,
  CONSTRAINT FK_AvRoomID FOREIGN KEY(roomID) REFERENCES rooms(roomID)
);
