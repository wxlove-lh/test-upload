<template>
  <van-popup
    v-model:show="visible"
    position="bottom"
    round
    :style="{ maxHeight: '80vh' }"
  >
    <div class="voucher-panel">
      <div class="panel-header">
        <span>记账凭证</span>
        <span class="panel-sub">凭证用于报税备查，请妥善保存</span>
        <van-icon name="cross" class="close-icon" @click="visible = false" />
      </div>

      <!-- 已有凭证 -->
      <div class="voucher-list" v-if="voucherBlobs.length > 0">
        <div class="voucher-item" v-for="(v, i) in voucherBlobs" :key="i" @click="preview(i)">
          <img :src="v.url" class="voucher-thumb" alt="凭证" />
        </div>
      </div>
      <van-empty v-else description="暂无凭证，请上传" image="image" :image-size="60" />

      <!-- 上传区域 -->
      <div class="upload-row">
        <van-uploader
          v-model="fileList"
          :max-count="9"
          accept="image/*"
          :after-read="onFileRead"
          multiple
        >
          <van-button size="small" type="primary" plain icon="plus">添加凭证</van-button>
        </van-uploader>
        <van-button
          v-if="pendingFiles.length > 0"
          size="small"
          type="primary"
          :loading="uploading"
          loading-text="上传中..."
          @click="handleUpload"
        >
          上传 {{ pendingFiles.length }} 张
        </van-button>
      </div>

      <!-- 操作提示 -->
      <div class="panel-tip">
        <van-icon name="info-o" />
        <span>凭证将与这笔账绑定保存，查账时可随时点开查看、导出</span>
      </div>
    </div>

    <!-- 图片预览 -->
    <van-image-preview
      v-model:show="showPreview"
      :images="previewImages"
      :start-position="previewIndex"
    />
  </van-popup>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { showToast } from 'vant'
import { uploadVouchers } from '@/api/transaction'
import api from '@/api/index'

const props = defineProps({
  show: { type: Boolean, default: false },
  transaction: { type: Object, default: null },
})

const emit = defineEmits(['update:show', 'uploaded'])

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val),
})

const voucherBlobs = ref([]) // { url } 列表（blob URL）
const fileList = ref([])      // van-uploader 已选文件
const pendingFiles = ref([])  // 待上传的 File 对象
const uploading = ref(false)

const showPreview = ref(false)
const previewIndex = ref(0)

const previewImages = computed(() => voucherBlobs.value.map(v => v.url))

/** 打开面板时，把该交易的凭证URL加载为可显示的 blob */
async function loadVouchers() {
  voucherBlobs.value = []
  fileList.value = []
  pendingFiles.value = []
  if (!props.transaction || !props.transaction.voucher_urls || props.transaction.voucher_urls.length === 0) {
    return
  }
  // 逐张拉取（凭证接口需要JWT，不能直接用<img src>）
  for (const url of props.transaction.voucher_urls) {
    try {
      const res = await api.get(url, { responseType: 'blob' })
      const objectUrl = URL.createObjectURL(res)
      voucherBlobs.value.push({ url: objectUrl })
    } catch (e) {
      // 单张加载失败不影响其他
      console.error('凭证加载失败:', url, e)
    }
  }
}

function onFileRead(file) {
  if (file && file.file) {
    pendingFiles.value.push(file.file)
  }
}

async function handleUpload() {
  if (pendingFiles.value.length === 0 || !props.transaction) return
  uploading.value = true
  try {
    const res = await uploadVouchers(props.transaction.id, pendingFiles.value)
    showToast(res.message || '上传成功')
    pendingFiles.value = []
    fileList.value = []
    emit('uploaded')
    await loadVouchers()
  } catch (e) {
    // 错误已在拦截器处理
  } finally {
    uploading.value = false
  }
}

function preview(index) {
  previewIndex.value = index
  showPreview.value = true
}

watch(
  () => props.show,
  (val) => {
    if (val) loadVouchers()
  }
)
</script>

<style scoped>
.voucher-panel {
  padding: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 14px;
  position: relative;
}

.panel-sub {
  font-size: 12px;
  font-weight: normal;
  color: #969799;
  flex: 1;
}

.close-icon {
  color: #999;
  font-size: 18px;
  cursor: pointer;
}

.voucher-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.voucher-item {
  width: 90px;
  height: 90px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebedf0;
  cursor: pointer;
}

.voucher-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.upload-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.panel-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 14px;
  padding: 10px;
  background: #f7f8fa;
  border-radius: 8px;
  font-size: 12px;
  color: #646566;
}
</style>
