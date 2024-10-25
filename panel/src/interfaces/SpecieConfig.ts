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
  'Kjasjavikalimm': 'red'
};

export const getSpecieColor = (specie: string) => {
  if (specie in specieColors) {
    return specieColors[specie];
  }
  return 'black';
};