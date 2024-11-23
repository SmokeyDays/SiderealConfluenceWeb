import os
import re
import pandas as pd
import json
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
    'F': 'Fleet',
    'Z': 'ZethEnvoy',
    'R': 'RelicWorld',
}
ignore_items = ['X']
converter_stage = {
    '➪': 'production',
    '→': 'trading',
    '➾': 'stealing',
    '↺': 'constant'
}
def arrow_pattern():
    res = ''
    for arrow in converter_stage.keys():
        res += arrow + '|'
    return res[:-1]
other_specie_info = {
    'Caylion': {
        "zh_name": "凯利安",
        "max_colony": 3,
        "tie_breaker": 1,
        "init_colony": 1,
        "init_research": 0,
    },
    'Eni': {
        "zh_name": "恩尼艾特",
        "max_colony": 3,
        "tie_breaker": 3,
        "init_colony": 1,
        "init_research": 0,
    },
    'Im': {
        "zh_name": "艾恩卓尔",
        "max_colony": 0,
        "tie_breaker": 8,
        "init_colony": 0,
        "init_research": 1,
    },
    'Unity': {
        "zh_name": "联合体",
        "max_colony": 1,
        "tie_breaker": 4,
        "init_colony": 1,
        "init_research": 1,
    },
    'Yengii': {
        "zh_name": "岩基艾",
        "max_colony": 3,
        "tie_breaker": 6,
        "init_colony": 1,
        "init_research": 1,
    },
    'Kjasjavikalimm': {
        "zh_name": "贾斯",
        "max_colony": 6,
        "tie_breaker": 6,
        "init_colony": 2,
        "init_research": 0,
    },
    'Kit': {
        "zh_name": "凯特",
        "max_colony": 999,
        "tie_breaker": 999,
        "init_colony": 1,
        "init_research": 1,
    },
    'Zeth': {
        "zh_name": "泽思",
        "max_colony": 3,
        "tie_breaker": 2,
        "init_colony": 0,
        "init_research": 1,
    },
    'Faderan': {
        "zh_name": "法德澜",
        "max_colony": 4,
        "tie_breaker": 7,
        "init_colony": 1,
        "init_research": 1,
    }
}
MustLend = ['文化包容', '志愿医疗运动', '相互理解', '长者的智慧', '跨文化档案', '异种科技库', '全向文化动态包容', '全民健康', '种族间共情', '永生者的智慧', '泛在文化影响', '超科技共同体']
EnietInterest = ['文化包容', '志愿医疗运动', '相互理解', '长者的智慧', '跨文化档案', '全向文化动态包容', '全民健康', '种族间共情', '永生者的智慧', '泛在文化影响']
FaderanRelicWorld = ['杜伦泰的赠礼', '关联集成存储器', '自动化运输网络', '遗迹探测器', '隐德莱希图书馆', '嬗变性分解器', '纳尔戈里安磨盘', '晨星废墟', '乐土转换器', '巴里安贸易舰队', '瑟尔的碎环', '雄伟浑天仪']

def analyze_items(item_str, donation = False):
    if item_str.endswith(' §'):
        item_str = item_str[:-2]
    item = {}

    pattern = re.compile(r'(\D\d+|\D)')
    matches = pattern.findall(item_str)
    for m in matches:
        if len(m) == 1:
            i, count = m, 1
        else:
            i, count = m[0], int(m[1:])
        if i not in translator.keys():
            if i not in ignore_items:
                raise NameError(f'i=={i}')
            continue
        real_key = translator[i] if not donation else translator[i] + 'Donation'
        item[real_key] = item.get(real_key, 0) + count

    return item

def analyze_items_with_donation(item_str):
    if not re.search('\+', item_str):
        return analyze_items(item_str)
    else:
        item_no_donation = re.search('.*(?=\+)', item_str).group()
        item_donation = re.search('(?=\+).*', item_str).group()[1:]
        return {**analyze_items(item_no_donation), **analyze_items(item_donation, donation=True)}
    

def analyze_converter(converter_str):
    if not re.search(f'({arrow_pattern()})', converter_str):
        converter_str = '↺' + converter_str
    input=re.match(f'.*(?={arrow_pattern()})',converter_str).group()
    input_items={}
    output_items={}
    if not re.search('\/', input):
        input_items = analyze_items(input)
    else:
        input_groups = input.split('/')
        input_items = []
        for input_group in input_groups:
            input_items.append(analyze_items(input_group))
    output=re.search(f'(?={arrow_pattern()}).+',converter_str).group()[1:]
    output_items = analyze_items_with_donation(output)

    arrow = re.search(f'{arrow_pattern()}',converter_str).group()
    converter = {
        "input_items": input_items,
        "output_items": output_items,
        "running_stage": converter_stage[arrow]
    }
    return converter

def analyze_converters(converters_str):
    converter_strs = converters_str.split(',')
    converters = []
    for converter_str in converter_strs:
        converters.append(analyze_converter(converter_str))
    return converters

def factory_from_csv(fac, converter_as_cost = False):
    if fac['Front Name'] in FaderanRelicWorld:
        return None, None, None
    meta_factory = None
    if converter_as_cost:
        meta_factory = {
            "name": f'{fac["Faction"]}_{fac["Front Name"]}_打出',
            "converters": analyze_converters(fac['Cost']),
            'feature': {
                'type': 'Meta',
                'properties': {
                    'unlock_factory': f'{fac["Faction"]}_{fac["Front Name"]}'
                }
            }
        }
    if re.search('Fleet Support', fac['Front Name']):
        factory = {
            'name': f'{fac["Faction"]}_{fac["Front Name"]}_{fac["s"]}',
            "converters": analyze_converters(fac['Front Factory']),
            'feature': {
                'type': 'Normal',
                'properties': {
                    'upgraded': True,
                }
            }
        }
        return factory, None, meta_factory
    if fac['Faction'] == '凯特' and not isinstance(fac['Upgrade1'], str):
        # todo
        return None, None, meta_factory
    upgrade=[]
    if isinstance(fac['Upgrade1'], str):
        if re.search('→',fac['Upgrade1']):
            upgrade_substance = analyze_converter(fac['Upgrade1'])
            upgrade.append(upgrade_substance)
        else:
            upgrade.append(f'{fac["Faction"]}_{fac["Upgrade1"]}')
    if isinstance(fac['Upgrade2'], str):
        upgrade.append(f'{fac["Faction"]}_{fac["Upgrade2"]}')
    feature = {
            'type': 'Normal',
            'properties': {
                'upgraded': False,
                'upgrade_factory': f'{fac["Faction"]}_{fac["Back Name"]}',
                'upgrade_cost': upgrade
            }
        }
    factory_str = fac["Front Factory"]
    factory_name = f'{fac["Faction"]}_{fac["Front Name"]}'
    if fac['Faction'] == 'Research':
        feature = {
            "type": "Research",
            "properties": {
              "tech": fac["Back Name"] if isinstance(fac["Back Name"], str) else '',
              "level": fac["Era"]
          }
        }
        factory_name = f'{fac["Front Name"]}'
    if fac['Faction'] == 'Colonies':
        info = factory_str.split(',')
        climate, factory_str = info[0], info[1]
        feature = {
            "type": "Colony",
            "properties": {
                "climate": climate,
                "upgraded": False,
                "upgrade_cost": analyze_converter(fac["Upgrade1"])['input_items']
            }
        }
        factory_name = f'{fac["Front Name"]}'
    factory = {
        'name': factory_name,
        'converters': analyze_converters(factory_str),
        'feature': feature
    }
    back_factory = None
    if isinstance(fac['Back Factory'], str):
        feature = {
            'type': 'Normal',
            'properties': {
                'upgraded': True
            }
        }
        back_factory_str = fac["Back Factory"]
        back_factory_name = f'{fac["Faction"]}_{fac["Back Name"]}'
        if fac['Faction'] == 'Colonies':
            info = back_factory_str.split(',')
            climate, back_factory_str = info[0], info[1]
            feature['properties']['climate'] = climate
            back_factory_name = f'{fac["Back Name"]}+'
        back_factory={
            'name': back_factory_name,
            'converters': analyze_converters(back_factory_str),
            'feature': feature
        }

    if fac['Faction'] == '恩尼艾特':
        if fac['Front Name'] in EnietInterest:
            factory['feature']['properties']['EnietInterest'] = True
            back_factory['feature']['properties']['EnietInterest'] = True
        if fac['Front Name'] in MustLend:
            factory['feature']['properties']['MustLend'] = True
            back_factory['feature']['properties']['MustLend'] = True

    return factory, back_factory, meta_factory

def deal_specie(csv_path, save_path, specie):
    specie_zh_name = other_specie_info[specie]['zh_name']
    csv_data=pd.read_csv(csv_path)
    factory_list=[]
    start_resource = {}
    start_factories = []
    for i in range(csv_data.shape[0]):
        bac=csv_data.loc[i]
        if bac['Faction']!=specie_zh_name:
            continue
        if bac['Cost']=='Starting' or bac['Cost']=='Researched' or re.search('→', str(bac['Cost']).strip()):
            try:
                factory, back_factory, meta_factory = factory_from_csv(bac, converter_as_cost = re.search('→', str(bac['Cost']).strip()))
            except:
                print(bac)
                raise
            if factory:
                factory_list.append(factory)
                if bac['Cost']=='Starting':
                    start_factories.append(factory['name'])
            if back_factory:
                factory_list.append(back_factory)
            if meta_factory:
                factory_list.append(meta_factory)
                start_factories.append(meta_factory['name'])
        if bac['Cost']=='Reference' and bac['Front Name'].startswith('Starting Race Card'):
            start_resource['items'] = analyze_items(bac['Front Factory'])
    start_resource['factories'] = start_factories

    specie_info = other_specie_info[specie]
    specie_info['name'] = specie
    specie_info['start_resource'] = start_resource
    specie_info['factories'] = factory_list
    with open(save_path + specie + '.json','w', encoding='utf-8') as f:
        string=json.dumps(specie_info, ensure_ascii=False, indent=4)
        f.write(string)

def deal_research(csv_path, save_path):
    csv_data=pd.read_csv(csv_path)
    research_list = []
    for i in range(csv_data.shape[0]):
        bac=csv_data.loc[i]
        if bac['Faction']=='Research':
            research, _, _ = factory_from_csv(bac)
            research_list.append(research)
    with open(save_path + 'researches.json','w', encoding='utf-8') as f:
        string=json.dumps(research_list, ensure_ascii=False, indent=4)
        f.write(string)

def deal_colony(csv_path, save_path):
    csv_data=pd.read_csv(csv_path)
    colony_list = []
    for i in range(csv_data.shape[0]):
        bac=csv_data.loc[i]
        if bac['Faction']=='Colonies':
            colony, back_colony, _ = factory_from_csv(bac)
            colony_list.append(colony)
            if back_colony:
                colony_list.append(back_colony)
    with open(save_path + 'colonies.json','w', encoding='utf-8') as f:
        string=json.dumps(colony_list, ensure_ascii=False, indent=4)
        f.write(string)

if __name__ == '__main__':
    for specie in other_specie_info.keys():
        deal_specie('./server/utils/raw_data.csv', './server/data/species/', specie)
    deal_research('./server/utils/raw_data.csv', './server/data/')
    deal_colony('./server/utils/raw_data.csv', './server/data/')
