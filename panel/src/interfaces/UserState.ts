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
