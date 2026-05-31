import { Link, Route, Routes } from "react-router-dom";
import "./App.css";

const API_URL = "http://localhost:8000";
const ML_URL = "http://localhost:8001";

function Layout({ children }) {
  return (
    <div className="app">
      <aside className="sidebar">
        <h2>AgileIQ</h2>
        <p>Gestion agile intelligente</p>
        <nav>
          <Link to="/">Tableau de bord</Link>
          <Link to="/projects">Projets</Link>
          <Link to="/tickets">Tickets</Link>
          <Link to="/ai">Modules IA</Link>
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  );
}

function Dashboard() {
  return (
    <Layout>
      <h1>Tableau de bord</h1>

      <div className="cards stats">
        <div className="card">
          <span className="label">API</span>
          <h3>Opérationnelle</h3>
          <p>Flask, JWT, PostgreSQL</p>
        </div>
        <div className="card">
          <span className="label">Swagger</span>
          <h3>OpenAPI 3.0</h3>
          <p>Documentation interactive</p>
        </div>
        <div className="card">
          <span className="label">IA</span>
          <h3>4 modules</h3>
          <p>Classification, priorité, clustering, prédiction</p>
        </div>
      </div>

      <div className="actions">
        <a href={`${API_URL}/docs`} target="_blank">Ouvrir Swagger</a>
        <a href={`${ML_URL}/ui/models`} target="_blank">Modèles IA</a>
      </div>
    </Layout>
  );
}

function Projects() {
  const projects = [
    { key: "AGILEIQ", name: "AgileIQ Platform", description: "Plateforme de gestion agile intelligente" },
    { key: "PFE", name: "Projet de fin d’études", description: "Suivi du développement et des livrables" },
  ];

  return (
    <Layout>
      <h1>Gestion des projets</h1>
      <p className="subtitle">Vue démonstrative des projets suivis par AgileIQ.</p>

      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Clé</th>
              <th>Nom</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((p) => (
              <tr key={p.key}>
                <td><strong>{p.key}</strong></td>
                <td>{p.name}</td>
                <td>{p.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="actions">
        <a href={`${API_URL}/docs`} target="_blank">Tester le CRUD projets</a>
      </div>
    </Layout>
  );
}

function Tickets() {
  const tickets = [
    { title: "Crash au login Firefox", type: "bug", severity: "major" },
    { title: "Ajouter export CSV", type: "feature", severity: "-" },
    { title: "Refonte du module de paiement", type: "epic", severity: "-" },
  ];

  return (
    <Layout>
      <h1>Gestion des tickets</h1>
      <p className="subtitle">Exemples de tickets utilisés pour démontrer les modules IA.</p>

      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Titre</th>
              <th>Type</th>
              <th>Sévérité</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((t) => (
              <tr key={t.title}>
                <td>{t.title}</td>
                <td><span className={`badge badge-${t.type}`}>{t.type}</span></td>
                <td>{t.severity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="actions">
        <a href={`${API_URL}/docs`} target="_blank">Tester le CRUD tickets</a>
      </div>
    </Layout>
  );
}

function AI() {
  return (
    <Layout>
      <h1>Modules d’intelligence artificielle</h1>
      <p className="subtitle">Accès rapide aux démonstrations du service IA AgileIQ.</p>

      <div className="cards">
        <a className="card" href={`${ML_URL}/evaluation/confusion_matrix.png`} target="_blank">
          <span className="label">Module 1</span>
          <h3>Classification automatique</h3>
          <p>Matrice de confusion, F1-score et prédiction du type de ticket.</p>
        </a>

        <a className="card" href={`${ML_URL}/ui/suggestions`} target="_blank">
          <span className="label">Module 2</span>
          <h3>Validation human-in-the-loop</h3>
          <p>Interface permettant d’accepter, modifier ou rejeter une suggestion IA.</p>
        </a>

        <a className="card" href={`${ML_URL}/visualization/clusters.png`} target="_blank">
          <span className="label">Module 3</span>
          <h3>Détection de bugs récurrents</h3>
          <p>Visualisation des groupes de bugs similaires.</p>
        </a>

        <a className="card" href={`${ML_URL}/ui/predictions`} target="_blank">
          <span className="label">Module 4</span>
          <h3>Analyse prédictive</h3>
          <p>Estimation des durées et identification des tickets à risque.</p>
        </a>
      </div>
    </Layout>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/projects" element={<Projects />} />
      <Route path="/tickets" element={<Tickets />} />
      <Route path="/ai" element={<AI />} />
    </Routes>
  );
}
