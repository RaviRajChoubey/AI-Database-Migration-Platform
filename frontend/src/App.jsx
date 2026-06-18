import "./App.css";

import Header from "./components/Header";
import Dashboard from "./components/Dashboard";
import MigrationForm from "./components/MigrationForm";

import {
  Routes,
  Route
} from "react-router-dom";

function App() {

  return (

    <>
      <Header />

      <Routes>

        <Route
          path="/"
          element={<MigrationForm />}
        />

        <Route
          path="/dashboard"
          element={<Dashboard />}
        />

      </Routes>

    </>

  );

}

export default App;