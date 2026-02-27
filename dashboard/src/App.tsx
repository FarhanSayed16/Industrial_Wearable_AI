import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ChangePassword from "./pages/ChangePassword";
import LiveView from "./pages/LiveView";
import Sessions from "./pages/Sessions";
import Analytics from "./pages/Analytics";
import WorkerProfile from "./pages/WorkerProfile";
import Settings from "./pages/Settings";
import Privacy from "./pages/Privacy";
import ShiftReplay from "./pages/ShiftReplay";
import LabelingQueue from "./pages/LabelingQueue";
import FloorMap from "./pages/FloorMap";
import "./components/ui/ui.css";
import "./components/charts/charts.css";
import "./App.css";
import { useTheme } from "./hooks/useTheme";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem("access_token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function App() {
  // Initialize theme at root
  useTheme();

  return (
    <>
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: "var(--color-bg-card)",
            color: "var(--color-text)",
            border: "1px solid var(--color-border)",
            borderRadius: "var(--radius-md)",
            boxShadow: "var(--shadow-md)",
          },
          success: {
            iconTheme: { primary: "var(--color-success)", secondary: "var(--color-bg-card)" },
          },
          error: {
            iconTheme: { primary: "var(--color-error)", secondary: "var(--color-bg-card)" },
          },
        }}
      />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<LiveView />} />
            <Route path="map" element={<FloorMap />} />
            <Route path="sessions" element={<Sessions />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="workers/:workerName" element={<WorkerProfile />} />
            <Route path="settings" element={<Settings />} />
            <Route path="privacy" element={<Privacy />} />
            <Route path="labeling" element={<LabelingQueue />} />
            <Route path="settings/password" element={<ChangePassword />} />
            <Route path="replay/:sessionId" element={<ShiftReplay />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;
