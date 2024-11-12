export const species = ["Caylion", "Yengii", "Im", "Eni", "Zeth", "Unity", "Faderan", "Kit", "Kjasjavikalimm"];

const specieColors: {[key: string]: string} = {
  'Caylion': 'lightgreen',
  'Yengii': 'darkblue',
  'Zeth': 'purple',
  'Im': 'lightblue',
  'Eni': 'blue',
  'Unity': 'gray',
  'Faderan': 'yellow',
  'Kit': 'orange',
  'Kjasjavikalimm': 'red',
  'None': 'white'
};

const specieZhNames: {[key: string]: string} = {
  'Caylion': '凯利安',
  'Yengii': '岩基艾',
  'Zeth': '泽思',
  'Im': '艾恩卓尔',
  'Eni': '恩尼艾特',
  'Unity': '联合体',
  'Faderan': '法德澜',
  'Kit': '凯特',
  'Kjasjavikalimm': '贾斯',
  'None': '未知'
};

export const getSpecieColor = (specie: string) => {
  if (specie in specieColors) {
    return specieColors[specie];
  }
  return 'black';
};

export const getSpecieZhName = (specie: string) => {
  if (specie in specieZhNames) {
    return specieZhNames[specie];
  }
  return '未知';
};

export const items = ["Food", "Culture", "Industry", "Energy", "Information", "Biotech", "Hypertech", "Ship", "Score","WildBig", "WildSmall", "ArbitrarySmall", "ArbitraryBig", "FoodDonation", "CultureDonation", "IndustryDonation", "EnergyDonation", "InformationDonation", "BiotechDonation", "HypertechDonation", "ShipDonation", "ScoreDonation", "WildBigDonation", "WildSmallDonation", "ArbitrarySmallDonation", "ArbitraryBigDonation"];
export const smallItem = ["Food", "Culture", "Industry"];
export const bigItem = ["Energy", "Information", "Biotech"];
export const wildSmallTarget = [...smallItem, "ArbitrarySmall"];
export const wildBigTarget = [...bigItem, "ArbitraryBig"];
export const arbitrarySmallSource = [...smallItem, "WildSmall"];
export const arbitraryBigSource = [...bigItem, "WildBig"];
export const arbitraryWorldSource = ["Jungle", "Ice", "Desert", "Water"];
const itemValues: {[key: string]: number} = {
  'Food': 1,
  'Culture': 1,
  'Industry': 1,
  'Energy': 1.5,
  'Information': 1.5,
  'Biotech': 1.5,
  'Hypertech': 3,
  'Ship': 1,
  'Score': 3,
  'WildBig': 1.5,
  'WildSmall': 1,
  'ArbitrarySmall': 1,
  'ArbitraryBig': 1.5,
}

export const getItemValue = (item: string) => {
  if (item in itemValues) {
    return itemValues[item];
  }
  return 0;
}

export const getItemsValue = (items: {[key: string]: number}) => {
  return Object.keys(items).reduce((sum, item) => sum + getItemValue(item) * items[item], 0);
}

export const getItemsDonationValue = (items: {[key: string]: number}) => {
  return Object.keys(items).reduce((sum, item) => {
    if (item.endsWith('Donation')) {
      return sum + getItemValue(item.replace('Donation', '')) * items[item];
    }
    return sum;
  }, 0);
}

const itemZhNames: {[key: string]: string} = {
  'Food': '食物',
  'Culture': '文化',
  'Industry': '工业',
  'Energy': '能源',
  'Information': '信息',
  'Biotech': '生物科技',
  'Hypertech': '超科技',
  'Ship': '飞船',
  'Score': '分数',
  'WildBig': '大型万能方块',
  'WildSmall': '小型万能方块',
  'ArbitrarySmall': '小型任意',
  'ArbitraryBig': '大型任意',
  'Ice': '冰川殖民地',
  'Jungle': '丛林殖民地',
  'Desert': '沙漠殖民地',
  'Water': '海洋殖民地',
}

const itemZhDescs: {[key: string]: string} = {
  'Food': '小绿',
  'Culture': '小白',
  'Industry': '小棕',
  'Energy': '大黄',
  'Information': '大黑',
  'Biotech': '大蓝',
  'Hypertech': '柱子',
  'Ship': '红三角',
  'Score': '星星',
  'WildBig': '大灰',
  'WildSmall': '小灰',
  'ArbitrarySmall': '小彩色',
  'ArbitraryBig': '大彩色',
}

export const getItemZhName = (item: string) => {
  let donation = false;
  if (item.endsWith('Donation')) {
    item = item.replace('Donation', '');
    donation = true;
  }
  if (item in itemZhNames) {
    return itemZhNames[item] + (donation ? '捐赠' : '');
  }
  return '未知';
}

export const getItemZhDesc = (item: string) => {
  if (item.endsWith('Donation')) {
    item = item.replace('Donation', '');
  }
  if (item in itemZhDescs) {
    return itemZhDescs[item];
  }
  return '未知';
}

export const getItemZhNameDesc = (item: string) => {
  return getItemZhName(item) + '(' + getItemZhDesc(item) + ')';
}

const itemColors: {[key: string]: string} = {
  'Food': 'lightgreen',
  'Culture': 'rgb(200, 200, 200)',
  'Industry': 'brown',
  'Energy': 'yellow',
  'Information': 'black',
  'Biotech': 'blue',
  'Hypertech': 'gray',
  'Ship': 'red',
  'Score': 'purple',
  'WildBig': 'gray',
  'WildSmall': 'gray',
  'ArbitrarySmall': 'gray',
  'ArbitraryBig': 'gray',
}

const getItemColor = (item: string) => {
  let donation = false;
  if (item.endsWith('Donation')) {
    item = item.replace('Donation', '');
    donation = true;
  }
  if (item in itemColors) {
    return itemColors[item];
  }
  return 'black';
}

export const getItemOption = (item: string) => {
  return { label: getItemZhNameDesc(item), value: item, style: { color: getItemColor(item) } };
}