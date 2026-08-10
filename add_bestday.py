"""Put the day of the week on the house itself.

Serhii writes to agents one house at a time, and the only thing he needs at
that moment is which day to offer. The loop already knows - the house sits in
day D, which is Thursday - so the card says so, and the message template can
be copied with the day already in it.

The mapping is read from plan.json, so it follows the loop: rebuild the plan
and every card updates with it.
"""
import pathlib

p = pathlib.Path(__file__).parent / "index.html"
s = p.read_text(encoding="utf-8")


def swap(old, new):
    global s
    assert old in s, "NOT FOUND: " + old[:110]
    s = s.replace(old, new, 1)


swap("let PLAN=null, planAsked=false;",
     """let PLAN=null, planAsked=false, DAYOF={};      // house id -> its day in the loop""")

swap("""    if(r.ok) PLAN=await r.json();
  }catch(e){}
  return PLAN;""",
     """    if(r.ok){
      PLAN=await r.json();
      (PLAN.days||[]).forEach(function(d){
        d.stops.forEach(function(st){
          DAYOF[st.id]={label:d.label, when:d.when, at:st.at,
                        week:(PLAN.week||[]).indexOf(d.label)>=0};
        });
      });
      render();
    }
  }catch(e){}
  return PLAN;""")

# ask for it once at start, not only when the plan view is opened
swap(" mark();\n if(DIRTY.size){ push().then(mark); }",
     " mark();\n loadPlan();\n if(DIRTY.size){ push().then(mark); }")

# the badge on the card
swap("""  '<div class="place"><b>'+(h.concelho||'—')+'</b>'""",
     """  (DAYOF[h.id]
    ? '<div class="bday'+(DAYOF[h.id].week?'':' later')+'">'+
      (DAYOF[h.id].week
        ? 'звать на <b>'+(DAYOF[h.id].when||('день '+DAYOF[h.id].label))+'</b>, около '+
          DAYOF[h.id].at
        : 'в круге на день '+DAYOF[h.id].label+' — эта часть отложена')+
      '</div>'
    : '')+
  '<div class="place"><b>'+(h.concelho||'—')+'</b>'""")

# and a way to see just one day's worth
swap('  <button data-f="plan">🧭 Круг</button>',
     '  <button data-f="plan">🧭 Круг</button>\n'
     '  <button data-f="thisweek">📆 Эта неделя</button>')

swap(" if(filt==='plan')return false;          // the plan draws itself",
     " if(filt==='plan')return false;          // the plan draws itself\n"
     " if(filt==='thisweek'&&!(DAYOF[h.id]&&DAYOF[h.id].week))return false;")

# the plan view names the days properly
swap("""    html+='<div class="day'+(inWeek?'':' later')+'"><div class="dh">День '+d.label+""",
     """    html+='<div class="day'+(inWeek?'':' later')+'"><div class="dh">'+
      (d.when?d.when.charAt(0).toUpperCase()+d.when.slice(1):'День '+d.label)+""")

swap(".planhead{background:var(--accent-s);border:1px solid var(--accent);",
     """.bday{font-size:12.5px;color:var(--accent);background:var(--accent-s);
 border-radius:8px;padding:4px 9px;align-self:flex-start}
.bday.later{color:var(--soft);background:transparent;border:1px solid var(--line)}
.planhead{background:var(--accent-s);border:1px solid var(--accent);""")

p.write_text(s, encoding="utf-8")
print("best day shown on every card")
