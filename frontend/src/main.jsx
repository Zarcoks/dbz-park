/**
 * Le point d'entrée : React s'accroche ici à la div `#root` de index.html.
 *
 * Les trois feuilles de style sont chargées dans cet ordre — Bootstrap d'abord,
 * puis les icônes, puis `dbz-park.css` qui pose les couleurs du parc par-dessus.
 */
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import './styles/dbz-park.css'

import App from './App'
import { AuthProvider } from './auth/AuthContext'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
