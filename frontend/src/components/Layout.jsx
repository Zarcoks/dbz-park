/**
 * Le gabarit commun à toutes les pages : l'en-tête, puis la page elle-même.
 *
 * C'est l'équivalent du `{% extends "park_management/index.html" %}` de Django.
 * `<Outlet />` est l'endroit où React Router pose la page de la route courante
 * — le `{% block content %}` du gabarit.
 */
import { Outlet } from 'react-router-dom'

import Header from './Header'

export default function Layout() {
  return (
    <>
      <Header />
      <main>
        <Outlet />
      </main>
    </>
  )
}
