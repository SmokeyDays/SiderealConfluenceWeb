<script setup lang="ts">
import { ref, computed } from 'vue';
import { 
  NSpace, NSelect, NButton, NCollapse, NCollapseItem, NTooltip
} from 'naive-ui';
import { getPlayerScore, GameState, Player } from '@/interfaces/GameState';
import ItemEntryDiv from '@/components/ItemEntryDiv.vue';
import { getSpecieColor, getSpecieZhName } from '@/interfaces/GameConfig';
import { socket } from '@/utils/connect';
import SpecieZhDiv from '@/components/SpecieZhDiv.vue';
import { sidConThemeOverrides } from '@/interfaces/SidConTheme';

const props = defineProps<{
  gameState: GameState;
  username: string;
  handleTradePanel: () => void;
  selectedPlayer: string;
  handleSelectPlayer: (playerId: string) => void;
  handleExchangePanel: () => void;
  handleBulletinPanel: () => void;
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
  if (getPlayerColonyCount(player) > player.max_colony) return '#ff4d4f'; // Bright Red
  if (player.max_colony === 0) return '#63e2b7'; // Naive Green
  if (getPlayerColonyCount(player) < player.max_colony) return '#70c0e8'; // Blue
  return '#63e2b7';
}

const hasItems = (obj: { [key: string]: number } | undefined) => {
  if (!obj) return false;
  return Object.entries(obj).some(([_, count]) => count > 0);
};

</script>

<template>
    <div class="game-panel sci-fi-hud">
      
      <div class="hud-header">
        <div class="hud-row">
          <span class="hud-label">房间</span>
          <span class="hud-value neon-text">{{ gameState.room_name }}</span>
        </div>
        <div class="hud-row">
          <span class="hud-label">回合数</span>
          <span class="hud-value">{{ gameState.current_round }}/{{ gameState.end_round }}</span>
          <span class="hud-separator">|</span>
          <span class="hud-value state-badge">{{ gameState.stage + " 阶段"}}</span>
        </div>
      </div>

      <div class="hud-divider"></div>

      <div class="player-selector-area">
        <n-select 
          size="small"
          v-model:value="selectedPlayer"
          v-on:update:value="props.handleSelectPlayer(selectedPlayer)"
          :options="getPlayerSelectOptions()" 
          placeholder="Select Target" 
        />
      </div>

      <div v-if="getPlayer() !== null" class="player-detail-panel">
        
        <div class="identity-card">
          <div class="id-header">
            <span class="id-name">{{ getPlayer()!.user_id }}</span>
            <div class="status-indicator" :class="{ 'status-ok': getPlayer()!.agreed, 'status-pending': !getPlayer()!.agreed }">
              {{ getPlayer()!.agreed ? '行动完毕' : '行动中' }}
            </div>
          </div>
          <div class="id-body">
            <SpecieZhDiv :specie="getPlayer()!.specie" :is-me="getPlayer()!.user_id === props.username" />
            <span v-if="getPlayer()!.specie === 'Faderan'" class="faderan-deck">
              法德澜遗迹牌堆剩余: {{ gameState.faderan_relic_world_deck_size }}
            </span>
          </div>
          <div class="id-stats">
            <div class="stat-item" :style="{ color: getPlayerColonyColor(getPlayer()!) }">
              <span class="stat-label">殖民地</span>
              {{ getPlayerColonyCount(getPlayer()!) }} / {{ getPlayer()!.max_colony }}
            </div>
            <div class="stat-item">
              <span class="stat-label">出价平手决胜</span>
              {{ getPlayer()!.tie_breaker }}
            </div>
          </div>
        </div>

        <div class="bulletin-terminal" v-if="getPlayer()!.bulletin_board">
          <div class="terminal-msg" v-if="getPlayer()!.bulletin_board.message">
            "> {{ getPlayer()!.bulletin_board.message }}"
          </div>
          
          <div class="trade-grid">
             <div class="trade-row seeking" v-if="hasItems(getPlayer()!.bulletin_board.seeking)">
              <span class="trade-tag seek">求购</span>
              <div class="trade-items">
                <template v-for="(count, item_id) in getPlayer()!.bulletin_board.seeking">
                  <ItemEntryDiv v-if="count > 0" :key="'seek-'+item_id" :item="item_id as string" :count="count" :iconWidth="24" :iconHeight="24"/>
                </template>
              </div>
            </div>

            <div class="trade-row offering" v-if="hasItems(getPlayer()!.bulletin_board.offering)">
              <span class="trade-tag offer">待售</span>
              <div class="trade-items">
                <template v-for="(count, item_id) in getPlayer()!.bulletin_board.offering">
                  <ItemEntryDiv v-if="count > 0" :key="'offer-'+item_id" :item="item_id as string" :count="count" :iconWidth="24" :iconHeight="24"/>
                </template>
              </div>
            </div>
          </div>
        </div>

        <div class="storage-grid-container">
          <div class="section-title">库存</div>
          <div class="storage-grid">
            <template v-for="(item_count, item_id) in getPlayer()!.storage">
              <div class="storage-cell" v-if="item_count > 0 && !isOtherPlayerScore(getPlayer()!.user_id, item_id as string)">
                <ItemEntryDiv :item="item_id as string" :count="item_count" :iconWidth="40" :iconHeight="40" />
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="action-panel" v-if="getMe() !== null">
        <template v-if="gameState.stage === 'trading' || gameState.stage === 'production'" >
            <n-button class="cyber-btn" block strong secondary :type="getMe()!.agreed ? 'info' : 'primary'" @click="getMe()!.agreed ? disagreeToNextStage() : agreeToNextStage()">
              {{ getMe()!.agreed ? '取消预备' : '结束行动' }}
            </n-button>
        </template>
        
        <div class="button-grid">
          <n-button size="small" secondary type="warning" @click="props.handleTradePanel" v-if="gameState.stage === 'trading'">交易面板</n-button>
          <n-button size="small" secondary type="warning" @click="props.handleBulletinPanel" v-if="gameState.stage === 'trading'">编辑公告</n-button>
          <n-button size="small" secondary type="warning" @click="props.handleExchangePanel" v-if="gameState.stage === 'trading' || gameState.stage === 'production'">自由转换</n-button>
        </div>
        
        <div class="exit-row">
             <n-button size="tiny" text type="error" @click="props.exitGame">回到大厅</n-button>
             <n-button size="tiny" text type="error" @click="leaveRoomAndReturnToLobby" v-if="gameState.stage === 'gameend'">离开游戏</n-button>
        </div>
      </div>

      <div class="score-panel-wrapper">
        <n-collapse>
          <n-collapse-item title=">> 分数信息" name="score">
            <div class="cyber-table">
              <div class="tbl-header">
                <span>玩家</span><span>分数</span><span>价值</span>
              </div>
              <div class="tbl-row" v-for="player in gameState.players" :key="player.user_id">
                <span class="tbl-name">{{ player.user_id }}</span>
                <span class="tbl-data">{{ !isOtherPlayerScore(player.user_id, 'Score') ? player.score : '??' }}</span>
                <span class="tbl-data dim">{{ player.item_value }}</span>
              </div>
              <n-tooltip placement="top" trigger="hover">
                <template #trigger>
                  <div class="tbl-footer" v-if="getMe()">
                    共计: {{ getPlayerScore(getMe()!).toFixed(2) }}
                  </div>
                </template>
                <div>
                  终局计分时，玩家得分 = 分数 + 物品价值 * 0.5
                </div>
              </n-tooltip>
            </div>
          </n-collapse-item>
        </n-collapse>
      </div>

    </div>
  <!-- </n-config-provider> -->
</template>

<style scoped>
/* 定义 Sci-Fi 变量 */
.sci-fi-hud {
  --bg-color: rgba(5, 10, 20, 0.95);
  --border-color: rgba(0, 212, 255, 0.5);
  --text-main: #cceeff;
  --text-dim: #5f7e8f;
  --accent-cyan: #00d4ff;
  --accent-red: #ff3b3b;
  --accent-green: #00ff9d;
  --font-tech: "Consolas", "Monaco", "Courier New", monospace;
  
  font-family: var(--font-tech);
  color: var(--text-main);
  background-color: var(--bg-color);
  
  /* 布局属性 */
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 320px; /* 稍微加宽一点以容纳紧凑信息 */
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-color);
  box-shadow: 5px 0 20px rgba(0, 212, 255, 0.1);
  overflow-y: auto;
  z-index: 100;
  
  /* 滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: var(--accent-cyan) var(--bg-color);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 移动端适配 */
@media screen and (orientation: portrait) {
  .sci-fi-hud {
    height: 50vh;
    width: 100vw;
    border-right: none;
    border-bottom: 2px solid var(--border-color);
  }
}

/* 1. Header */
.hud-header {
  padding: 15px;
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.1) 0%, transparent 100%);
}

.hud-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.hud-label {
  font-size: 0.75rem;
  color: var(--text-dim);
  letter-spacing: 1px;
}

.hud-value {
  font-weight: bold;
  font-size: 1rem;
}

.neon-text {
  color: var(--accent-cyan);
  text-shadow: 0 0 5px var(--accent-cyan);
}

.state-badge {
  background: var(--accent-cyan);
  color: #000;
  padding: 0 4px;
  font-size: 0.8rem;
  border-radius: 2px;
  text-transform: uppercase;
}

.hud-divider {
  height: 1px;
  background: linear-gradient(90deg, var(--border-color), transparent);
  margin-bottom: 10px;
}

/* 2. Selector */
.player-selector-area {
  padding: 0 15px 10px 15px;
}

/* 3. Player Details */
.player-detail-panel {
  flex: 1;
  padding: 0 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.identity-card {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px;
  background: rgba(0, 0, 0, 0.3);
}

.id-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.1);
  padding-bottom: 4px;
  margin-bottom: 4px;
}

.id-name {
  font-size: 1.1rem;
  font-weight: bold;
  color: #fff;
}

.status-indicator {
  font-size: 0.7rem;
  padding: 1px 4px;
  border: 1px solid var(--text-dim);
}
.status-ok { color: var(--accent-green); border-color: var(--accent-green); box-shadow: 0 0 4px var(--accent-green) inset; }
.status-pending { color: var(--accent-red); border-color: var(--accent-red); }

.id-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.faderan-deck {
  font-size: 0.75rem;
  color: #e0e;
}

.id-stats {
  display: flex;
  gap: 10px;
  margin-top: 4px;
  font-size: 0.75rem;
}
.stat-item {
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 5px;
  border-radius: 2px;
}
.stat-label {
  color: var(--text-dim);
  margin-right: 3px;
}

/* Bulletin Terminal */
.bulletin-terminal {
  border-left: 2px solid var(--text-dim);
  background: rgba(255, 255, 255, 0.02);
  padding: 5px;
  margin-top: 5px;
}
.terminal-msg {
  font-family: "Courier New", monospace;
  font-size: 0.8rem;
  color: #ddd;
  margin-bottom: 6px;
  word-break: break-all;
}
.trade-row {
  display: flex;
  align-items: center;
  margin-bottom: 2px;
}
.trade-tag {
  font-size: 0.7rem;
  font-weight: bold;
  width: 35px;
  text-align: center;
  margin-right: 5px;
  color: #000;
}
.trade-tag.seek { background-color: #ff6b6b; }
.trade-tag.offer { background-color: #51cf66; }
.trade-items { display: flex; flex-wrap: wrap; gap: 2px; }

/* Storage Grid */
.storage-grid-container {
  margin-top: 5px;
}
.section-title {
  font-size: 0.75rem;
  color: var(--accent-cyan);
  border-bottom: 1px solid var(--accent-cyan);
  margin-bottom: 5px;
  display: inline-block;
}
.storage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
  gap: 5px;
}
.storage-cell {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 1;
}

/* 4. Actions */
.action-panel {
  padding: 15px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
.cyber-btn {
  margin-bottom: 10px;
  border-radius: 0; /* 硬朗的直角 */
  letter-spacing: 1px;
}
.button-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 5px;
  margin-bottom: 5px;
}
.exit-row {
  display: flex;
  justify-content: flex-end;
}

/* 5. Score Table */
.score-panel-wrapper {
  border-top: 1px solid var(--border-color);
  background: #000;
}
.cyber-table {
  font-size: 0.8rem;
  padding: 0 10px 10px 10px;
}
.tbl-header, .tbl-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  padding: 4px 0;
  border-bottom: 1px solid #333;
}
.tbl-header {
  color: var(--accent-cyan);
  font-weight: bold;
}
.tbl-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tbl-data {
  text-align: right;
  font-family: monospace;
}
.tbl-data.dim { color: #666; }
.tbl-footer {
  text-align: center;
  color: var(--accent-green);
  margin-top: 5px;
  font-weight: bold;
  border: 1px dashed var(--accent-green);
}
</style>