<template>
  <div class="voice-recorder">
    <div class="record-area">
      <div
        class="record-btn"
        :class="{ recording: isRecording }"
        @touchstart.prevent="startRecord"
        @touchend.prevent="stopRecord"
        @touchcancel.prevent="stopRecord"
        @mousedown.prevent="startRecord"
        @mouseup.prevent="stopRecord"
        @mouseleave="stopRecord"
      >
        <van-icon name="audio" size="36" color="#fff" />
        <span class="record-text">{{ isRecording ? '松开结束' : '按住说话' }}</span>
      </div>
      <div v-if="isRecording" class="record-timer">
        录音中 {{ formatDuration(duration) }}
      </div>
    </div>

    <div v-if="audioBlob" class="record-result">
      <van-cell title="录音完成" :value="formatDuration(duration)" />
      <van-button size="small" plain @click="playAudio" class="play-btn">
        <van-icon name="play" /> 回放
      </van-button>
    </div>

    <div class="dev-hint">
      <van-icon name="info-o" />
      <span>语音记账功能开发中，当前版本仅支持录音预览</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'

const emit = defineEmits(['recorded'])

const isRecording = ref(false)
const duration = ref(0)
const audioBlob = ref(null)

let mediaRecorder = null
let audioChunks = []
let timer = null
let audioUrl = null

async function startRecord() {
  if (isRecording.value) return
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder = new MediaRecorder(stream)
    audioChunks = []

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data)
    }

    mediaRecorder.onstop = () => {
      audioBlob.value = new Blob(audioChunks, { type: 'audio/webm' })
      stream.getTracks().forEach(track => track.stop())
      emit('recorded', audioBlob.value)
    }

    mediaRecorder.start()
    isRecording.value = true
    duration.value = 0
    timer = setInterval(() => { duration.value++ }, 1000)
  } catch (e) {
    // 用户拒绝权限或不支持
    isRecording.value = false
  }
}

function stopRecord() {
  if (!isRecording.value || !mediaRecorder) return
  isRecording.value = false
  clearInterval(timer)
  if (mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  mediaRecorder = null
}

function playAudio() {
  if (!audioBlob.value) return
  if (audioUrl) URL.revokeObjectURL(audioUrl)
  audioUrl = URL.createObjectURL(audioBlob.value)
  const audio = new Audio(audioUrl)
  audio.play()
}

function formatDuration(sec) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

onBeforeUnmount(() => {
  clearInterval(timer)
  if (audioUrl) URL.revokeObjectURL(audioUrl)
})
</script>

<style scoped>
.voice-recorder {
  padding: 20px;
}

.record-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
}

.record-btn {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1989fa, #07c160);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 4px 12px rgba(25, 137, 250, 0.3);
  user-select: none;
}

.record-btn.recording {
  transform: scale(1.15);
  background: linear-gradient(135deg, #ee0a24, #ff6034);
  box-shadow: 0 4px 20px rgba(238, 10, 36, 0.4);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 4px 20px rgba(238, 10, 36, 0.4); }
  50% { box-shadow: 0 4px 30px rgba(238, 10, 36, 0.7); }
}

.record-text {
  font-size: 11px;
  color: #fff;
}

.record-timer {
  margin-top: 16px;
  font-size: 16px;
  color: #ee0a24;
  font-weight: bold;
}

.record-result {
  margin-top: 16px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.play-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.dev-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 24px;
  padding: 12px;
  background: #fff8e6;
  border-radius: 8px;
  font-size: 12px;
  color: #ed6a0c;
}
</style>
