// 任务列表页：列表 + 状态筛选 + 新增/编辑弹窗 + 删除确认。状态仅用 useState/useEffect。
import { useCallback, useEffect, useState } from 'react'
import {
  Button,
  Card,
  Form,
  Input,
  Modal,
  Select,
  Space,
  Table,
  Tag,
  App,
} from 'antd'
import { useNavigate } from 'react-router-dom'
import { listTasks, createTask, updateTask, deleteTask } from '../api/task'
import { removeToken } from '../utils/auth'

const STATUS_OPTIONS = [
  { value: 'todo', label: '待办' },
  { value: 'doing', label: '进行中' },
  { value: 'done', label: '已完成' },
]

const STATUS_TAG_COLOR = { todo: 'default', doing: 'processing', done: 'success' }
const STATUS_LABEL = Object.fromEntries(STATUS_OPTIONS.map((o) => [o.value, o.label]))

export default function TaskList() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)
  const [statusFilter, setStatusFilter] = useState(undefined)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null) // null 表示新增
  const [form] = Form.useForm()

  const navigate = useNavigate()
  const { message, modal } = App.useApp()

  // 拉取列表；status 为空则不传筛选参数
  const fetchTasks = useCallback(async (status) => {
    setLoading(true)
    try {
      const data = await listTasks(status ? { status } : {})
      setTasks(data)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchTasks(statusFilter)
  }, [statusFilter, fetchTasks])

  // 打开新增弹窗
  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setModalOpen(true)
  }

  // 打开编辑弹窗并回填数据
  const openEdit = (record) => {
    setEditing(record)
    form.setFieldsValue(record)
    setModalOpen(true)
  }

  // 弹窗提交：新增或编辑
  const handleSubmit = async () => {
    const values = await form.validateFields()
    if (editing) {
      await updateTask(editing.id, values)
      message.success('更新成功')
    } else {
      await createTask(values)
      message.success('创建成功')
    }
    setModalOpen(false)
    form.resetFields()
    fetchTasks(statusFilter)
  }

  // 删除二次确认
  const handleDelete = (record) => {
    modal.confirm({
      title: '确认删除',
      content: `确定删除任务「${record.title}」吗？`,
      okText: '删除',
      okButtonProps: { danger: true },
      onOk: async () => {
        await deleteTask(record.id)
        message.success('删除成功')
        fetchTasks(statusFilter)
      },
    })
  }

  const handleLogout = () => {
    removeToken()
    navigate('/login')
  }

  const columns = [
    { title: '标题', dataIndex: 'title', key: 'title' },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text) => text || '—',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => <Tag color={STATUS_TAG_COLOR[status]}>{STATUS_LABEL[status]}</Tag>,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button type="link" size="small" onClick={() => openEdit(record)}>
            编辑
          </Button>
          <Button type="link" size="small" danger onClick={() => handleDelete(record)}>
            删除
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div style={{ maxWidth: 960, margin: '24px auto', padding: '0 16px' }}>
      <Card
        title="我的任务"
        extra={
          <Space>
            <Select
              allowClear
              placeholder="按状态筛选"
              style={{ width: 140 }}
              value={statusFilter}
              onChange={(value) => setStatusFilter(value)}
              options={STATUS_OPTIONS}
            />
            <Button type="primary" onClick={openCreate}>
              新增任务
            </Button>
            <Button onClick={handleLogout}>退出登录</Button>
          </Space>
        }
      >
        <Table rowKey="id" columns={columns} dataSource={tasks} loading={loading} />
      </Card>

      {/* 新增 / 编辑共用一个弹窗，不新建路由页面 */}
      <Modal
        title={editing ? '编辑任务' : '新增任务'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        destroyOnClose
      >
        <Form form={form} layout="vertical" initialValues={{ status: 'todo' }}>
          <Form.Item
            label="标题"
            name="title"
            rules={[{ required: true, message: '请输入任务标题' }, { max: 100, message: '标题不超过 100 字' }]}
          >
            <Input placeholder="请输入任务标题" />
          </Form.Item>
          <Form.Item label="描述" name="description" rules={[{ max: 1000, message: '描述不超过 1000 字' }]}>
            <Input.TextArea rows={3} placeholder="可选" />
          </Form.Item>
          <Form.Item label="状态" name="status" rules={[{ required: true, message: '请选择状态' }]}>
            <Select options={STATUS_OPTIONS} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
