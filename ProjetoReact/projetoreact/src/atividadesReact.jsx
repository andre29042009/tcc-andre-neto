function App() {

   let x = 5;
   let y = 10;
 
   let soma = x + y;
   let multiplicacao = x * y;
   let divisao = x / y;
   let cores = ["amarelo", "laranja"];
 

   let pessoas = [
     { id: 1, nome: "Joãozinho", idade: 12 },
     { id: 2, nome: "Maria", idade: 14 }
   ];
 
 
   return (
     <div>
       {multiplicacao > divisao && <p>{multiplicacao} é maior que {divisao}</p>}
       {multiplicacao == divisao && <p>Multiplicação e divisão são iguais</p>}
       {soma > 10 && <p>Isso é mais que uma dezena.</p>}
       <p>O número {x} é menor que {soma}</p>
 
       {pessoas.map((pessoa) => (
         <p key={pessoa.id}>
           {pessoa.nome} tem {pessoa.idade} anos
         </p>
       ))}
     </div>
   );
 }
 
 export default App;