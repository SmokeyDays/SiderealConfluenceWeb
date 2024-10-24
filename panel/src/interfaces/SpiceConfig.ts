export const spices = ['Kylion', 'Zeth', 'Icarus'];
const spiceColors: {[key: string]: string} = {
  'Kylion': 'yellow',
  'Zeth': 'purple',
  'Icarus': 'gray'
};

export const getSpiceColor = (spice: string) => {
  if (spice in spiceColors) {
    return spiceColors[spice];
  }
  return 'black';
};