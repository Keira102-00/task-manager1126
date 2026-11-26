import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { App as AntApp } from 'antd'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      {/* AntApp 提供 message/modal 的上下文，避免静态调用告警 */}
      <AntApp>
        <App />
      </AntApp>
    </BrowserRouter>
  </React.StrictMode>,
)
