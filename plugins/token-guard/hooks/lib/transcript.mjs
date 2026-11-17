// Incremental reader for the Claude Code session transcript (JSONL).
//
// One API response can be written as several consecutive lines that share the
// same message.id (one per content block), so steps are counted per distinct id.
// Subagent lines (isSidechain) belong to another conversation and are skipped.

import { closeSync, fstatSync, openSync, readSync } from 'node:fs'

/**
 * Reads the transcript from state.transcriptOffset to the last complete line
 * and updates state.steps, state.lastMessageId, state.lastContextTokens and
 * state.lastAssistantText. Returns the number of new steps.
 */
export function advanceTranscript(state, transcriptPath) {
  const fd = openSync(transcriptPath, 'r')
  let chunk
  try {
    const size = fstatSync(fd).size
    if (size < state.transcriptOffset) state.transcriptOffset = 0 // file was replaced
    const len = size - state.transcriptOffset
    if (len <= 0) return 0
    const buf = Buffer.alloc(len)
    readSync(fd, buf, 0, len, state.transcriptOffset)
    chunk = buf
  } finally {
    closeSync(fd)
  }
  const lastNl = chunk.lastIndexOf(0x0a)
  if (lastNl < 0) return 0 // no complete line yet
  state.transcriptOffset += lastNl + 1

  let newSteps = 0
  for (const line of chunk.subarray(0, lastNl).toString('utf8').split('\n')) {
    if (!line.trim()) continue
    let entry
    try {
      entry = JSON.parse(line)
    } catch {
      continue
    }
    if (entry?.type !== 'assistant' || entry.isSidechain) continue
    const msg = entry.message
    if (!msg || typeof msg !== 'object') continue
    const id = msg.id ?? entry.uuid ?? null
    if (id !== state.lastMessageId) {
      state.lastMessageId = id
      state.steps++
      newSteps++
      state.lastAssistantText = ''
    }
    const u = msg.usage
    if (u && typeof u === 'object') {
      state.lastContextTokens =
        (Number(u.input_tokens) || 0) +
        (Number(u.cache_read_input_tokens) || 0) +
        (Number(u.cache_creation_input_tokens) || 0)
    }
    if (Array.isArray(msg.content)) {
      for (const block of msg.content) {
        if (block?.type === 'text' && typeof block.text === 'string') {
          state.lastAssistantText = (state.lastAssistantText ? state.lastAssistantText + '\n' : '') + block.text
        }
      }
    }
  }
  return newSteps
}
