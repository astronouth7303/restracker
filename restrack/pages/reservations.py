# -*- tab-width: 4; use-tabs: 1; coding: utf-8 -*-
# vim:tabstop=4:noexpandtab:
"""
Stuff dealing with reservations.
"""
from restrack.web import page, template, HTTPError, ActionNotAllowed
from restrack.utils import struct, result2obj, first, itercursor
from events import Event
from users import User

class Reservation(struct):
	__fields__ = ('rid', 'timebooked', 'starttime', 'endtime', 'roomnum', 
		'building', 'semail', 'aemail', 'eid')
	
	def start(self):
		"""Format and return the start time."""
		FMT = "%m-%d-%Y %I:%M%p"
		return self.starttime.strftime(FMT)
	
	def end(self):
		"""Format and return the end time."""
		FMT = "%m-%d-%Y %I:%M%p"
		return self.endtime.strftime(FMT)
	
	def format(self):
		"""Format the reservation."""
		DFMT = "%m-%d-%Y "
		TFMT = "%I:%M%p"
		
		st = self.starttime.strftime(DFMT+TFMT)
		en = self.endtime.strftime(DFMT+TFMT)
		
		# If on the same day, print the date once
		if self.starttime.date() == self.endtime.date():
			en = self.endtime.strftime(TFMT)
		
		rv = '%s to %s: ' % (st, en)
		if hasattr(self, 'displayname'): # room info loaded
			from rooms import Room
			rv += Room(**self.__dict__).display
		else:
			rv += '%s %s' % (self.building, self.roomnum)
		return rv

@page(r'/event/(\d+)/reservation')
def index(req, eid):
	"""Format the reservation page."""
	try:
		eid = int(eid)
	except:
		raise HTTPError(404)
	
	cur = req.execute("SELECT * FROM event WHERE eid=%(id)i", id=eid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	event = first(result2obj(cur, Event))
	#find conflicts
	cur = req.execute("""
SELECT * FROM reservation NATURAL LEFT OUTER JOIN (
		SELECT COUNT(against) AS conflicts, rid
			FROM resconflicts NATURAL JOIN reservation 
			WHERE EID=%(event)i 
			GROUP BY rid
		) AS conflicting NATURAL LEFT OUTER JOIN room
	WHERE reservation.eid = %(event)i
	ORDER BY starttime""", event=eid)
	reservations = list(result2obj(cur, Reservation))
	
	return template(req, 'reservation-list', event=event, reservations=reservations)

@page(r'/event/(\d+)/reservation/(\d+)')
def details(req, eid, rid):
	"""Details page for a specific reservation."""
	try:
		eid = int(eid)
		rid = int(rid)
	except:
		raise HTTPError(404)
	
	cur = req.execute("SELECT * FROM reservation NATURAL JOIN room WHERE rid=%(r)i", r=rid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	resv = first(result2obj(cur, Reservation))
	
	if resv.eid != eid:
		raise HTTPError(404)
	
	cur = req.execute("SELECT * FROM event WHERE eid=%(e)i", e=eid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	event = first(result2obj(cur, Event))
	
	cur = req.execute("""SELECT * 
	FROM resconflicts NATURAL JOIN reservation NATURAL JOIN room 
	WHERE against=%(r)i
	ORDER BY starttime""", r=rid)
	confs = list(result2obj(cur, Reservation))
	
	return template(req, 'reservation', reservation=resv, event=event, conflicts=confs)

@page(r'/event/(\d+)/reservation/(\d+)/edit', mustauth=True, methods=['GET','POST'])
def edit(req, eid, rid):
	"""Edit a specific reservation."""
	try:
		eid = int(eid)
		rid = int(rid)
	except:
		raise HTTPError(404)
	
	cur = req.execute("SELECT * FROM reservation NATURAL JOIN room WHERE rid=%(r)i", r=rid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	resv = first(result2obj(cur, Reservation))
	
	if resv.eid != eid:
		raise HTTPError(404)
	
	cur = req.execute("SELECT * FROM event WHERE eid=%(e)i", e=eid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	event = first(result2obj(cur, Event))
	
	if not (req.user == resv.semail or req.issuper()):
		raise ActionNotAllowed
	
	post = req.post()
	if post:
		raise NotImplementedError
	
	return template(req, 'reservation-edit', event=event, reservation=resv)

@page(r'/event/(\d+)/reservation/(\d+)/approve', mustauth=True, methods=['GET','POST'])
def approve(req, eid, rid):
	"""Approve an event with conflict checking."""
	try:
		eid = int(eid)
		rid = int(rid)
	except:
		raise HTTPError(404)
	
	if not req.isadmin():
		raise ActionNotAllowed
	
	cur = req.execute("SELECT * FROM reservation NATURAL JOIN room WHERE rid=%(r)i", r=rid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	resv = first(result2obj(cur, Reservation))
	
	if resv.eid != eid:
		raise HTTPError(404)
	
	cur = req.execute("SELECT * FROM event WHERE eid=%(e)i", e=eid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	event = first(result2obj(cur, Event))
	
	cur = req.execute("""SELECT * 
	FROM resconflicts NATURAL JOIN reservation NATURAL JOIN room 
	WHERE against=%(r)i
	ORDER BY starttime""", r=rid)
	confs = list(result2obj(cur, Reservation))
	
	post = req.post()
	if post and not resv.aemail:
		# in 2.5, we could just use any()/all()
		canapprove = True
		for c in confs:
			if c.aemail:
				canapprove = False
				break
		
		if 'yes' in post and canapprove:
			cur = req.execute(
				"UPDATE reservation SET aemail=%(a)s WHERE rid=%(r)i",
				a=req.user, r=rid)
			assert cur.rowcount
			
		req.status(303)
		req.header('Location', req.fullurl('/event/%i/reservation/%i'%(eid,rid)))
		return
	
	return template(req, 'reservation-approve', event=event, reservation=resv, 
		conflicts=confs)

@page(r'/event/(\d+)/reservation/(\d+)/delete', mustauth=True, methods=['GET','POST'])
def delete(req, eid, rid):
	"""Delete a reservation from the database."""
	try:
		eid = int(eid)
		rid = int(rid)
	except:
		raise HTTPError(404)
	
	if not req.isadmin():
		raise ActionNotAllowed
	
	cur = req.execute("SELECT * FROM reservation NATURAL JOIN room WHERE rid=%(r)i", r=rid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	resv = first(result2obj(cur, Reservation))
	
	if resv.eid != eid:
		raise HTTPError(404)
	
	cur = req.execute("SELECT * FROM event WHERE eid=%(e)i", e=eid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	event = first(result2obj(cur, Event))
	
	cur = req.execute(
		"SELECT COUNT(*) FROM runby WHERE eid=%(e)i AND cemail=%(c)s", 
		e=eid, c=req.user)
	isclub = first(itercursor(cur))[0]
	
	# running groups, booking user, admin
	if not (isclub or req.user == resv.semail or req.isadmin()):
		raise ActionNotAllowed
	
	post = req.post()
	if post:
		if 'yes' in post:
			cur = req.execute(
				"DELETE reservation WHERE rid=%(r)i", r=rid)
			assert cur.rowcount
			req.status(303)
			req.header('Location', req.fullurl('/event/%i'%eid))
		else:
			req.status(303)
			req.header('Location', req.fullurl('/event/%i/reservation/%i'%(eid,rid)))
		return
		
	return template(req, 'reservation-delete', event=event, reservation=resv)

@page(r'/event/(\d+)/reservation/create', mustauth=True, methods=['GET','POST'])
def create(req, eid):
	"""Create a new reservation."""
	try:
		eid = int(eid)
	except:
		raise HTTPError(404)
	
	if not (req.isstudent() or req.issuper()):
		raise ActionNotAllowed
	
	cur = req.execute("SELECT * FROM event WHERE eid=%(id)i", id=eid)
	if cur.rowcount == 0:
		raise HTTPError(404)
	event = first(result2obj(cur, Event))
	
	cur = req.execute(
		"SELECT * FROM runBy NATURAL JOIN clubusers WHERE eid=%(id)i ORDER BY name", 
		id=eid)
	clubs = list(result2obj(cur, User))
	
	if not (req.inclub(c.cemail for c in clubs) or req.issuper()):
		raise ActionNotAllowed
	
	post = req.post()
	if post:
		if req.issuper():
			semail = post['semail']
		else:
			semail = req.user
		
		building = post['building']
		roomnum = post['roomnum']
		#FIXME: Parse datetimes
		st = post['starttime']
		et = post['endtime']
		
		cur = req.execute("""INSERT INTO reservation 
			(eid, semail, timebooked, starttime, endtime, roomnum, building)
			VALUES
			(%(e)i, %(s)s, NOW(), %(st)s, %(et)s, %(rn)s, %(build)s)
			RETURNING rid""", e=eid, s=semail, st=st, et=et, rn=roomnum, 
			build=building)
		assert cur.rowcount
		rid = first(itercursor(cur))[0]
		
		req.status(303)
		req.header('Location', req.fullurl('/event/%i/reservation/%i' % (eid, rid)))
	
	query = req.query()
	building = query.get('building', None)
	roomnum = query.get('roomnum', None)
	st = query.get('starttime', None)
	et = query.get('endtime', None)
	
	return template(req, 'reservation-create', event=event, 
		building=building, roomnum=roomnum, starttime=st, endtime=et)

@page(r'/reservations')
def index(req):
	"""Creates an index page for reservations."""
	cur = req.execute("""SELECT reservation.*, event.name FROM reservation NATURAL JOIN event WHERE aEmail IS NULL AND startTime > now() ORDER BY startTime;""")
	reservations = list(result2obj(cur, Reservation))

	return template(req, 'unapproved-reservations', reservations=reservations)

