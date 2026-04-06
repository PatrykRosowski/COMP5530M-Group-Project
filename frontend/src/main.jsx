import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import BusNetworkMap from './BusNetworkMap.jsx'
import EvaluationPage from './EvaluationPage.jsx'
import './index.css'
import App from './App.jsx'

const router = createBrowserRouter([
  {
    path: '/',
    element: <BusNetworkMap />,
  },
  {
    path: '/evaluate',
    element: <EvaluationPage />,
  },
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
      <RouterProvider router={router} />
  </StrictMode>,
)
