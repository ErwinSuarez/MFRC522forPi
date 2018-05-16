DELIMITER $$

USE `eventDBv2`$$

DROP PROCEDURE IF EXISTS `recordToDb`$$

CREATE PROCEDURE recordToDb(IN _roomID INT, IN _uid char(30))
BEGIN
  DECLARE _timecheck timestamp;
  DECLARE _hca bool;
  DECLARE _hsk bool;
  DECLARE _flag bool;
  DECLARE _roomStatus bool;
  DECLARE _depID int;
  DECLARE _dep_code char(6);
  DECLARE _isRecordEXISTS bool;
  DECLARE _isAuthorized bool;
  DECLARE _isDepExists bool;
  
  SET _timecheck = (SELECT NOW());
  SET _flag = false;
  SET _depID = (SELECT depID FROM emps WHERE uid = _uid LIMIT 1);
  SET _roomStatus = false;
  SET _isRecordEXISTS = (SELECT EXSITS(SELECT * FROM availability WHERE roomID = _roomID ORDER BY IF DESC LIMIT 1));
  SET _isAuthorized = false;
  SET _isDepExists = (SELECT EXISTS(SELECT * FROM deps WHERE depID = _depID));
  
  SET _hsk = false;
  SET _roomStatus = false;
  SET _hca = false;
  
  IF _isDepExists = false THEN
    SET _depID = 0;
    INSERT INTO records(roomID,uid,timecheck,depID,flag,auth) VALUES(_roomID,_uid,_timecheck,_depID,_flag,_isAuthorized);
    
  ELSEIF _isDepExists = true THEN
    SET _isAuthorized = true
    INSERT INTO records(roomID,uid,timecheck,depID,flag,auth) VALUES(_roomID,_uid,_timecheck,_depID,_flag,_isAuthorized);
    
    IF _isRecordEXISTS THEN
      SET _hsk = (SELECT hsk FROM availability WHERE roomID = _roomID ORDER BY ID DESC LIMIT 1);
      SET _roomStatus = (SELECT roomStatus FROM availability WHERE roomID = _roomID ORDER BY ID DESC LIMIT 1);
      SET _hca = (SELECT hca FROM availability WHERE roomID = _roomID ORDER BY ID DESC LIMIT 1);
      
    IF _depID = 1 THEN  -- department HCA depID 1
      SET _hca = true;
      IF _hsk = true THEN
        SET _roomStatus = true;
      END IF;
    
    ELSE IF _depID = 2 THEN  -- department HSK depID 2
      SET _hsk = true;
      IF _hca = true THEN
        SET _roomStatus = true;
      END IF;
    END IF;
    
    INSERT INTO availability(roomID,hca,hsk,timecheck,roomStatus) VALUES(_roomID,_hca,_hsk,_timecheck,_roomStatus);
    
    IF _hsk = true AND _hca = true AND roomStatus = true THEN
      SET _hsk = false;
      SET _hca = false;
      SET _roomStatus = false;
      SET _timecheck = (SELECT NOW());
      INSERT INTO availability(roomID,hca,hsk,timecheck,roomStatus) VALUES(_roomID,_hca,_hsk,_timecheck,_roomStatus);
    END IF;

    ELSE
      IF _depID = 1 THEN  -- department HCA depID 1
        SET _hca = true;
      ELSEIF _depID = 2 THEN  -- department HSK depID 2
        SET _hsk = true;
      END IF;
      
      INSERT INTO availability(roomID,hca,hsk,timecheck,roomStatus) VALUES(_roomID,_hca,_hsk,_timecheck,_roomStatus);
    END IF;
  END IF;
END $$
DELIMITER;
