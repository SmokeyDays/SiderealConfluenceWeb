<script setup lang="ts">
  import { computed } from 'vue';
  import { NButton } from 'naive-ui';
  import type { Player } from '@/interfaces/GameState';
  import PanelTemplate from '@/components/panels/PanelTemplate.vue';
  import SpecieZhDiv from '@/components/SpecieZhDiv.vue';
  import { getSpecieZhName } from '@/interfaces/GameConfig';
  const props = defineProps<{
    closeEndPanel: () => void;
    getMe: () => Player | null;
    getPlayer: (playerId: string) => Player | null;
    username: string;
    players: Player[];
  }>();

  const getPlayerScore = (player: Player) => {
    return player.score + player.item_value * 0.5 / 3;
  }

  const sortedPlayers = computed(() => {
    return [...props.players].sort((a, b) => getPlayerScore(b) - getPlayerScore(a));
  });

  const winner = computed(() => sortedPlayers.value[0]);

  console.log(sortedPlayers.value);
</script>

<template>
  <PanelTemplate>
    <n-card hoverable class="end-panel standard-panel">
      <h2>游戏结束</h2>
      <h3>玩家得分</h3>
      <table>
        <thead>
          <tr>
            <th>名次</th>
            <th>玩家</th>
            <th>种族</th>
            <th>得分</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(player, index) in sortedPlayers" :key="player.user_id">
            <td>{{ index + 1 }}</td>
            <td>{{ player.user_id }}</td>
            <td><SpecieZhDiv :specie="player.specie" :is-me="player.user_id === props.username" /></td>
            <td>{{ getPlayerScore(player) + ' (' + player.score + ' + ' + (player.item_value * 0.5 / 3) + ')' }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="winner" class="winner-message">
        <h2>恭喜 {{ winner.user_id }} ({{ getSpecieZhName(winner.specie) }}) 获得胜利！</h2>
        <p>得分：{{ getPlayerScore(winner) }}</p>
      </div>

      <n-button type="error" @click="props.closeEndPanel">Close</n-button>
    </n-card>
  </PanelTemplate>
</template>

<style scoped>
.end-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin: 0 auto;
  border-radius: 10px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: center;
}

th {
  background-color: #f2f2f2;
  font-weight: bold;
}

.n-button {
  margin-top: 20px;
}

.winner-message {
  margin-top: 30px;
  text-align: center;
  font-weight: bold;
}

.winner-message h2 {
  font-size: 24px;
  color: #ff4d4f;
}

.winner-message p {
  font-size: 18px;
  color: #333;
}
</style>
