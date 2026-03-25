import { useState } from "react";

function App() {
  const [cep, setCep] = useState("");
  const [dados, setDados] = useState(null);

  async function buscar() {
    const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
    const data = await res.json();
    setDados(data);
  }

  return (
    <div class="procurarCEP"
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        flexDirection: "column",
      }}
    >
      <h1>Digite seu CEP:</h1>

      <input onChange={(e) => setCep(e.target.value)} />

      <button onClick={buscar}>Buscar</button>

      {dados && <p class="cidadeCEP">{dados.localidade}</p>}
    </div>
  );
}

export default App;
