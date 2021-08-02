import cassiopeia as cass
import roleml

import json
from datetime import timedelta
import time
from collections import Counter

import csv
from csv import writer



def getInfo(match, summoner):
    p = match.participants[summoner]
    
    roleml.change_role_formatting('full')
    match.timeline.load()
    
    d_spell = spellList[str(p.summoner_spell_d.id)]  
    f_spell = spellList[str(p.summoner_spell_f.id)]  

    result = p.team.win

    return d_spell, f_spell, result

def get_challenger_data():
    data= cass.get_challenger_league(cass.Queue.ranked_solo_fives) #get the challenger data
    
    d_spells = []
    f_spells = []
    results = []

    for item in data.entries:
        if data.entries.index(item) %10 ==0:
            #print every 10 entries to update user
            print('\nCURRENT LADDER ENTRY= ', data.entries.index(item))
        elif data.entries.index(item)>250:
            pass
        else:
            summoner= item.summoner
            match_history = summoner.match_history(queues={cass.Queue.ranked_solo_fives}, 
                                            begin_index=0, end_index=1)
            for match in match_history:
                if match.is_remake:
                    pass
                elif match.duration < timedelta(minutes=15, seconds= 30):
                    # skip ff at 15
                    pass
                else:
                    #now we want the role [top, mid, jg, adc, support] and champion
                    #keep track of each one per match to find most common
                    dSpell, fSpell, res= getInfo(match,summoner)
                    d_spells.append(dSpell)
                    f_spells.append(fSpell)
                    results.append(res)
            
            
    return d_spells, f_spells, results

def write_output(dspells, fspells, results):
    #summoner name, (role, games), (champ, games)
    print("\nd spell, f spell, result")
    for i in range(0,len(dspells)):
        print(dspells[i],"//", fspells[i], '//', results[i])

#%% Main run                 
if __name__ == "__main__":
    start_time = time.time()
    
    cass.set_riot_api_key('REDACT')
    cass.set_default_region('JP')
    
    with open('spellsFull.json', 'r') as spellList_file:
        spellList = json.load(spellList_file)
        spellList_file.close()
        spellList= spellList['keys']
    
    d, f, r = get_challenger_data()
    write_output(d, f, r)

    rows = []
    
    for x in range(len(d) -1):
        rows.append([d[x], f[x], r[x]])

    with open('spell_infoJP.csv', 'w', newline= '') as dfspells_file:
        writer = csv.writer(dfspells_file)
        writer.writerow(['d_spell', 'f_spell', 'result'])
        for item in rows:
            writer.writerow(item)
    
    print("\n--- %s seconds ---" % (time.time() - start_time))


