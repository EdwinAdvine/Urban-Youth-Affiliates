import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { authApi } from '@/api/auth'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    tiktok_url: '',
    instagram_url: '',
    terms_accepted: false
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.terms_accepted) {
      toast.error('You must accept the terms')
      return
    }
    setLoading(true)
    try {
      const res = await authApi.register(form)
      toast.success(res.data.message || 'Registration successful!')
      if (!res.data.requires_approval) {
        navigate('/affiliate/dashboard')
      } else {
        navigate('/login')
      }
    } catch (err: any) {
      toast.error(err.response?.data?.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-yu-black flex
