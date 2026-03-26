import { useState } from "react";

function App() {
  const [cep, setCep] = useState("");
  const [dados, setDados] = useState(null);

  async function buscar() {
  const cepLimpo = cep.replace(/\D/g, "")

  const res = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`)
  const data = await res.json()

  setDados(data)
}

  return (
    <div 
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

      {dados && <p className="cidadeCEP">{dados.localidade}</p>}
    </div>
  );
}

export default App;
