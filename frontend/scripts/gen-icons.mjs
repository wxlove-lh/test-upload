/**
 * 生成 PWA 图标（无第三方依赖，纯 Node 内置 zlib 手写 PNG 编码）
 * 设计：深绿品牌底(#123F33) + 白色 "¥" 符号
 * 输出：public/icons/icon-192.png、icon-512.png
 * 运行：node scripts/gen-icons.mjs
 */
import { deflateSync } from 'node:zlib'
import { writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))

// ── CRC32（PNG 块校验用） ──
const CRC_TABLE = (() => {
  const t = new Uint32Array(256)
  for (let n = 0; n < 256; n++) {
    let c = n
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1
    t[n] = c >>> 0
  }
  return t
})()

function crc32(buf) {
  let c = 0xffffffff
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8)
  return (c ^ 0xffffffff) >>> 0
}

function chunk(type, data) {
  const len = Buffer.alloc(4)
  len.writeUInt32BE(data.length)
  const typeBuf = Buffer.from(type, 'ascii')
  const crcBuf = Buffer.alloc(4)
  crcBuf.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])))
  return Buffer.concat([len, typeBuf, data, crcBuf])
}

function encodePng(size, rgba) {
  const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])
  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(size, 0)
  ihdr.writeUInt32BE(size, 4)
  ihdr[8] = 8 // bit depth
  ihdr[9] = 6 // color type RGBA
  const raw = Buffer.alloc(size * (size * 4 + 1))
  for (let y = 0; y < size; y++) {
    raw[y * (size * 4 + 1)] = 0 // filter: none
    rgba.copy(raw, y * (size * 4 + 1) + 1, y * size * 4, (y + 1) * size * 4)
  }
  const idat = deflateSync(raw, { level: 9 })
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))])
}

// ── 画图：深绿底 + 白色 ¥ ──
function drawIcon(size) {
  const buf = Buffer.alloc(size * size * 4)
  const BG = [0x12, 0x3f, 0x33]
  const FG = [0xff, 0xff, 0xff]

  for (let i = 0; i < size * size; i++) {
    buf[i * 4] = BG[0]
    buf[i * 4 + 1] = BG[1]
    buf[i * 4 + 2] = BG[2]
    buf[i * 4 + 3] = 255
  }

  const s = size / 512
  const set = (x, y, c) => {
    if (x < 0 || y < 0 || x >= size || y >= size) return
    const i = (y * size + x) * 4
    buf[i] = c[0]; buf[i + 1] = c[1]; buf[i + 2] = c[2]; buf[i + 3] = 255
  }

  const line = (x1, y1, x2, y2, r, c) => {
    const dx = x2 - x1
    const dy = y2 - y1
    const steps = Math.max(1, Math.ceil(Math.hypot(dx, dy)))
    const rr = Math.max(1, Math.round(r * s))
    for (let i = 0; i <= steps; i++) {
      const t = i / steps
      const cx = Math.round(x1 + dx * t)
      const cy = Math.round(y1 + dy * t)
      for (let dy2 = -rr; dy2 <= rr; dy2++) {
        for (let dx2 = -rr; dx2 <= rr; dx2++) {
          if (dx2 * dx2 + dy2 * dy2 <= rr * rr) set(cx + dx2, cy + dy2, c)
        }
      }
    }
  }

  // 512 设计坐标：竖线 + 两条斜线汇聚 + 两条横杠
  line(256, 128, 256, 392, 26, FG)   // 竖
  line(136, 136, 252, 250, 26, FG)   // 左斜
  line(376, 136, 260, 250, 26, FG)   // 右斜
  line(184, 288, 328, 288, 26, FG)   // 上横
  line(184, 348, 328, 348, 26, FG)   // 下横

  return buf
}

const outDir = join(__dirname, '..', 'public', 'icons')
mkdirSync(outDir, { recursive: true })

for (const size of [192, 512]) {
  const png = encodePng(size, drawIcon(size))
  writeFileSync(join(outDir, `icon-${size}.png`), png)
  console.log(`生成 icon-${size}.png (${png.length} 字节)`)
}
