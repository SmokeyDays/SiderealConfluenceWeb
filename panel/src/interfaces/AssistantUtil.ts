/**
 * 在特定假设下计算夏普里值。
 * 假设: 任何非全体成员的子联盟的价值等于其成员单方价值之和。
 * 只有全体成员合作时才可能产生额外的协同效应。
 *
 * @param playerStandaloneValues - 一个 Map 对象，键是参与者ID (string)，
 * 值是该参与者的单方价值 (number)。
 * @param grandCooperativeValue - 全体参与者达成合作后的最终总价值 (number)。
 * @returns 一个 Map 对象，键是参与者ID，值是该参与者的夏普里值。
 */
export function calculateShapleyValuesSimplified(
  playerStandaloneValues: Map<string, number>,
  grandCooperativeValue: number
): Map<string, number> {
  const players = Array.from(playerStandaloneValues.keys());
  const n = players.length;
  const shapleyResults = new Map<string, number>();

  if (n === 0) {
    return shapleyResults; // 返回空 Map
  }

  let sumOfStandaloneValues = 0;
  for (const standaloneValue of playerStandaloneValues.values()) {
    sumOfStandaloneValues += standaloneValue;
  }

  // 计算合作产生的总协同增益（或亏损）
  // This is (v(N) - sum(v({j})))
  const totalSynergy = grandCooperativeValue - sumOfStandaloneValues;

  // 每个参与者分得其单方价值，并均分总协同增益
  for (const player of players) {
    const standaloneValue = playerStandaloneValues.get(player);
    if (standaloneValue === undefined) {
      // 这种情况理论上不应发生，因为 players 来自 playerStandaloneValues.keys()
      throw new Error(`错误: 参与者 ${player} 的单方价值未定义。`);
    }
    const shapleyValue = standaloneValue + totalSynergy / n;
    shapleyResults.set(player, shapleyValue);
  }

  return shapleyResults;
}