export class Achievement {
  constructor(
    public id: string,
    public name: string,
    public scope: string,
    public description: string,
    public hint: string,
    public difficulty: number,
    public unlocked: boolean
  ) {}
}

export function checkUsername(newUsername: string) {
  if (newUsername.trim() === '') {
    return false;
  }
  // length must be between 3 and 16
  if (newUsername.length < 3 || newUsername.length > 20) {
    return false;
  }
  return true;
}