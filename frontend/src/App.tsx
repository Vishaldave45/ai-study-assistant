import Card from "./components/Card";
import Heading from "./components/Heading";

function App() {
  return (
    <main style={{padding:"40px"}}>
      <Card>
         <Heading title="📚 AI Study Assistant" />

      <p>Building from scratch 🚀</p>
      </Card>

       <Card>
         <Heading title="Dashboard" />

        <p>See your uploaded documents.</p>
      </Card>
      
     
    </main>
  );
}

export default App;

