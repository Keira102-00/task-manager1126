// 路由定义 + 登录守卫。状态仅用 useState/useEffect，不引入 Redux/Zustand。
import { Navigate, Route, Routes } from 'react-router-dom'
import Login from './pages/Login'
import TaskList from './pages/TaskList'
import { getToken } from './utils/auth'

// 路由守卫：无 token 强制回登录页
function RequireAuth({ children }) {
  return getToken() ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/tasks"
        element={
          <RequireAuth>
            <TaskList />
          </RequireAuth>
        }
      />
      {/* 其他路径统一重定向到任务页 */}
      <Route path="*" element={<Navigate to="/tasks" replace />} />
    </Routes>
  )
}
