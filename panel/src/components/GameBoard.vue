<script setup lang="ts">
import { ref } from 'vue';
import { NSpace, NSelect, NButton, NDivider, NCard, NTooltip, NCollapse, NCollapseItem } from 'naive-ui';
import { GameState, Player } from '@/interfaces/GameState';
import StorageDisplayer from '@/components/StorageDisplayer.vue';
import ItemEntryDiv from '@/components/ItemEntryDiv.vue';
import { getSpecieColor, getSpecieZhName } from '@/interfaces/GameConfig';
import { socket } from '@/utils/connect';
import PanelTemplate from '@/components/panels/PanelTemplate.vue';
import SpecieZhDiv from '@/components/SpecieZhDiv.vue';
const props = defineProps<{
  gameState: GameState;
  username: string;
  handleTradePanel: () => void;
  selectedPlayer: string;
  handleSelectPlayer: (playerId: string) => void;
  handleExchangePanel: () => void;
  exitGame: () => void;
}>();

const selectedPlayer = ref(props.selectedPlayer);

const getPlayer = () => {
  return props.gameState.players.find(player => player.user_id === props.selectedPlayer) || null;
};

const getMe = () => {
  return props.gameState.players.find(player => player.user_id === props.username) || null;
};

const getPlayerSelectOptions = () => {

  return props.gameState.players.map(player => ({
    label: getSpecieZhName(player.specie) + (player.user_id === props.username ? ' (你)' : `(${player.user_id})`),
    value: player.user_id, 
    style: { color: getSpecieColor(player.specie, true), fontWeight: 'bold' }
  }));
};
const agreeToNextStage = () => {
  console.log(props.gameState.room_name);
  socket.emit('agree', { username: props.username, room_name: props.gameState.room_name });
};
const disagreeToNextStage = () => {
  socket.emit('disagree', { username: props.username, room_name: props.gameState.room_name });
};
const leaveRoomAndReturnToLobby = () => {
  socket.emit('leave-room', { username: props.username, room_name: props.gameState.room_name });
  props.exitGame();
};

const isOtherPlayerScore = (player_id: string, item: string) => {
  return (player_id !== props.username && item === "Score") && props.gameState.stage !== 'gameend';
}

const getPlayerColonyCount = (player: Player) => {
  let count = 0;
  for (let factory of Object.values(player.factories)) {
    if (factory.feature.type === 'Colony') count++;
  }
  return count;
}

const getPlayerColonyColor = (player: Player) => {
  if (getPlayerColonyCount(player) > player.max_colony) return 'red';
  if (player.max_colony === 0) return 'gray';
  if (getPlayerColonyCount(player) < player.max_colony) return 'blue';
  return 'green';
}
</script>

<template>
  <n-card vertical align="center" justify="center" class="game-panel" hoverable>
    <div class="game-board-container">
      <div class="game-info">轮次: {{ gameState.current_round }} / {{ gameState.end_round }} ，阶段: {{ gameState.stage }}</div>
      <div class="game-info">房间: {{ gameState.room_name }} 玩家: {{ gameState.players.length }}</div>
      <n-divider />
      <n-select 
        v-model:value="selectedPlayer"
        v-on:update:value="props.handleSelectPlayer(selectedPlayer)"
        :options="getPlayerSelectOptions()" 
        placeholder="Choose a player" 
      />
      <div v-if="getPlayer() !== null" class="player-info">
        <div class="player-basic-info">
          <div class="player-name">{{ getPlayer()!.user_id }} - </div>
          <SpecieZhDiv :specie="getPlayer()!.specie" :is-me="getPlayer()!.user_id === props.username" :style="{fontWeight: 'bold'}" />
          <div class="player-agreed" :style="{ fontWeight: 'bold', color: getPlayer()!.agreed ? 'green' : 'red' }">{{ getPlayer()!.agreed ? '已动完' : '没动完' }}</div>
        </div>
        <div class="player-basic-info">
          <n-tooltip placement="top" trigger="hover">
            <template #trigger>
              <div class="player-colony" :style="{ fontWeight: 'bold', color: getPlayerColonyColor(getPlayer()!) }">殖民地支持: {{ getPlayerColonyCount(getPlayer()!) }} / {{ getPlayer()!.max_colony }}</div>
            </template>
            <div>
              超出殖民地上限的殖民地必须在交易阶段结束时丢弃
            </div>
          </n-tooltip>
          <div class="player-tie-breaker" :style="{ fontWeight: 'bold'}">出价平手决胜: {{ getPlayer()!.tie_breaker }}</div>
        </div>
        <div class="relic-world-deck-size" :style="{ fontWeight: 'bold' , color: getSpecieColor(getPlayer()!.specie, true)}" v-if="getPlayer()!.specie === 'Faderan'">遗物世界牌堆剩余: {{ gameState.faderan_relic_world_deck_size }}</div>
        <div class="storage-container">
          <template v-for="(item_count, item_id) in getPlayer()!.storage">
            <ItemEntryDiv :item="item_id as string" :count="item_count" :iconWidth="60" :iconHeight="60" v-if="item_count > 0 && !isOtherPlayerScore(getPlayer()!.user_id, item_id as string)"/>
          </template>
        </div>
      </div>
      <n-divider />
      <div class="player-action">
        <template v-if="getMe() !== null">
          <template v-if="gameState.stage === 'trading' || gameState.stage === 'production'" >
            <template v-if="getMe()!.agreed === false">
              <n-button type="primary" @click="agreeToNextStage">宣布已动完</n-button>
            </template>
            <template v-else>
              <n-button type="info" @click="disagreeToNextStage">宣布未动完</n-button>
            </template>
          </template>
          <n-button type="warning" @click="props.handleTradePanel" v-if="gameState.stage === 'trading'">交易</n-button>
          <n-button type="warning" @click="props.handleExchangePanel" v-if="gameState.stage === 'trading' || gameState.stage === 'production'">自由转换</n-button>
          <n-button type="error" @click="props.exitGame">返回大厅</n-button>
          <n-button type="error" @click="leaveRoomAndReturnToLobby" v-if="gameState.stage === 'gameend'">退出游戏</n-button>
        </template>
      </div>
      <n-divider />
      <n-collapse>
        <n-collapse-item title="玩家分数" name="score">
          <template #header-extra>
            {{ getMe()!.score + ' (' + getMe()!.item_value + ')' }}
          </template>
          <div class="score-table">
            <table>
              <thead>
                <tr>
                  <th>玩家</th>
                  <n-tooltip placement="top" trigger="hover">
                    <template #trigger>
                      <th>分数</th>
                    </template>
                    <div>
                      终局计分时，玩家得分 = 分数 + 物品价值 * 0.5
                    </div>
                  </n-tooltip>
                  <n-tooltip placement="top" trigger="hover">
                    <template #trigger>
                      <th>物品</th>
                    </template>
                    <div>
                      终局计分时，玩家得分 = 分数 + 物品价值 * 0.5
                    </div>
                  </n-tooltip>
                </tr>
              </thead>
              <tbody>
                <tr v-for="player in gameState.players" :key="player.user_id">
                  <td><SpecieZhDiv :specie="player.specie" :is-me="player.user_id === props.username" :style="{fontWeight: 'bold'}" /></td>
                  <td>{{ !isOtherPlayerScore(player.user_id, 'Score') ? player.score : '?'}}</td>
                  <td>{{ player.item_value }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </n-collapse-item>
      </n-collapse>
    </div>
  </n-card>
</template>

<style scoped>
.game-panel {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 300px;
  padding-bottom: 50px;
  /* padding: 100px; */
  overflow-y: auto;
}
@media screen and (orientation: portrait) {
  .game-panel {
    height: 50vh;
    width: 100vw;
  }
}

.game-board-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.game-info {
  font-size: 1.2rem;
  font-weight: bold;
}
.player-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.player-basic-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}
.player-basic-info > * {
  margin: 5px;
}
.storage-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
}

.player-action {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
}
.player-action > * {
  margin: 10px;
}
.score-table {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 10px;
}
.score-table table {
  width: 100%;
  border-collapse: collapse;
}
.score-table th, .score-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}
.score-table th {
  font-weight: bold;
  background-color: #f2f2f2;
}
</style>
