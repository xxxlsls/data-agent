<template>
  <div class="px-app">
    <!-- ===== 顶栏 ===== -->
    <header class="px-header">
      <div class="px-brand">
        <span class="px-logo">▣</span>
        <div class="px-brand-text">
          <h1 class="px-title">DATA QUEST</h1>
          <span class="px-subtitle">数据查询助手 · NL2SQL</span>
        </div>
      </div>
      <!-- 关卡指示：已完成的查询数 -->
      <div class="px-stage">
        <span class="px-stage-label">QUESTS</span>
        <span class="px-stage-num">{{ queryCount }}</span>
      </div>
    </header>

    <!-- ===== 主体 ===== -->
    <div class="px-body">
      <!-- 左侧栏：快捷提问（从欢迎页中央移到这里，常驻可见） -->
      <aside class="px-sidebar">
        <div class="px-panel">
          <div class="px-panel-head">
            <span class="px-panel-icon">▤</span>
            <span class="px-panel-title">QUICK QUESTS</span>
          </div>
          <div class="px-panel-body">
            <button
              v-for="(q, i) in quickQuestions"
              :key="q"
              class="px-quest"
              :disabled="loading"
              @click="sendQuickQuestion(q)"
            >
              <span class="px-quest-idx">{{ String(i + 1).padStart(2, "0") }}</span>
              <span class="px-quest-text">{{ q }}</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- 消息区 -->
      <main class="px-main" ref="messagesEl" @scroll="onScroll">
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="px-welcome">
          <div class="px-welcome-box">
            <div class="px-welcome-robot">▚▞</div>
            <h2 class="px-welcome-title">READY PLAYER ONE</h2>
            <p class="px-welcome-desc">
              用自然语言描述你的需求<br />
              系统将自动生成 SQL 并返回查询结果
            </p>
            <div class="px-welcome-hint">
              <span class="px-blink">▶</span> 从左侧选择一个任务，或在下方直接输入
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-else class="px-messages">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['px-row', msg.role]"
          >
            <div v-if="msg.role === 'assistant'" class="px-avatar px-avatar-bot">▣</div>

            <div class="px-bubble-wrap">
              <div class="px-bubble">
                <!-- 文本 -->
                <div v-if="msg.type === 'text'" class="px-text">{{ msg.content }}</div>

                <!-- 进度 -->
                <div v-else-if="msg.type === 'steps'" class="px-steps">
                  <div
                    v-for="(step, sIdx) in msg.steps"
                    :key="sIdx"
                    :class="['px-step', step.status]"
                  >
                    <span class="px-step-box">
                      <span v-if="step.status === 'success'">x</span>
                      <span v-else-if="step.status === 'error'">!</span>
                      <span v-else class="px-step-run">.</span>
                    </span>
                    <span class="px-step-text">{{ step.text }}</span>
                  </div>
                </div>

                <!-- 表格 -->
                <div v-else-if="msg.type === 'table'" class="px-table-block">
                  <div class="px-table-bar">
                    <span>▤ RESULT</span>
                    <span class="px-table-count">{{ msg.rows.length }} ROWS</span>
                  </div>
                  <div class="px-table-wrap">
                    <table class="px-table">
                      <thead>
                        <tr>
                          <th v-for="col in msg.columns" :key="col">{{ col }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(row, rIdx) in msg.rows" :key="rIdx">
                          <td v-for="col in msg.columns" :key="col">
                            {{ row[col] }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- 错误 -->
                <div v-else-if="msg.type === 'error'" class="px-error">
                  <span class="px-error-tag">ERROR</span>
                  <span class="px-error-detail">{{ msg.content }}</span>
                </div>
              </div>
              <span v-if="msg.ts" class="px-time">{{ msg.ts }}</span>
            </div>

            <div v-if="msg.role === 'user'" class="px-avatar px-avatar-user">◧</div>
          </div>
          <div class="px-bottom-spacer"></div>
        </div>
      </main>
    </div>

    <!-- ===== 底栏：状态 + 输入 ===== -->
    <footer class="px-footer">
      <!-- 状态栏（状态指示从顶栏移到此处） -->
      <div class="px-statusbar">
        <span class="px-status-dot" :class="loading ? 'busy' : 'idle'"></span>
        <span class="px-status-text">{{ loading ? "RUNNING..." : "READY" }}</span>
        <span class="px-status-sep">│</span>
        <span class="px-status-text">SQL ENGINE</span>
        <button
          v-if="showScrollBtn"
          class="px-jump"
          @click="scrollToBottom(true)"
          title="跳到最新"
        >
          ▼▼
        </button>
      </div>

      <!-- 输入框 -->
      <div class="px-input-row">
        <span class="px-prompt">&gt;</span>
        <input
          ref="inputEl"
          v-model="question"
          class="px-input"
          @keyup.enter="sendQuestion"
          placeholder="输入你的问题…"
          :disabled="loading"
        />
        <button
          class="px-send"
          @click="sendQuestion"
          :disabled="loading || !question"
          :title="loading ? '查询中…' : '发送'"
        >
          <span v-if="!loading" class="px-send-arrow">▶</span>
          <span v-else class="px-send-spin"></span>
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { nextTick, ref, computed } from "vue";

// ===== 常量 =====
const API_URL = "/api/query";

const quickQuestions = [
  "查询最近一周的订单数据",
  "统计本月各地区的销售额",
  "查看客户消费金额排名 TOP 10",
  "分析商品分类的销售趋势",
  "统计各商品的订单量",
  "对比今年与去年的营收情况",
];

// ===== 状态 =====
const question = ref("");
const loading = ref(false);
const messages = ref([]);
const messagesEl = ref(null);
const inputEl = ref(null);
const showScrollBtn = ref(false);
const isNearBottom = ref(true);

// 顶栏关卡数：用户提问次数
const queryCount = computed(
  () => messages.value.filter((m) => m.role === "user").length
);

// ===== 工具 =====
function timeNow() {
  const d = new Date();
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function scrollToBottom(smooth = false) {
  const el = messagesEl.value;
  if (!el) return;
  el.scrollTo({
    top: el.scrollHeight,
    behavior: smooth ? "smooth" : "instant",
  });
}

function onScroll() {
  const el = messagesEl.value;
  if (!el) return;
  const threshold = 120;
  isNearBottom.value = el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
  showScrollBtn.value = !isNearBottom.value;
}

// ===== 动作 =====
function sendQuickQuestion(q) {
  if (loading.value) return;
  question.value = q;
  sendQuestion();
}

async function sendQuestion() {
  if (!question.value || loading.value) return;

  const q = question.value;
  question.value = "";
  loading.value = true;

  messages.value.push({
    role: "user",
    type: "text",
    content: q,
    ts: timeNow(),
  });

  // 进度容器
  const stepIndex =
    messages.value.push({
      role: "assistant",
      type: "steps",
      steps: [],
      ts: timeNow(),
    }) - 1;

  await nextTick();
  scrollToBottom();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q }),
    });

    if (!response.body) throw new Error("服务器未返回流");

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop();

      for (const evt of events) {
        const line = evt.trim();
        if (!line.startsWith("data:")) continue;

        let data;
        try {
          data = JSON.parse(line.replace(/^data:\s*/, ""));
        } catch {
          continue;
        }

        const steps = messages.value[stepIndex].steps;

        // 进度
        if (data.type === "progress") {
          let step = steps.find((s) => s.text === data.step);
          if (!step) {
            step = { text: data.step, status: data.status };
            steps.push(step);
          } else {
            step.status = data.status;
          }
        }

        // 结果表
        else if (data.type === "result" && Array.isArray(data.data)) {
          messages.value.push({
            role: "assistant",
            type: "table",
            columns: Object.keys(data.data[0] || {}),
            rows: data.data,
            ts: timeNow(),
          });
        }

        // 错误
        else if (data.type === "error") {
          messages.value.push({
            role: "assistant",
            type: "error",
            content: data.message || "发生错误",
            ts: timeNow(),
          });
        }

        await nextTick();
        scrollToBottom();
      }
    }
  } catch (e) {
    messages.value.push({
      role: "assistant",
      type: "error",
      content: e?.message || "请求失败",
      ts: timeNow(),
    });
  } finally {
    loading.value = false;
    await nextTick();
    scrollToBottom();
  }
}
</script>

<style scoped>
/* ===== 整体布局 ===== */
.px-app {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* ===== 顶栏 ===== */
.px-header {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--header-h);
  padding: 0 var(--sp-4);
  background: var(--px-surface);
  border-bottom: var(--px-border);
  box-shadow: var(--px-shadow-sm);
  z-index: 10;
}

.px-brand {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}

.px-logo {
  font-size: 26px;
  color: var(--px-primary);
  line-height: 1;
}

.px-brand-text {
  display: flex;
  flex-direction: column;
}

.px-title {
  font-family: "Press Start 2P", var(--font-family);
  font-size: 14px;
  letter-spacing: 1px;
  color: var(--px-ink);
  line-height: 1.4;
}

.px-subtitle {
  font-size: var(--fs-xs);
  color: var(--px-ink-2);
}

/* 关卡计数 */
.px-stage {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-1) var(--sp-3);
  background: var(--px-ink);
  color: var(--px-surface);
  border: var(--px-border-thin);
  box-shadow: var(--px-shadow-sm);
}

.px-stage-label {
  font-size: 10px;
  letter-spacing: 1px;
  color: var(--px-primary-l);
}

.px-stage-num {
  font-size: var(--fs-md);
  font-weight: 700;
}

/* ===== 主体 ===== */
.px-body {
  flex: 1;
  display: flex;
  min-height: 0;
}

/* ===== 左侧栏 ===== */
.px-sidebar {
  flex-shrink: 0;
  width: 240px;
  padding: var(--sp-4);
  overflow-y: auto;
  border-right: var(--px-border);
  background: rgba(251, 247, 234, 0.6);
}

.px-panel {
  border: var(--px-border);
  background: var(--px-surface);
  box-shadow: var(--px-shadow);
}

.px-panel-head {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-3);
  background: var(--px-primary);
  color: #fff;
  border-bottom: var(--px-border-thin);
}

.px-panel-icon {
  font-size: var(--fs-sm);
}

.px-panel-title {
  font-size: 10px;
  letter-spacing: 1px;
}

.px-panel-body {
  display: flex;
  flex-direction: column;
}

.px-quest {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-3);
  background: transparent;
  border: none;
  border-bottom: 2px dashed var(--px-ink-3);
  font-family: var(--font-family);
  font-size: var(--fs-xs);
  color: var(--px-ink-2);
  text-align: left;
  cursor: pointer;
  transition: background var(--t-fast), color var(--t-fast);
}

.px-quest:last-child {
  border-bottom: none;
}

.px-quest:hover:not(:disabled) {
  background: var(--px-primary-l);
  color: var(--px-ink);
}

.px-quest:active:not(:disabled) {
  background: var(--px-primary);
  color: #fff;
}

.px-quest:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.px-quest-idx {
  flex-shrink: 0;
  color: var(--px-accent);
  font-weight: 700;
}

.px-quest-text {
  line-height: 1.5;
}

/* ===== 消息区 ===== */
.px-main {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 空状态 */
.px-welcome {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100%;
  padding: var(--sp-8) var(--sp-4);
}

.px-welcome-box {
  max-width: 460px;
  padding: var(--sp-6);
  text-align: center;
  border: var(--px-border);
  background: var(--px-surface);
  box-shadow: var(--px-shadow-lg);
}

.px-welcome-robot {
  font-size: 40px;
  color: var(--px-primary);
  margin-bottom: var(--sp-4);
  animation: px-bounce 1.6s steps(4, end) infinite;
}

.px-welcome-title {
  font-family: "Press Start 2P", var(--font-family);
  font-size: 15px;
  letter-spacing: 1px;
  color: var(--px-ink);
  margin-bottom: var(--sp-3);
}

.px-welcome-desc {
  font-size: var(--fs-sm);
  color: var(--px-ink-2);
  line-height: 1.9;
  margin-bottom: var(--sp-4);
}

.px-welcome-hint {
  padding-top: var(--sp-3);
  border-top: 2px dashed var(--px-ink-3);
  font-size: var(--fs-xs);
  color: var(--px-ink-2);
}

.px-blink {
  color: var(--px-accent);
  animation: px-blink 1s steps(1, end) infinite;
}

/* 消息列表 */
.px-messages {
  padding: var(--sp-5) var(--sp-4);
}

.px-bottom-spacer {
  height: var(--sp-4);
}

.px-row {
  display: flex;
  gap: var(--sp-2);
  margin-bottom: var(--sp-5);
  animation: px-fade-up var(--t-base);
}

.px-row.user {
  justify-content: flex-end;
}

.px-row.assistant {
  justify-content: flex-start;
}

/* 头像：方块 */
.px-avatar {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  border: var(--px-border-thin);
  box-shadow: var(--px-shadow-sm);
}

.px-avatar-bot {
  background: var(--px-primary-l);
  color: var(--px-primary-d);
}

.px-avatar-user {
  background: var(--px-accent-l);
  color: var(--px-accent);
}

/* 气泡 */
.px-bubble-wrap {
  display: flex;
  flex-direction: column;
  max-width: min(720px, 74%);
}

.px-row.user .px-bubble-wrap {
  align-items: flex-end;
}

.px-row.assistant .px-bubble-wrap {
  align-items: flex-start;
}

.px-bubble {
  padding: var(--sp-3) var(--sp-4);
  font-size: var(--fs-base);
  line-height: 1.7;
  word-break: break-word;
  border: var(--px-border);
  box-shadow: var(--px-shadow-sm);
}

.px-row.user .px-bubble {
  background: var(--px-primary);
  color: #fff;
}

.px-row.assistant .px-bubble {
  background: var(--px-surface);
  color: var(--px-ink);
}

.px-time {
  margin-top: var(--sp-1);
  font-size: 10px;
  color: var(--px-ink-3);
}

/* ===== 进度步骤 ===== */
.px-steps {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.px-step {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: var(--fs-sm);
}

.px-step-box {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  border: var(--px-border-thin);
  background: var(--px-surface-2);
  color: var(--px-ink-3);
}

.px-step.success .px-step-box {
  background: var(--px-success-bg);
  border-color: var(--px-success);
  color: var(--px-success);
}

.px-step.error .px-step-box {
  background: var(--px-error-bg);
  border-color: var(--px-error);
  color: var(--px-error);
}

.px-step.running .px-step-box {
  background: var(--px-warning-bg);
  border-color: var(--px-warning);
  color: var(--px-warning);
}

.px-step-run {
  animation: px-blink 0.8s steps(1, end) infinite;
}

.px-step-text {
  color: var(--px-ink-2);
}

.px-step.success .px-step-text,
.px-step.running .px-step-text {
  color: var(--px-ink);
}

.px-step.error .px-step-text {
  color: var(--px-error);
}

/* ===== 表格 ===== */
.px-table-block {
  min-width: 320px;
}

.px-table-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--sp-2) var(--sp-3);
  margin-bottom: var(--sp-3);
  background: var(--px-ink);
  color: var(--px-surface);
  font-size: 10px;
  letter-spacing: 1px;
}

.px-table-count {
  color: var(--px-primary-l);
}

.px-table-wrap {
  overflow-x: auto;
  border: var(--px-border-thin);
}

.px-table {
  width: max-content;
  min-width: 100%;
  border-collapse: collapse;
}

.px-table th,
.px-table td {
  padding: var(--sp-2) var(--sp-3);
  font-size: var(--fs-xs);
  text-align: left;
  white-space: nowrap;
  border: 1px solid var(--px-ink-3);
}

.px-table th {
  background: var(--px-primary-l);
  color: var(--px-ink);
  font-weight: 700;
  letter-spacing: 1px;
}

.px-table td {
  background: var(--px-surface-2);
  color: var(--px-ink-2);
}

.px-table tbody tr:hover td {
  background: var(--px-accent-l);
  color: var(--px-ink);
}

/* ===== 错误 ===== */
.px-error {
  display: flex;
  align-items: flex-start;
  gap: var(--sp-2);
}

.px-error-tag {
  flex-shrink: 0;
  padding: 1px var(--sp-2);
  background: var(--px-error);
  color: #fff;
  font-size: 10px;
  letter-spacing: 1px;
}

.px-error-detail {
  font-size: var(--fs-sm);
  color: var(--px-error);
  line-height: 1.6;
}

/* ===== 底栏 ===== */
.px-footer {
  flex-shrink: 0;
  padding: var(--sp-2) var(--sp-4) var(--sp-4);
  background: var(--px-surface);
  border-top: var(--px-border);
  box-shadow: 0 -2px 0 rgba(34, 34, 59, 0.15);
}

/* 状态栏 */
.px-statusbar {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: 0 var(--sp-1) var(--sp-2);
  font-size: 10px;
  letter-spacing: 1px;
  color: var(--px-ink-2);
}

.px-status-dot {
  width: 8px;
  height: 8px;
  background: var(--px-success);
  border: 1px solid var(--px-ink);
}

.px-status-dot.busy {
  background: var(--px-warning);
  animation: px-blink 0.8s steps(1, end) infinite;
}

.px-status-sep {
  color: var(--px-ink-3);
}

.px-jump {
  margin-left: auto;
  padding: 1px var(--sp-2);
  background: var(--px-accent-l);
  border: var(--px-border-thin);
  font-family: var(--font-family);
  font-size: 10px;
  color: var(--px-ink);
  cursor: pointer;
  box-shadow: var(--px-shadow-sm);
}

.px-jump:hover {
  background: var(--px-accent);
  color: #fff;
}

/* 输入行 */
.px-input-row {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-1);
  border: var(--px-border);
  background: var(--px-surface-2);
  box-shadow: var(--px-shadow-sm);
}

.px-prompt {
  padding-left: var(--sp-2);
  color: var(--px-accent);
  font-weight: 700;
  animation: px-blink 1.1s steps(1, end) infinite;
}

.px-input {
  flex: 1;
  min-width: 0;
  padding: var(--sp-2) 0;
  border: none;
  outline: none;
  background: transparent;
  font-family: var(--font-family);
  font-size: var(--fs-md);
  color: var(--px-ink);
}

.px-input::placeholder {
  color: var(--px-ink-3);
}

.px-input:disabled {
  opacity: 0.5;
}

.px-send {
  flex-shrink: 0;
  width: 38px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--px-primary);
  border: var(--px-border-thin);
  color: #fff;
  font-size: 15px;
  cursor: pointer;
  transition: background var(--t-fast), transform var(--t-fast);
}

.px-send:hover:not(:disabled) {
  background: var(--px-primary-d);
  transform: translate(-1px, -1px);
}

.px-send:active:not(:disabled) {
  transform: translate(1px, 1px);
}

.px-send:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.px-send-spin {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  animation: px-spin 0.7s steps(8, end) infinite;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .px-sidebar {
    width: 200px;
  }
}

@media (max-width: 720px) {
  .px-body {
    flex-direction: column;
  }

  /* 窄屏：左侧栏折到上方，横向滚动 */
  .px-sidebar {
    width: 100%;
    padding: var(--sp-2);
    border-right: none;
    border-bottom: var(--px-border);
  }

  .px-panel-body {
    flex-direction: row;
    overflow-x: auto;
  }

  .px-quest {
    flex-shrink: 0;
    border-bottom: none;
    border-right: 2px dashed var(--px-ink-3);
    white-space: nowrap;
  }

  .px-title {
    font-size: 11px;
  }

  .px-subtitle {
    display: none;
  }

  .px-bubble-wrap {
    max-width: 84%;
  }
}
</style>
