import re
import pandas as pd
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
translator_donation = {
    'g': 'FoodDonation',
    'b': 'IndustryDonation',
    'w': 'CultureDonation',
    'B': 'InformationDonation',
    'T': 'BiotechDonation',
    'Y': 'EnergyDonation',
    'U': 'HypertechDonation',
    '*': 'ShipDonation',
    '$': 'ScoreDonation',
    's': 'ArbitarySmallDonation',
    'L': 'ArbitaryBigDonation',
    'A': 'WildBigDonation',
    'a': 'WildSmallDonation',
    'J': 'JungleDonation',
    'D': 'DesertDonation',
    'W': 'WaterDonation',
    'I': 'IceDonation',
    'N': 'ArbitraryWorldDonation',
    'F': 'FleetDonation'
}
def factory_gen(fac):
    input=re.match('.*(?=➪|→)',fac).group()
    input_items={
                }
    output_items={
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
                    
    output=re.search('(?=➪|→).+',fac).group()[1:]
    if re.search('\+',output):
        output_no_donation=re.search('.*(?=\+)',output).group()
        output_donation=re.search('(?=\+).*',output).group()[1:]
        for i in output_donation:
            matched = False
            for key in translator_donation.keys():
                if i==key:
                    output_items[translator_donation[key]] = output_items.get(translator_donation[key], 0) + 1
                    matched = True
                    break                      
            if not matched:
                raise NameError(f'i=={i},{fac}')
    else:
        output_no_donation=output
    for i in output_no_donation:
        matched = False
        for key in translator.keys():
            if i==key:
                output_items[translator[key]] = output_items.get(translator[key], 0) + 1
                matched = True
                break                      
        if not matched:
            raise NameError(f'i=={i},{fac}')
    return output_items,input_items

def factory_from_csv(fac):
    factory={}
    factory["name"]=f'{fac['Faction']}_{fac['Front Name']}'
    output_items,input_items=factory_gen(fac['Front Factory'])
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
    factory['feature']['properties']['upgrade_cost']=upgrade

    back_factory={}
    back_factory["name"]=f'{fac['Faction']}_{fac['Back Name']}'
    output_items,input_items=factory_gen(fac['Back Factory'])
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