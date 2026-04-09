import React from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";

function App() {
  const [metrics, setMetrics] = React.useState(null);

  React.useEffect(() => {
    axios
      .get("http://localhost:8000/api/v1/dashboard/admin")
      .then((res) => setMetrics(res.data))
      .catch(() => setMetrics({ error: "Backend unavailable" }));
  }, []);

  return (
    <main style={{ fontFamily: "Inter, sans-serif", margin: "2rem" }}>
      <h1>SocietyMan Admin Dashboard</h1>
      <p>Live KPIs for collections, dues, operations and support tickets.</p>
      <pre style={{ background: "#f5f5f5", padding: 12, borderRadius: 8 }}>
        {JSON.stringify(metrics, null, 2)}
      </pre>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
