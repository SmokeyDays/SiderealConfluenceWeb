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

export const items = ["Food", "Culture", "Industry", "Energy", "Information", "Biotech", "Hypertech", "Ship", "Score","AnyBig", "AnySmall"];
