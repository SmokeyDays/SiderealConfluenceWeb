import re

translator = {
    'g': 'Food',
    'b': 'Industry',
    'w': 'Culture',
    'B': 'Information',
    'T': 'Biotech',
    'Y': 'Energy',
    'U': 'Hypertech',
    '*': 'Ship',
    '$': 'Score',
    's': 'ArbitarySmall',
    'L': 'ArbitaryBig',
    'A': 'WildBig',
    'a': 'WildSmall',
    'J': 'Jungle',
    'D': 'Desert',
    'W': 'Water',
    'I': 'Ice',
    'N': 'ArbitraryWorld',
    'F': 'Fleet'
}

def factory_gen(fac):
    input=re.match('.*(?=➪|→)',fac).group()
    input_items={
                    "Food": 0,
                    "Culture": 0,
                    "Industry": 0,
                    "Information": 0,
                    "Biotech": 0,
                    "Energy": 0,
                    "Hypertech": 0,
                    "Ship": 0,
                    "Score": 0
                }
    output_items={
                "Food": 0,
                "Culture": 0,
                "Industry": 0,
                "Information": 0,
                "Biotech": 0,
                "Energy": 0,
                "Hypertech": 0,
                "Ship": 0,
                "Score": 0
            }
    donation_items={
                "Food": 0,
                "Culture": 0,
                "Industry": 0,
                "Information": 0,
                "Biotech": 0,
                "Energy": 0,
                "Hypertech": 0,
                "Ship": 0,
                "Score": 0
            }
    for i in input:
        matched = False
        for key in translator.keys():
            if i==key:
                input_items[translator[key]] = input_items.get(translator[key], 0) + 1
                matched = True
                break                      
        if not matched:
            raise NameError(f'i=={i},{fac}')
            #print(input_items)
            
    output=re.search('(?=➪|→).+',fac).group()[1:]
    if re.search('\+',output):
        output_no_donation=re.search('.*(?=\+)',output).group()
        output_donation=re.search('(?=\+).*',output).group()[1:]

        for i in output_no_donation:
            if i =='g':
                output_items['Food'] = output_items.get('Food',0) + 1
            elif i =='b':
                output_items['Industry']+=1
            elif i=='w':
                output_items["Culture"]+=1
            elif i=='B':
                output_items['Information']+=1
            elif i=='T':
                output_items['Biotech']+=1
            elif i=='Y':
                output_items['Energy']+=1
            elif i=='U':
                output_items['Hypertech']+=1
            elif i=="*":
                output_items['Ship']+=1
            elif i=='$':
                output_items['Score']+=1
            elif i=='A':
                if 'WildBig' in output_items.keys():
                    output_items['WildBig']+=1
                else:
                    output_items['WildBig']=1                    
            elif i=='a':
                if 'WildSmall' in output_items.keys():
                    output_items['WildSmall']+=1
                else:
                    output_items['WildSmall']=1   
            elif i=='J':
                output_items['jungle']=1
            elif i=='D':
                output_items['desert']=1
            elif i=='W':
                output_items['water']=1
            elif i=='I':
                output_items['ice']=1      
            else:  
                 raise NameError(f'i=={i},{fac}')
        for i in output_donation:
            if i =='g':
                donation_items['Food']+=1
            elif i =='b':
                donation_items['Industry']+=1
            elif i=='w':
                donation_items["Culture"]+=1
            elif i=='B':
                donation_items['Information']+=1
            elif i=='T':
                donation_items['Biotech']+=1
            elif i=='Y':
                donation_items['Energy']+=1
            elif i=='U':
                donation_items['Hypertech']+=1
            elif i=="*":
                donation_items['Ship']+=1
            elif i=='$':
                donation_items['Score']+=1
            elif i=='A':
                if 'WildBig' in donation_items.keys():
                    donation_items['WildBig']+=1
                else:
                    donation_items['WildBig']=1                    
            elif i=='a':
                if 'WildSmall' in donation_items.keys():
                    donation_items['WildSmall']+=1
                else:
                    donation_items['WildSmall']=1    
            elif i=='J':
                donation_items['jungle']=1
            elif i=='D':
                donation_items['desert']=1
            elif i=='W':
                donation_items['water']=1
            elif i=='I':
                donation_items['ice']=1   
            else:
                raise NameError(f'i=={i},{fac}')
    else:
        output_no_donation=output
        for i in output_no_donation:
            if i =='g':
                output_items['Food']+=1
            elif i =='b':
                output_items['Industry']+=1
            elif i=='w':
                output_items["Culture"]+=1
            elif i=='B':
                output_items['Information']+=1
            elif i=='T':
                output_items['Biotech']+=1
            elif i=='Y':
                output_items['Energy']+=1
            elif i=='U':
                output_items['Hypertech']+=1
            elif i=="*":
                output_items['Ship']+=1
            elif i=='$':
                output_items['Score']+=1     
            elif i=='A':
                if 'WildBig' in output_items.keys():
                    output_items['WildBig']+=1
                else:
                    output_items['WildBig']=1                    
            elif i=='a':
                if 'WildSmall' in output_items.keys():
                    output_items['WildSmall']+=1
                else:
                    output_items['WildSmall']=1      
            else:
                raise NameError(f'i=={i},{fac}')
    return output_items,donation_items,input_items
    import pandas as pd
def factory_from_csv(fac):
    factory={}
    factory["name"]=f'{fac['Faction']}_{fac['Front Name']}'
    output_items,donation_items,input_items=factory_gen(fac['Front Factory'])
    factory["output_items"]=output_items
    factory['input_items']=input_items
    factory['donation_items']=donation_items
    factory['input']=float(fac['Input'])
    factory['output']=fac['Front Output']
    factory['efficiency']=fac['Front Efficiency']
    factory['feature']={}
    factory['feature']['type']='Normal'
    factory['feature']['properties']={}
    factory['feature']['properties']['upgraded']=False
    factory['feature']['properties']['upgrade_factory']=f'{fac['Faction']}_{fac['Back Name']}'
    upgrade=[]
    upgrade.append(f'{fac['Faction']}_{fac['Upgrade2']}')
    if re.search('→',fac['Upgrade1']):
        upgrade_substance={}
        output_items,donation_items,input_items=factory_gen(fac['Upgrade1'])
        upgrade_substance['input_items']=input_items
        upgrade_substance['output_items']=output_items
        upgrade.append(upgrade_substance)
    else:
        upgrade.append(f'{fac['Faction']}_{fac['Upgrade1']}')
    factory['feature']['properties']['upgrade_requirements']=upgrade

    back_factory={}
    back_factory["name"]=f'{fac['Faction']}_{fac['Back Name']}'
    output_items,donation_items,input_items=factory_gen(fac['Back Factory'])
    back_factory["output_items"]=output_items
    back_factory['input_items']=input_items
    back_factory['donation_items']=donation_items
    back_factory['input']=float(fac['Input'])
    back_factory['output']=fac['Back Output']
    back_factory['efficiency']=fac['Back Efficiency']
    back_factory['feature']={}
    back_factory['feature']['type']='Normal'
    back_factory['feature']['properties']={}
    back_factory['feature']['properties']['upgraded']=True

    return factory,back_factory


a=pd.read_csv('工作簿1.csv')
import json

factory_list=[]
for i in range(395):
    bac=a.loc[i]
    if bac['Faction']=='艾恩卓尔' and (bac['Cost']=='Starting' or bac['Cost']=='Researched'):
        #print(bac)
        try:
            fact,backfact=factory_from_csv(bac)
        except:
            print(bac)
            raise
        factory_list.append(fact)
        factory_list.append(backfact)
with open('Caylion_fac.json','w') as f:
    string=json.dumps(factory_list,ensure_ascii=False)
    f.write(string)