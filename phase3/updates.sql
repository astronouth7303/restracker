-- Create a room
INSERT INTO room (building, roomNum, displayName, occupancy) VALUES (%(building)s, %(room)s, %(name)s, %(size)i);

-- Change room info
UPDATE room SET displayName=%(name)s occupancy=%(size)i WHERE building=%(building)s AND roomNum=%(room)s;

-- Create a user
INSERT INTO users (email, password) VALUES (%(email)s, %(hash)s);

-- Change user email
UPDATE users SET email=%(newemail)s WHERE email=%(oldemail)s;

-- Update user information
UPDATE users SET name=%(name)s password=%(hash)s WHERE email=%(email)s;
UPDATE admin SET title=%(title)s WHERE aemail=%(email)s;
UPDATE student SET year=%(year)i major1=%(major1)s major2=%(major2)s WHERE semail=%(email)s;
UPDATE club SET description=%(desc)s class=%(cls)i WHERE cemail=%(email)s;

-- Promote a user to administrator
INSERT INTO admin (aemail, super) VALUES (%(email)s, %(super)s);

-- Set the super bit
UPDATE admin SET super=%(super)s WHERE aemail=%(email)s;

-- Make a user into a club
INSERT INTO club (cemail, description) VALUES (%(email)s, %(desc)s);

-- Make a user a student
INSERT INTO student (semail, year, major1, major2) VALUES (%(email)s, %(year)i, %(major1)s, %(major2)s);

-- Add a student to a club
INSERT INTO memberOf (semail, cemail) VALUES (%(student)s, %(club)s);

-- Add comment to an event
INSERT INTO comments (email, txt, madeat, parent) VALUES (%(email)s, %(txt)s, NOW(), %(parent)s);

-- Create an event
INSERT INTO event (name, description, expectedsize) VALUES (%(name)s, %(desc)s, %(size)s);

-- Change event info
UPDATE event SET name=%(name)s description=%(desc)s expectedsize=%(size)s WHERE EID=%(id)s;

-- Add equipment to a room
INSERT INTO isIn (equipName, quantity, building, roomNum) VALUES (%(name)s, %(num)i, %(building)s, %(room)s);

-- Change the amount of equipment in a room
UPDATE isIn SET quantity=%(num)i WHERE equipName=%(name)s AND building=%(building)s AND roomNum=%(room)s;

-- Delete equipment from a room
DELETE FROM isIn WHERE equipName=%(name)s AND building=%(building)s AND roomNum=%(room)s;

-- Add a reservation to an event
INSERT INTO reservation (semail, building, roomNum, startTime, endTime, timebooked) VALUES (%(who)s, %(building)s, %(room)s, %(start)s, %(end)s, NOW());

-- (Un)Approve a reservation
UPDATE reservation SET aemail=%(admin)s WHERE RID=%(id)s;

-- Change event info
UPDATE reservation SET starttime=%(start) endtime=%(end)s building=%(building)s roomnum=%(room)s aemail=NULL WHERE RID=%(id)s;

-- Remove a reservation from an event
DELETE FROM reservation WHERE RID=%(id)s;

-- Add a club to an event
INSERT INTO runBy (eid, cemail) VALUES (%(eid)i, %(cemail)s);

-- Remove a club from an event
DELETE FROM runBy WHERE eid=%(eid)i AND cemail=%(cemail)s;

-- Add equipment to an event
INSERT INTO uses (eid, equipname, quantity) VALUES (%(eid)i, %(equip)s, %(num)i);

-- Change amount of equipment an event uses
UPDATE uses SET quantity=%(num)i WHERE eid=%(eid)i AND equipname=%(equip)s;

-- Remove equipment from event
DELETE FROM uses WHERE eid=%(eid)i AND equipname=%(equip)s;

-- Create a session
INSERT INTO sessions (id, expires) VALUES (%(id)s, %(exp)s);

-- Change session data
UPDATE sessions SET data=%(data)s WHERE id=%(id)s;

-- Clean sessions
DELETE FROM sessions WHERE expires <= NOW();
