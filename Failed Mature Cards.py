"""
Name: Failed Mature Cards
Filename: Failed Mature Cards.py
Version: 0.4
Author: Kenishi
Desc:	Generates a new graph that shows the number of mature cards that were failed over a time period
		
		Report bugs to https://github.com/Kenishi/Failed-Mature-Cards
"""

import anki
import anki.stats
from anki.hooks import wrap, addHook

# Graph Bar Color
reviewFailC = "#DE8073"

def failingGraph(*args, **kwargs):
	self = args[0]
	old = kwargs['_old']  ### Reference back to cardGraph()
	
	if self.type == 0:
		days = 30; chunk = 1
	elif self.type == 1:
		days = 52; chunk = 7
	else:
		days = None; chunk = 30
	return old(self) + _plotFailingGraph(self, _failingCards(self,days,chunk),
							days,
							_("Failing Mature Cards"))

def _plotFailingGraph(self,data, days, title):
	if not data:
		return ""
	max_yaxis=0
	for (x,y) in data: # Unzip the data
		if y > max_yaxis:
			test = int(round((float(y)/10))*10)
			if test < y:
				max_yaxis = test + 10
			else:
				max_yaxis = test
				
	txt = self._title(_("Failed Mature Cards"),
					  _("Number of matured cards failed."))
	txt += self._graph(id="failing", data=[dict(data=data, color=reviewFailC)], conf=dict(xaxis=dict(max=0.5),yaxis=dict(min=0,max=max_yaxis)))

	return txt

def _failingCards(self, num=7, chunk=1):
	lims = []
	if num is not None:
		lims.append("id > %d" % (
			(self.col.sched.dayCutoff-(num*chunk*86400))*1000))
	lim = self._revlogLimit()
	
	if lim:
		lims.append(lim)
	if lims:
		lim = "where " + " and ".join(lims)
	else:
		lim = ""
	if self.type == 0:
		tf = 60.0 # minutes
	else:
		tf = 3600.0 # hours
	
	if lim:
		return self.col.db.all("""
SELECT
(CAST((id/1000 - :cut) / 86400.0 as int))/:chunk as day,
COUNT(*) as count
FROM revlog %s and (ivl < lastIvl and lastIvl >= 21)
GROUP BY day ORDER by day""" % lim, cut=self.col.sched.dayCutoff, tf=tf, chunk=chunk)
	else:
		return self.col.db.all("""
SELECT
(CAST((id/1000 - :cut) / 86400.0 as int))/:chunk as day,
COUNT(*) as count
FROM revlog %s WHERE (ivl < lastIvl and lastIvl >= 21)
GROUP BY day ORDER by day""" % lim, cut=self.col.sched.dayCutoff, tf=tf, chunk=chunk)		

anki.stats.CollectionStats.cardGraph = wrap(anki.stats.CollectionStats.cardGraph, failingGraph, pos="")	