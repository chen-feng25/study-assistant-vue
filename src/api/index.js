const BASE = '/api'
async function req(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } }
  if (body) opts.body = JSON.stringify(body)
  let r
  try { r = await fetch(BASE + path, opts) } catch (e) { throw new Error('网络错误，请检查连接') }
  let d
  try { d = await r.json() } catch (e) { throw new Error(`服务器异常 (${r.status})`) }
  if (!r.ok) throw new Error(d.detail || d.error || `请求失败 (${r.status})`)
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

  getGrades: (userId) => req('GET', `/records?user_id=${userId}`).then(d => d.grades || []),
  addCourse: (name, userId) => req('POST', '/courses/add', { name, user_id: userId }),
  getCourses: (userId) => req('GET', `/courses?user_id=${userId}`).then(d => d.courses || []),

  _gids: (ids) => ids?.length ? `&grade_ids=${ids.join(',')}` : '',
  getStats: (userId, gradeIds) => req('GET', `/stats?user_id=${userId}${api._gids(gradeIds)}`),
  getReport: (userId, gradeIds) => req('GET', `/stats/report?user_id=${userId}${api._gids(gradeIds)}`),
  getDiagnosis: (userId, gradeIds) => req('GET', `/stats/diagnosis?user_id=${userId}${api._gids(gradeIds)}`),
  getPlan: (userId, gradeIds) => req('GET', `/stats/plan?user_id=${userId}${api._gids(gradeIds)}`),

  chat: (msg, history, userId) => req('POST', '/chat', { message: msg, history, user_id: userId }),

  getApiKeyStatus: () => req('GET', '/settings/apikey'),
  saveApiKey: (key) => req('POST', '/settings/apikey', { api_key: key }),
}
