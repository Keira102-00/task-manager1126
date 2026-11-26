// 登录 / 注册 Tab 页：单页内切换，不新建路由。
import { useState } from 'react'
import { Button, Card, Form, Input, Tabs, App } from 'antd'
import { useNavigate } from 'react-router-dom'
import { login, register } from '../api/auth'
import { setToken } from '../utils/auth'

const rules = {
  username: [
    { required: true, message: '请输入用户名' },
    { min: 3, message: '用户名至少 3 个字符' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码至少 6 位' },
  ],
}

export default function Login() {
  const [activeTab, setActiveTab] = useState('login')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  const { message } = App.useApp()

  // 登录成功：存 token，跳任务页
  const onLogin = async (values) => {
    setSubmitting(true)
    try {
      const data = await login(values)
      setToken(data.access_token)
      message.success('登录成功')
      navigate('/tasks')
    } finally {
      setSubmitting(false)
    }
  }

  // 注册成功：提示后切回登录 Tab（不在前端自动登录）
  const onRegister = async (values) => {
    setSubmitting(true)
    try {
      await register(values)
      message.success('注册成功，请登录')
      setActiveTab('login')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: '80px auto' }}>
      <Card title="任务管理系统">
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'login',
              label: '登录',
              children: (
                <Form layout="vertical" onFinish={onLogin}>
                  <Form.Item label="用户名" name="username" rules={rules.username}>
                    <Input placeholder="请输入用户名" autoComplete="username" />
                  </Form.Item>
                  <Form.Item label="密码" name="password" rules={rules.password}>
                    <Input.Password placeholder="请输入密码" autoComplete="current-password" />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" block loading={submitting}>
                    登录
                  </Button>
                </Form>
              ),
            },
            {
              key: 'register',
              label: '注册',
              children: (
                <Form layout="vertical" onFinish={onRegister}>
                  <Form.Item label="用户名" name="username" rules={rules.username}>
                    <Input placeholder="设置用户名" autoComplete="username" />
                  </Form.Item>
                  <Form.Item label="密码" name="password" rules={rules.password}>
                    <Input.Password placeholder="设置密码（至少 6 位）" autoComplete="new-password" />
                  </Form.Item>
                  <Button type="primary" htmlType="submit" block loading={submitting}>
                    注册
                  </Button>
                </Form>
              ),
            },
          ]}
        />
      </Card>
    </div>
  )
}
