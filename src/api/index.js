const BASE = '/api'
async function req(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body) opts.body = JSON.stringify(body)
  const r = await fetch(BASE + path, opts)
  const d = await r.json()
  if (!r.ok) throw new Error(d.error || `HTTP ${r.status}`)
  return d
}

export const api = {
  login: (u, p) => req('POST', '/auth/login', { username: u, password: p }),
  register: (u, p) => req('POST', '/auth/register', { username: u, password: p }),

  addGrade: (d) => req('POST', '/records/grade', d),
  addPractice: (d) => req('POST', '/records/practice', d),
  addNote: (d) => req('POST', '/records/note', d),
  addMistake: (d) => req('POST', '/records/mistake', d),
  getRecords: (userId) => req('GET', `/records?user_id=${userId}`),
  deleteRecord: (type, id, userId) => req('DELETE', `/records/${type}/${id}?user_id=${userId}`),

  getStats: (userId) => req('GET', `/stats?user_id=${userId}`),
  getReport: (userId) => req('GET', `/stats/report?user_id=${userId}`),

  chat: (msg, history) => req('POST', '/chat', { message: msg, history }),
}
